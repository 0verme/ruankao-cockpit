"""Translate scheduled task results into Progress and Review domain inputs.

A PlannerOutput remains a projection. This adapter never records completion,
planned duration, or an inferred success; callers must supply the actual
comprehensive attempt and its explicit event identity.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Iterable, Mapping

from engine.progress.model import EVENT_SCHEMA_VERSION
from engine.review.model import (
    ITEM_SCHEMA_VERSION,
    REVIEW_EVENT_SCHEMA_VERSION,
    ReviewValidationError,
    validate_review_items,
)


class TaskResultError(ValueError):
    """A scheduled task result cannot safely become domain facts."""

    def __init__(self, message: str, category: str) -> None:
        self.category = category
        super().__init__(message)


def _fail(message: str, category: str) -> None:
    raise TaskResultError(message, category)


def _scheduled_task(planner_output: Mapping[str, Any], task_id: str) -> Mapping[str, Any]:
    days = planner_output.get("days")
    if not isinstance(days, list) or not days or not isinstance(days[0], Mapping):
        _fail("planner_output.days[0] is required", "invalid_planner_output")

    today_tasks = days[0].get("tasks")
    if not isinstance(today_tasks, list):
        _fail("planner_output.days[0].tasks must be a list", "invalid_planner_output")
    matches = [task for task in today_tasks if isinstance(task, Mapping) and task.get("task_id") == task_id]
    if len(matches) > 1:
        _fail(f"task_id {task_id!r} is ambiguous in today's plan", "invalid_planner_output")
    if matches:
        return matches[0]

    later_tasks = [
        task
        for day in days[1:]
        if isinstance(day, Mapping) and isinstance(day.get("tasks"), list)
        for task in day["tasks"]
        if isinstance(task, Mapping) and task.get("task_id") == task_id
    ]
    today_demands = days[0].get("unmet_demand", [])
    demand_matches = (
        isinstance(today_demands, list)
        and any(
            isinstance(demand, Mapping) and demand.get("demand_id") == task_id
            for demand in today_demands
        )
    )
    if later_tasks or demand_matches:
        _fail(f"task_id {task_id!r} is not scheduled for today", "task_not_scheduled")
    _fail(f"task_id {task_id!r} is not present in this plan", "unknown_task")
    raise AssertionError("unreachable")


def _require_attempt(result: Any) -> tuple[Mapping[str, Any], str | None]:
    if not isinstance(result, Mapping):
        _fail("result must contain an explicit progress_event", "unsupported_result_type")
    progress_event = result.get("progress_event")
    if not isinstance(progress_event, Mapping):
        _fail("result.progress_event must be an event object", "unsupported_result_type")
    if progress_event.get("event_type") != "comprehensive_attempt":
        _fail(
            "task execution requires an objective comprehensive_attempt fact",
            "unsupported_result_type",
        )
    if type(progress_event.get("correct")) is not bool:
        _fail("comprehensive_attempt.correct must be supplied as a boolean fact", "unsupported_result_type")
    if not isinstance(progress_event.get("event_id"), str) or not progress_event["event_id"].strip():
        _fail("progress_event.event_id must be supplied explicitly", "invalid_progress_event")
    if not isinstance(progress_event.get("occurred_at"), str) or not progress_event["occurred_at"].strip():
        _fail("progress_event.occurred_at must be supplied explicitly", "invalid_progress_event")

    context_id = result.get("review_context_event_id")
    if context_id is not None and (not isinstance(context_id, str) or not context_id.strip()):
        _fail("review_context_event_id must be a non-empty explicit identity", "invalid_review_event")
    return progress_event, context_id


def build_topic_review_item_from_attempt(
    progress_event: Mapping[str, Any],
    topic_id: str,
    taxonomy: Mapping[str, Any],
    capabilities: Mapping[str, Any],
) -> dict[str, Any]:
    """Build and validate a stable topic item from a real attempt's provenance."""
    if not isinstance(progress_event, Mapping) or progress_event.get("event_type") != "comprehensive_attempt":
        _fail("topic Review Item requires a comprehensive_attempt", "unsupported_result_type")
    if not isinstance(progress_event.get("topics"), list) or topic_id not in progress_event["topics"]:
        _fail(f"attempt topics must contain {topic_id!r}", "target_mismatch")
    if not isinstance(taxonomy, Mapping) or not isinstance(capabilities, Mapping):
        _fail("taxonomy and capabilities documents are required", "invalid_catalog")

    question = progress_event.get("question")
    if not isinstance(question, Mapping):
        _fail("attempt.question must contain real question provenance", "missing_source_reference")

    source_reference = {
        key: question[key]
        for key in (
            "source_id",
            "source_commit",
            "source_path",
            "source_question_id",
            "golden_set_record_id",
        )
        if key in question
    }
    item = {
        "schema_version": ITEM_SCHEMA_VERSION,
        "review_item_id": f"review/topic/{topic_id}",
        "item_kind": "topic",
        "canonical_ref": {
            "topic_id": topic_id,
            "taxonomy_version": taxonomy.get("taxonomy_version"),
        },
        "source_reference": source_reference,
    }
    try:
        validate_review_items([item], taxonomy, capabilities)
    except ReviewValidationError as exc:
        _fail(str(exc), exc.category)
    return item


