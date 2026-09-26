"""Deterministic MVP Today Plan generation.

The engine consumes validated ProgressState and MasteryReviewState projections;
only ``days[0]`` is actively planned. The remaining required PlannerOutput days
are empty contract placeholders, not a Rolling 7-Day scheduling policy.
"""
from __future__ import annotations

from datetime import date, timedelta
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from engine.rules.review_policy_v01 import resolve_timezone
from scripts.validate_planner_contract import (
    PLANNER_OUTPUT_HORIZON_DAYS,
    PLANNER_OUTPUT_HORIZON_UNIT,
    PlannerContractError,
    _canonical_instant,
    _parse_instant,
    validate_planner_output,
    validate_snapshot,
)

PLAN_POLICY_ID = "planner-policy/minimal-today"
PLAN_POLICY_VERSION = "v0.1"
MVP_REVIEW_MINUTES = 15
MVP_NEW_LEARNING_MINUTES = 25


def _stable_id(prefix: str, identity: tuple[str, ...]) -> str:
    payload = json.dumps(identity, ensure_ascii=False, separators=(",", ":"))
    return f"{prefix}-{hashlib.sha256(payload.encode('utf-8')).hexdigest()}"


def _pointer_escape(value: str) -> str:
    return value.replace("~", "~0").replace("/", "~1")


def _task_id(local_date: str, task_type: str, target_kind: str, target_ref: str) -> str:
    return _stable_id(
        "task",
        (PLAN_POLICY_ID, PLAN_POLICY_VERSION, local_date, task_type, target_kind, target_ref),
    )


def _demand_id(local_date: str, demand_type: str, target_kind: str, target_ref: str) -> str:
    return _stable_id(
        "demand",
        (PLAN_POLICY_ID, PLAN_POLICY_VERSION, local_date, demand_type, target_kind, target_ref),
    )


def _trace(
    *,
    subject_kind: str,
    subject_id: str,
    decision_category: str,
    reason_code: str,
    target_kind: str,
    target_ref: str,
    input_references: list[str],
    structured_inputs: Mapping[str, Any],
    display_message: str,
) -> dict[str, Any]:
    trace_id = _stable_id(
        "trace",
        (PLAN_POLICY_ID, PLAN_POLICY_VERSION, subject_kind, subject_id, decision_category),
    )
    return {
        "trace_id": trace_id,
        "subject_kind": subject_kind,
        "subject_id": subject_id,
        "decision_category": decision_category,
        "reason_code": reason_code,
        "planner_policy": {"policy_id": PLAN_POLICY_ID, "policy_version": PLAN_POLICY_VERSION},
        "input_references": input_references,
        "target_kind": target_kind,
        "target_ref": target_ref,
        "structured_inputs": dict(structured_inputs),
        "display_message": display_message,
    }


def _review_evidence_topic_ids(
    progress_state: Mapping[str, Any],
    review_state: Mapping[str, Any],
) -> set[str]:
    """Return topics with positive attempt or supported item-level evidence.

    Attempts count regardless of correctness: low accuracy is not absence of
    learning. Review scheduling/mastery state also prevents reclassifying an
    already scheduled topic as new. Aggregate coverage is deliberately not used
    because it cannot identify individual topics.
    """
    evidenced = {
        topic_id
        for topic_id, metric in progress_state["topics"].items()
        if any(metric[key] > 0 for key in ("attempt_count", "correct_count", "incorrect_count"))
    }
    for item in review_state["items"].values():
        if item["item_kind"] != "topic":
            continue
        topic_id = item["canonical_ref"]["topic_id"]
        has_supported_evidence = any(
            record["evidence_status"] == "supported" for record in item["evidence"]
        )
        has_existing_schedule_or_learning = (
            item["mastery_state"] != "new" or item["review_status"] != "not_scheduled"
        )
        if has_supported_evidence or has_existing_schedule_or_learning:
            evidenced.add(topic_id)
    return evidenced


def _next_unlearned_topic(snapshot: Mapping[str, Any]) -> str | None:
    inputs = snapshot["inputs"]
    evidenced = _review_evidence_topic_ids(inputs["progress_state"], inputs["mastery_review_state"])
    # L3 IDs have the smallest taxonomy granularity in v0.1 and form directly
    # actionable learning targets. Canonical ID order is the entire MVP order.
    candidates = sorted(
        topic_id
        for topic_id in inputs["taxonomy"]["topic_ids"]
        if topic_id.count(".") == 2 and topic_id not in evidenced
    )
    return candidates[0] if candidates else None


