"""Deterministic replay for ``MasteryReviewState v0.1``.

The replay composes the frozen layers without promoting a derived state to a
fact source:

``progress events + explicit review context -> Review Evidence -> policy``

Only the unambiguous comprehensive correctness fact is mapped to a policy
success/failure outcome.  Score evidence is retained and explicitly mapped to
``insufficient`` until a versioned score rubric exists; it is never guessed to
be a success or failure.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Iterable, Mapping
from zoneinfo import ZoneInfo

from engine.progress import replay as progress_replay
from engine.progress.model import (
    EVENT_SCHEMA_VERSION,
    REPLAY_RULE_VERSION,
    ProgressValidationError,
)
from engine.rules import (
    MASTERY_POLICY_ID,
    MASTERY_POLICY_VERSION,
    PROJECTION_SCHEMA_VERSION,
    REVIEW_POLICY_ID,
    REVIEW_POLICY_VERSION,
    PolicyEvidence,
    ReviewPolicyError,
    derive_projection,
    parse_instant,
    policy_identity,
    resolve_timezone,
)

from .model import (
    EVIDENCE_SCHEMA_VERSION,
    REVIEW_EVENT_SCHEMA_VERSION,
    REVIEW_MODEL_VERSION,
    ReviewItemCatalog,
    ReviewValidationError,
    project_review_evidence,
    validate_review_items,
)


MASTERY_REVIEW_STATE_SCHEMA_VERSION = "mastery-review-state/v0.1"
# Backward-compatible spelling for the initial P4.5 implementation.
MASTER_REVIEW_STATE_SCHEMA_VERSION = MASTERY_REVIEW_STATE_SCHEMA_VERSION
MASTERY_POLICY_FULL_VERSION = f"{MASTERY_POLICY_ID}/{MASTERY_POLICY_VERSION}"
REVIEW_POLICY_FULL_VERSION = f"{REVIEW_POLICY_ID}/{REVIEW_POLICY_VERSION}"

OUTCOME_ADAPTER_ID = "review-outcome/raw-facts"
OUTCOME_ADAPTER_VERSION = "v0.1"
OUTCOME_ADAPTER_FULL_VERSION = f"{OUTCOME_ADAPTER_ID}/{OUTCOME_ADAPTER_VERSION}"

_SUPPORTED_POLICY_SPECS = {
    "mastery": frozenset({MASTERY_POLICY_FULL_VERSION, MASTERY_POLICY_ID, MASTERY_POLICY_VERSION}),
    "review": frozenset({REVIEW_POLICY_FULL_VERSION, REVIEW_POLICY_ID, REVIEW_POLICY_VERSION}),
}


class MasteryReviewReplayError(ValueError):
    """Raised when the replay cannot safely construct a deterministic state."""

    def __init__(self, message: str, category: str = "invalid_replay_input") -> None:
        self.category = category
        super().__init__(message)


def _policy_spec_name(value: Any, label: str, accepted: frozenset[str], full: str) -> str:
    if value is None:
        return full
    if isinstance(value, str):
        if value in accepted:
            return full
        raise MasteryReviewReplayError(
            f"{label}: unsupported frozen policy {value!r}",
            "invalid_policy_input",
        )
    if isinstance(value, Mapping):
        unknown = sorted(set(value) - {"policy_id", "policy_version"})
        if unknown:
            raise MasteryReviewReplayError(
                f"{label}: unknown field(s): {', '.join(unknown)}",
                "invalid_policy_input",
            )
        policy_id = value.get("policy_id")
        policy_version = value.get("policy_version")
        expected_id, expected_version = full.rsplit("/", 1)
        if policy_id != expected_id or policy_version != expected_version:
            raise MasteryReviewReplayError(
                f"{label}: expected {full!r}",
                "invalid_policy_input",
            )
        return full
    raise MasteryReviewReplayError(
        f"{label}: expected a frozen policy identity string or object",
        "invalid_policy_input",
    )


def _resolve_replay_timezone(
    timezone_name: str | ZoneInfo | None,
    schedule_timezone: str | ZoneInfo | None,
) -> ZoneInfo:
    if timezone_name is None and schedule_timezone is None:
        raise MasteryReviewReplayError(
            "timezone: an explicit IANA timezone is required",
            "invalid_timezone",
        )

    def resolve(value: str | ZoneInfo) -> ZoneInfo:
        if isinstance(value, ZoneInfo):
            return value
        return resolve_timezone(value)

    try:
        selected = resolve(schedule_timezone if schedule_timezone is not None else timezone_name)  # type: ignore[arg-type]
        if timezone_name is not None and schedule_timezone is not None:
            requested = resolve(timezone_name)
            if requested.key != selected.key:
                raise MasteryReviewReplayError(
                    "timezone and schedule_timezone must name the same IANA timezone",
                    "invalid_timezone",
                )
    except ReviewPolicyError as exc:
        raise MasteryReviewReplayError(str(exc), exc.category) from exc
    return selected


def _materialize(value: Any, label: str) -> Any:
    """Materialize one-shot iterables while preserving validator rejection types."""
    if isinstance(value, (str, bytes, Mapping)):
        return value
    try:
        return list(value)
    except TypeError as exc:
        raise ReviewValidationError(
            f"{label}: expected an iterable",
            "invalid_replay_input",
        ) from exc


def _adapt_evidence(record: Mapping[str, Any]) -> tuple[PolicyEvidence, str, str]:
    """Map policy-neutral evidence to the frozen policy primitive explicitly."""
    status = record["evidence_status"]
    kind = record["evidence_kind"]

    if status == "supported" and kind == "comprehensive_correctness":
        correct = record["evidence_value"]["correct"]
        outcome = "success" if correct else "failure"
        reason = "comprehensive_correctness_fact"
    elif status == "supported" and kind in {"case_score", "case_capability_score"}:
        # A score is a real fact, but P4.2 did not freeze its success rubric.
        # The adapter therefore preserves it and gives the policy a no-op.
        outcome = "insufficient"
        reason = "score_outcome_mapping_unfrozen"
    elif status == "insufficient_evidence":
        outcome = "insufficient"
        reason = "insufficient_evidence"
    elif status == "unsupported":
        outcome = "insufficient"
        reason = "unsupported_evidence"
    else:  # pragma: no cover - project_review_evidence validates this domain
        raise MasteryReviewReplayError(
            f"unsupported evidence mapping: status={status!r}, kind={kind!r}",
            "invalid_evidence_outcome",
        )

    return (
        PolicyEvidence(
            evidence_id=record["evidence_id"],
            occurred_at=parse_instant(record["occurred_at"], "review evidence.occurred_at"),
            outcome=outcome,
        ),
        outcome,
        reason,
    )


def _check_evidence_as_of(
    evidence: Iterable[Mapping[str, Any]],
    as_of: datetime,
) -> None:
    for record in evidence:
        occurred_at = parse_instant(record["occurred_at"], "review evidence.occurred_at")
        if occurred_at > as_of:
            raise ReviewPolicyError(
                f"review evidence {record['evidence_id']!r} occurs after as_of",
                "future_evidence",
            )


def _evidence_trace(
    record: Mapping[str, Any],
    outcome: str,
    reason: str,
) -> dict[str, Any]:
    """Return explain metadata without modifying the Review Evidence record."""
    return {
        "evidence_id": record["evidence_id"],
        "source_event_id": record["source_event_id"],
        "review_event_id": record["review_event_id"],
        "occurred_at": record["occurred_at"],
        "attempt_context": record["attempt_context"],
        "evidence_kind": record["evidence_kind"],
        "evidence_status": record["evidence_status"],
        "evidence_value": record["evidence_value"],
        "source_reference": dict(record["source_reference"]),
        "policy_outcome": outcome,
        "policy_outcome_reason": reason,
    }


def replay(
    progress_events: Iterable[Mapping[str, Any]],
    review_events: Iterable[Mapping[str, Any]],
    items: Iterable[Mapping[str, Any]] | ReviewItemCatalog,
    taxonomy: Mapping[str, Any],
    capabilities: Mapping[str, Any],
    *,
    as_of: datetime | str,
    timezone: str | ZoneInfo | None = None,
    schedule_timezone: str | ZoneInfo | None = None,
    mastery_policy: str | Mapping[str, Any] | None = None,
    review_policy: str | Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Rebuild ``MasteryReviewState v0.1`` from immutable inputs.

    ``as_of`` and one explicit IANA timezone are mandatory business inputs.
    ``timezone`` is the public common-envelope name; ``schedule_timezone`` is
    accepted as the policy vocabulary and must agree when both are supplied.
    Only the frozen v0.1 policy identities are currently supported.
    """
    selected_timezone = _resolve_replay_timezone(timezone, schedule_timezone)
    _policy_spec_name(
        mastery_policy,
        "mastery_policy",
        _SUPPORTED_POLICY_SPECS["mastery"],
        MASTERY_POLICY_FULL_VERSION,
    )
    _policy_spec_name(
        review_policy,
        "review_policy",
        _SUPPORTED_POLICY_SPECS["review"],
        REVIEW_POLICY_FULL_VERSION,
    )
    try:
        as_of_instant = parse_instant(as_of, "as_of")
    except ReviewPolicyError as exc:
        raise MasteryReviewReplayError(str(exc), exc.category) from exc

    progress_input = _materialize(progress_events, "progress_events")
    review_input = _materialize(review_events, "review_events")

    try:
        progress_state = progress_replay(progress_input, taxonomy, capabilities)
    except ProgressValidationError as exc:
        raise ReviewValidationError(str(exc), exc.category) from exc

    if isinstance(items, ReviewItemCatalog):
        item_catalog = items
    else:
        item_input = _materialize(items, "items")
        item_catalog = validate_review_items(item_input, taxonomy, capabilities)

    evidence = project_review_evidence(
        progress_input,
        review_input,
        item_catalog,
        taxonomy,
        capabilities,
    )
    _check_evidence_as_of(evidence, as_of_instant)

    active_item_ids = sorted(
        review_item_id
        for review_item_id, item in item_catalog.items.items()
        if item.item.get("status") == "active"
    )
    evidence_by_item: dict[str, list[PolicyEvidence]] = {item_id: [] for item_id in active_item_ids}
    traces_by_item: dict[str, list[dict[str, Any]]] = {item_id: [] for item_id in active_item_ids}
    for record in evidence:
        policy_evidence, outcome, reason = _adapt_evidence(record)
        evidence_by_item[record["review_item_id"]].append(policy_evidence)
        traces_by_item[record["review_item_id"]].append(
            _evidence_trace(record, outcome, reason)
        )

    policy_projection = derive_projection(
        evidence_by_item,
        as_of=as_of_instant,
        schedule_timezone=selected_timezone,
        item_ids=active_item_ids,
    )

    projected_items: dict[str, dict[str, Any]] = {}
    for review_item_id in active_item_ids:
        item = item_catalog.items[review_item_id]
        projected = dict(policy_projection["items"][review_item_id])
        projected.update(
            {
                "item_kind": item.item_kind,
                "canonical_ref": dict(item.canonical_ref),
                "source_reference": dict(item.item["source_reference"]),
                "evidence_ids": [
                    trace["evidence_id"] for trace in traces_by_item[review_item_id]
                ],
                "evidence": traces_by_item[review_item_id],
            }
        )
        projected_items[review_item_id] = projected

    return {
        "schema_version": MASTERY_REVIEW_STATE_SCHEMA_VERSION,
        "review_model_version": REVIEW_MODEL_VERSION,
        "review_event_schema_version": REVIEW_EVENT_SCHEMA_VERSION,
        "review_evidence_version": EVIDENCE_SCHEMA_VERSION,
        "progress_event_schema_version": EVENT_SCHEMA_VERSION,
        "progress_replay_version": REPLAY_RULE_VERSION,
        "mastery_policy_version": MASTERY_POLICY_FULL_VERSION,
        "review_policy_version": REVIEW_POLICY_FULL_VERSION,
        "policy_projection_schema_version": PROJECTION_SCHEMA_VERSION,
        "as_of": policy_projection["as_of"],
        "timezone": policy_projection["schedule_timezone"],
        "schedule_timezone": policy_projection["schedule_timezone"],
        "tzdata_version": policy_projection["tzdata_version"],
        "policy": policy_identity(),
        "outcome_adapter": {
            "adapter_id": OUTCOME_ADAPTER_ID,
            "adapter_version": OUTCOME_ADAPTER_VERSION,
            "adapter": OUTCOME_ADAPTER_FULL_VERSION,
        },
        "progress_replayed_event_count": progress_state["replayed_event_count"],
        "item_order": active_item_ids,
        "items": projected_items,
        "review": dict(policy_projection["review"]),
        "mastery": dict(policy_projection["mastery"]),
    }


__all__ = [
    "MASTERY_REVIEW_STATE_SCHEMA_VERSION",
    "MASTER_REVIEW_STATE_SCHEMA_VERSION",
    "MASTERY_POLICY_FULL_VERSION",
    "REVIEW_POLICY_FULL_VERSION",
    "OUTCOME_ADAPTER_ID",
    "OUTCOME_ADAPTER_VERSION",
    "OUTCOME_ADAPTER_FULL_VERSION",
    "MasteryReviewReplayError",
    "replay",
]