def _topic_from_review_target(target_ref: Any) -> str:
    if not isinstance(target_ref, str):
        _fail("review target_ref must be a string", "target_mismatch")
    parts = target_ref.split("/")
    if len(parts) == 3 and parts[0] == "review" and parts[1] == "topic" and parts[2]:
        return parts[2]
    if target_ref.startswith(("review/question/", "review/case_capability/")):
        _fail(
            f"review target category in {target_ref!r} is not supported by this adapter",
            "unsupported_execution_target",
        )
    _fail(f"unsupported or malformed review target {target_ref!r}", "target_mismatch")
    raise AssertionError("unreachable")


def record_task_result(
    planner_output: Mapping[str, Any],
    task_id: str,
    result: Mapping[str, Any],
    *,
    taxonomy: Mapping[str, Any] | None = None,
    capabilities: Mapping[str, Any] | None = None,
    existing_review_items: Iterable[Mapping[str, Any]] | None = None,
) -> dict[str, list[Mapping[str, Any]]]:
    """Return appendable Progress, Review Context, and new Item facts.

    A new-learning attempt requires the current taxonomy, capability catalog,
    and Review Item catalog. The adapter validates those inputs, fails closed
    when the stable topic item already exists, and derives its source reference
    only from the real attempt's question provenance.
    """
    if not isinstance(planner_output, Mapping):
        _fail("planner_output must be an object", "invalid_planner_output")
    if not isinstance(task_id, str) or not task_id.strip():
        _fail("task_id must be a non-empty string", "unknown_task")

    task = _scheduled_task(planner_output, task_id)
    task_type = task.get("task_type")
    target_kind = task.get("target_kind")
    target_ref = task.get("target_ref")

    if task_type == "new_learning":
        if target_kind != "topic" or not isinstance(target_ref, str) or not target_ref:
            _fail("new_learning must target a topic", "target_mismatch")
        expected_topic = target_ref
        attempt_context = "initial_learning"
        registers_item = True
    elif task_type == "review":
        if target_kind != "review_item":
            _fail("review must target a review_item", "target_mismatch")
        expected_topic = _topic_from_review_target(target_ref)
        attempt_context = "review"
        registers_item = False
    else:
        _fail(f"task type {task_type!r} is not supported for execution", "unsupported_execution_target")

    progress_event, context_id = _require_attempt(result)
    if result.keys() != {"progress_event", "review_context_event_id"}:
        _fail(
            "result fields must include only progress_event and review_context_event_id",
            "unsupported_result_type",
        )
    if context_id is None:
        _fail("execution requires an explicit review_context_event_id", "invalid_review_event")

    if not isinstance(progress_event.get("topics"), list) or expected_topic not in progress_event["topics"]:
        _fail(
            f"attempt topics must contain planned topic {expected_topic!r}",
            "target_mismatch",
        )

    event = deepcopy(dict(progress_event))
    review_contexts: list[Mapping[str, Any]] = []
    review_items: list[Mapping[str, Any]] = []
    if registers_item:
        if taxonomy is None or capabilities is None or existing_review_items is None:
            _fail(
                "new_learning requires taxonomy, capabilities, and existing_review_items",
                "invalid_catalog",
            )
        try:
            existing_catalog = validate_review_items(existing_review_items, taxonomy, capabilities)
        except ReviewValidationError as exc:
            _fail(str(exc), exc.category)
        review_item_id = f"review/topic/{expected_topic}"
        if existing_catalog.get(review_item_id) is not None:
            _fail(
                f"new_learning cannot register existing review item {review_item_id!r}",
                "duplicate_review_item",
            )
        review_items.append(
            build_topic_review_item_from_attempt(event, expected_topic, taxonomy, capabilities)
        )
        context_item_id = review_item_id
    else:
        context_item_id = target_ref

    review_contexts.append({
        "schema_version": REVIEW_EVENT_SCHEMA_VERSION,
        "event_id": context_id,
        "event_type": "review_context",
        "source_event_id": event["event_id"],
        "review_item_id": context_item_id,
        "attempt_context": attempt_context,
        "occurred_at": event["occurred_at"],
    })

    # Keep the Progress schema version explicit; full fact validation remains
    # owned by Progress replay and Review validation/replay.
    if event.get("schema_version") != EVENT_SCHEMA_VERSION:
        _fail(
            f"progress_event.schema_version must be {EVENT_SCHEMA_VERSION!r}",
            "invalid_progress_event",
        )

    return {
        "progress_events": [event],
        "review_events": review_contexts,
        "review_items": review_items,
    }