def _due_reviews(review_state: Mapping[str, Any]) -> list[tuple[str, Mapping[str, Any]]]:
    pending: list[tuple[str, Mapping[str, Any]]] = []
    for review_item_id, item in review_state["items"].items():
        status = item["review_status"]
        if status not in {"overdue", "due"}:
            continue
        due_at = item.get("next_due_at")
        if not isinstance(due_at, str) or not due_at:
            raise PlannerContractError(
                f"{review_item_id}: due review has no next_due_at",
                "invalid_domain_state",
            )
        pending.append((review_item_id, item))
    return sorted(
        pending,
        key=lambda row: (
            0 if row[1]["review_status"] == "overdue" else 1,
            _parse_instant(row[1]["next_due_at"], f"{row[0]}.next_due_at"),
            row[0],
        ),
    )


def _empty_day(day_offset: int, local_date: date, study_days: set[int], capacity: int) -> dict[str, Any]:
    study_day = local_date.isoweekday() in study_days
    day_capacity = capacity if study_day else 0
    return {
        "day_offset": day_offset,
        "local_date": local_date.isoformat(),
        "study_day": study_day,
        "capacity_minutes": day_capacity,
        "planned_minutes": 0,
        "remaining_minutes": day_capacity,
        "tasks": [],
        "unmet_demand": [],
    }


def plan_today(
    planner_input: Mapping[str, Any],
    as_of: str,
    *,
    root: Path | None = None,
) -> dict[str, Any]:
    """Generate a validated PlannerOutput using an explicit ``as_of`` instant.

    ``planner_input.as_of`` and the explicit argument must denote the same
    instant. The function has no wall-clock, random, machine-timezone or AI
    dependency; identical validated inputs and instant yield identical output.
    """
    contract_root = Path(root) if root is not None else Path(__file__).resolve().parents[2]
    snapshot = validate_snapshot(planner_input, contract_root)
    explicit_instant = _parse_instant(as_of, "plan_today.as_of")
    if explicit_instant != _parse_instant(snapshot["as_of"], "PlannerInput.as_of"):
        raise PlannerContractError(
            "explicit as_of must match PlannerInput.as_of as an instant",
            "inconsistent_input",
        )
    canonical_as_of = _canonical_instant(as_of)
    timezone_name = snapshot["timezone"]
    local_zone = resolve_timezone(timezone_name)
    local_date = explicit_instant.astimezone(local_zone).date()

    inputs = snapshot["inputs"]
    configuration = inputs["user_configuration"]
    capacity = configuration["daily_available_minutes"]
    study_days = set(configuration["study_days"])
    output: dict[str, Any] = {
        "schema_version": "planner-output/v0.1",
        "planner_policy": {"policy_id": PLAN_POLICY_ID, "policy_version": PLAN_POLICY_VERSION},
        "input_snapshot_schema_version": snapshot["schema_version"],
        "as_of": canonical_as_of,
        "timezone": timezone_name,
        "generated_for_local_date": local_date.isoformat(),
        "horizon": {"unit": PLANNER_OUTPUT_HORIZON_UNIT, "day_count": PLANNER_OUTPUT_HORIZON_DAYS},
        "days": [
            _empty_day(offset, local_date + timedelta(days=offset), study_days, capacity)
            for offset in range(PLANNER_OUTPUT_HORIZON_DAYS)
        ],
        "explain_traces": [],
    }
    today = output["days"][0]
    remaining = today["capacity_minutes"]
    review_state = inputs["mastery_review_state"]
    due_reviews = _due_reviews(review_state)

    def add_demand(
        *,
        demand_type: str,
        target_kind: str,
        target_ref: str,
        minutes: int,
        reason_code: str,
        input_references: list[str],
        structured_inputs: Mapping[str, Any],
        display_message: str,
    ) -> None:
        demand_id = _demand_id(local_date.isoformat(), demand_type, target_kind, target_ref)
        trace = _trace(
            subject_kind="unmet_demand",
            subject_id=demand_id,
            decision_category="demand_unmet",
            reason_code=reason_code,
            target_kind=target_kind,
            target_ref=target_ref,
            input_references=input_references,
            structured_inputs=structured_inputs,
            display_message=display_message,
        )
        today["unmet_demand"].append({
            "demand_id": demand_id,
            "demand_type": demand_type,
            "target_kind": target_kind,
            "target_ref": target_ref,
            "requested_minutes": minutes,
            "explain_trace_id": trace["trace_id"],
        })
        output["explain_traces"].append(trace)

    for review_item_id, item in due_reviews:
        target_ref = review_item_id
        status = item["review_status"]
        reason_code = "overdue_review" if status == "overdue" else "due_today_review"
        escaped = _pointer_escape(review_item_id)
        item_pointer = f"/inputs/mastery_review_state/items/{escaped}"
        common_inputs = {
            "review_status": status,
            "next_due_at": item["next_due_at"],
            "planned_minutes": MVP_REVIEW_MINUTES,
            "capacity_minutes": today["capacity_minutes"],
        }
        if remaining >= MVP_REVIEW_MINUTES:
            task_id = _task_id(local_date.isoformat(), "review", "review_item", target_ref)
            trace = _trace(
                subject_kind="plan_task",
                subject_id=task_id,
                decision_category="task_scheduled",
                reason_code=reason_code,
                target_kind="review_item",
                target_ref=target_ref,
                input_references=[
                    f"{item_pointer}/review_status",
                    f"{item_pointer}/next_due_at",
                ],
                structured_inputs=common_inputs,
                display_message="复习已逾期内容" if status == "overdue" else "复习今日到期内容",
            )
            today["tasks"].append({
                "task_id": task_id,
                "task_type": "review",
                "target_kind": "review_item",
                "target_ref": target_ref,
                "planned_minutes": MVP_REVIEW_MINUTES,
                "explain_trace_id": trace["trace_id"],
            })
            output["explain_traces"].append(trace)
            remaining -= MVP_REVIEW_MINUTES
        else:
            add_demand(
                demand_type="review",
                target_kind="review_item",
                target_ref=target_ref,
                minutes=MVP_REVIEW_MINUTES,
                reason_code="capacity_limited_overdue_review" if status == "overdue" else "capacity_limited_due_review",
                input_references=[
                    f"{item_pointer}/review_status",
                    f"/inputs/user_configuration/daily_available_minutes",
                ],
                structured_inputs=common_inputs,
                display_message="复习已到期，但剩余容量不足；保留为未满足需求",
            )

    # Rest days / zero-capacity days have no new-learning demand. Eligible
    # reviews above remain visible as unmet debt when they cannot fit.
    new_topic_id = _next_unlearned_topic(snapshot) if today["capacity_minutes"] > 0 else None
    if new_topic_id is not None:
        target_kind = "topic"
        reason = {
            "selection_rule": "unlearned_l3_topics_by_canonical_id",
            "evidence_basis": "no_progress_attempt_or_supported_topic_review_evidence",
            "planned_minutes": MVP_NEW_LEARNING_MINUTES,
            "capacity_minutes": today["capacity_minutes"],
        }
        topic_attempt_pointer = f"/inputs/progress_state/topics/{_pointer_escape(new_topic_id)}/attempt_count"
        references = ["/inputs/taxonomy/topic_ids", topic_attempt_pointer]
        if remaining >= MVP_NEW_LEARNING_MINUTES:
            task_id = _task_id(local_date.isoformat(), "new_learning", target_kind, new_topic_id)
            trace = _trace(
                subject_kind="plan_task",
                subject_id=task_id,
                decision_category="task_scheduled",
                reason_code="next_unlearned_topic",
                target_kind=target_kind,
                target_ref=new_topic_id,
                input_references=references,
                structured_inputs=reason,
                display_message="按 stable topic ID 顺序安排下一个无有效学习证据的知识点",
            )
            today["tasks"].append({
                "task_id": task_id,
                "task_type": "new_learning",
                "target_kind": target_kind,
                "target_ref": new_topic_id,
                "planned_minutes": MVP_NEW_LEARNING_MINUTES,
                "explain_trace_id": trace["trace_id"],
            })
            output["explain_traces"].append(trace)
            remaining -= MVP_NEW_LEARNING_MINUTES
        else:
            add_demand(
                demand_type="new_learning",
                target_kind=target_kind,
                target_ref=new_topic_id,
                minutes=MVP_NEW_LEARNING_MINUTES,
                reason_code="capacity_limited_new_learning",
                input_references=references + ["/inputs/user_configuration/daily_available_minutes"],
                structured_inputs=reason,
                display_message="下一个未学习知识点未能放入今日容量；保留为未满足需求",
            )

    today["planned_minutes"] = sum(task["planned_minutes"] for task in today["tasks"])
    today["remaining_minutes"] = today["capacity_minutes"] - today["planned_minutes"]
    if remaining != today["remaining_minutes"]:  # pragma: no cover - internal invariant
        raise AssertionError("task allocation minutes do not balance")

    return validate_planner_output(output, snapshot, contract_root)


__all__ = [
    "MVP_NEW_LEARNING_MINUTES",
    "MVP_REVIEW_MINUTES",
    "PLAN_POLICY_ID",
    "PLAN_POLICY_VERSION",
    "plan_today",
]
