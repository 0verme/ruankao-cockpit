"""Review Model and Review Evidence v0.1 validation primitives.

This module deliberately sits beside ``engine.progress``.  Progress events remain
immutable facts; a review context event explicitly associates one such fact with
one review item and an initial-learning/review context.  No mastery or scheduling
policy is implemented here.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import PurePosixPath
import re
from typing import Any, Iterable, Mapping

from engine.progress.model import Catalogs, ProgressValidationError, validate_events


REVIEW_MODEL_VERSION = "review-model/v0.1"
ITEM_SCHEMA_VERSION = "review-item/v0.1"
REVIEW_EVENT_SCHEMA_VERSION = "review-event/v0.1"
EVIDENCE_SCHEMA_VERSION = "review-evidence/v0.1"
REVIEW_FIXTURE_SCHEMA_VERSION = "review-fixture/v0.1"
IDENTITY_NAMESPACE = "review"

REVIEW_ITEM_KINDS = ("topic", "question", "case_capability")
REVIEW_CONTEXTS = ("initial_learning", "review")
EVIDENCE_STATUSES = ("supported", "insufficient_evidence", "unsupported")
PROGRESS_ATTEMPT_TYPES = ("comprehensive_attempt", "case_attempt")

ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]*$")
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
WINDOWS_ABSOLUTE_RE = re.compile(r"^(?:[A-Za-z]:[\\/]|\\\\)")
FORBIDDEN_LOCAL_PATH_PARTS = (
    "/vol5/",
    "/root/",
    "ruankao-cockpit_base/research",
)
SOURCE_REFERENCE_KEYS = {
    "source_id",
    "source_commit",
    "source_path",
    "source_question_id",
    "golden_set_record_id",
    "source_value",
}


class ReviewValidationError(ValueError):
    """Raised when Review Item, Review Event, or Evidence input is invalid."""

    def __init__(self, message: str, category: str = "invalid_review_contract") -> None:
        self.category = category
        super().__init__(message)


@dataclass(frozen=True)
class ValidatedReviewItem:
    """A validated item descriptor with its canonical identity."""

    item: Mapping[str, Any]
    review_item_id: str
    item_kind: str
    canonical_ref: Mapping[str, Any]
    canonical_key: tuple[str, ...]


@dataclass(frozen=True)
class ReviewItemCatalog:
    """Validated review items indexed by their stable identity."""

    items: Mapping[str, ValidatedReviewItem]
    taxonomy_version: str
    capability_version: str

    def get(self, review_item_id: str) -> ValidatedReviewItem | None:
        return self.items.get(review_item_id)


@dataclass(frozen=True)
class ValidatedReviewEvent:
    """A validated explicit context event and its source progress fact."""

    event: Mapping[str, Any]
    occurred_at: datetime
    source_event: Mapping[str, Any]


def _fail(message: str, category: str = "invalid_review_contract") -> None:
    raise ReviewValidationError(message, category)


def _is_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip()) and "\x00" not in value


def _require_string(value: Any, label: str, category: str = "invalid_review_contract") -> str:
    if not _is_non_empty_string(value):
        _fail(f"{label}: expected a non-empty string", category)
    return value


def _require_identifier(value: Any, label: str) -> str:
    value = _require_string(value, label)
    if ID_RE.fullmatch(value) is None:
        _fail(f"{label}: invalid identifier {value!r}")
    return value


def _check_allowed_keys(value: Mapping[str, Any], allowed: set[str], label: str) -> None:
    unknown = sorted(set(value) - allowed)
    if unknown:
        _fail(f"{label}: unknown field(s): {', '.join(unknown)}")


def _parse_timestamp(value: Any, label: str) -> datetime:
    if not isinstance(value, str) or not value.strip():
        _fail(f"{label}: timestamp must be an ISO 8601 string", "invalid_timestamp")
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        _fail(f"{label}: invalid ISO 8601 timestamp: {value!r}", "invalid_timestamp")
        raise AssertionError("unreachable") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        _fail(f"{label}: timezone is required", "invalid_timestamp")
    return parsed


def _utc(value: datetime) -> datetime:
    return value.astimezone(timezone.utc)


def _canonical_timestamp(value: datetime) -> str:
    return _utc(value).isoformat().replace("+00:00", "Z")


def _looks_like_local_path(value: str) -> bool:
    return (
        value.startswith("/")
        or WINDOWS_ABSOLUTE_RE.match(value) is not None
        or any(part in value for part in FORBIDDEN_LOCAL_PATH_PARTS)
    )


def _validate_source_reference(
    value: Any,
    label: str,
    *,
    require_question_id: bool = False,
) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        _fail(f"{label}: source reference is required", "missing_source_reference")
    _check_allowed_keys(value, SOURCE_REFERENCE_KEYS, label)

    for key in ("source_id", "source_commit", "source_path"):
        if key not in value:
            _fail(f"{label}.{key}: field is required", "missing_source_reference")

    _require_identifier(value["source_id"], f"{label}.source_id")
    source_commit = _require_string(value["source_commit"], f"{label}.source_commit")
    if COMMIT_RE.fullmatch(source_commit) is None:
        _fail(
            f"{label}.source_commit: expected a 40-character lowercase immutable revision",
            "invalid_source_reference",
        )

    source_path = _require_string(value["source_path"], f"{label}.source_path")
    if _looks_like_local_path(source_path):
        _fail(f"{label}.source_path: absolute/local path is forbidden", "forbidden_path")
    if "\\" in source_path:
        _fail(f"{label}.source_path: use repository-relative POSIX paths", "forbidden_path")
    parts = PurePosixPath(source_path).parts
    if not parts or any(part in {".", ".."} for part in parts):
        _fail(
            f"{label}.source_path: path must be repository-relative without traversal",
            "forbidden_path",
        )

    has_question_id = "source_question_id" in value
    if require_question_id and not has_question_id:
        _fail(
            f"{label}.source_question_id: field is required",
            "missing_source_reference",
        )
    if has_question_id:
        _require_identifier(value["source_question_id"], f"{label}.source_question_id")
    if "golden_set_record_id" in value:
        _require_identifier(value["golden_set_record_id"], f"{label}.golden_set_record_id")
    if "source_value" in value:
        _require_string(value["source_value"], f"{label}.source_value")

    return dict(value)


def _build_catalogs(
    taxonomy: Mapping[str, Any] | Catalogs,
    capabilities: Mapping[str, Any] | None,
) -> Catalogs:
    if isinstance(taxonomy, Catalogs):
        if capabilities is not None:
            _fail("capabilities must be omitted when Catalogs is supplied", "invalid_catalog")
        return taxonomy
    if capabilities is None:
        _fail("capabilities document is required", "invalid_catalog")
    try:
        return Catalogs.from_documents(taxonomy, capabilities)
    except ProgressValidationError as exc:
        _fail(str(exc), exc.category)
    raise AssertionError("unreachable")


def _expected_item_id(item_kind: str, canonical_ref: Mapping[str, Any]) -> str:
    if item_kind == "topic":
        return f"{IDENTITY_NAMESPACE}/topic/{canonical_ref['topic_id']}"
    if item_kind == "question":
        return (
            f"{IDENTITY_NAMESPACE}/question/"
            f"{canonical_ref['source_id']}/{canonical_ref['source_question_id']}"
        )
    if item_kind == "case_capability":
        return f"{IDENTITY_NAMESPACE}/case_capability/{canonical_ref['capability_id']}"
    _fail(f"item_kind: unsupported value {item_kind!r}", "unknown_item_kind")
    raise AssertionError("unreachable")


def _validate_canonical_ref(
    item_kind: str,
    value: Any,
    catalogs: Catalogs,
    label: str,
) -> tuple[dict[str, Any], tuple[str, ...]]:
    if not isinstance(value, Mapping):
        _fail(f"{label}: canonical reference is required", "missing_canonical_reference")

    if item_kind == "topic":
        _check_allowed_keys(value, {"topic_id", "taxonomy_version"}, label)
        if "topic_id" not in value or "taxonomy_version" not in value:
            _fail(f"{label}: topic_id and taxonomy_version are required", "missing_canonical_reference")
        topic_id = _require_identifier(value["topic_id"], f"{label}.topic_id")
        if topic_id not in catalogs.topic_ids:
            _fail(f"{label}.topic_id: unknown topic_id {topic_id!r}", "unknown_topic_id")
        taxonomy_version = _require_string(value["taxonomy_version"], f"{label}.taxonomy_version")
        if taxonomy_version != catalogs.taxonomy_version:
            _fail(
                f"{label}.taxonomy_version: expected {catalogs.taxonomy_version!r}",
                "invalid_catalog_version",
            )
        canonical = {"topic_id": topic_id, "taxonomy_version": taxonomy_version}
        return canonical, (item_kind, topic_id)

    if item_kind == "question":
        _check_allowed_keys(value, {"source_id", "source_question_id"}, label)
        if "source_id" not in value or "source_question_id" not in value:
            _fail(
                f"{label}: source_id and source_question_id are required",
                "missing_canonical_reference",
            )
        source_id = _require_identifier(value["source_id"], f"{label}.source_id")
        source_question_id = _require_identifier(
            value["source_question_id"], f"{label}.source_question_id"
        )
        canonical = {"source_id": source_id, "source_question_id": source_question_id}
        return canonical, (item_kind, source_id, source_question_id)

    if item_kind == "case_capability":
        _check_allowed_keys(value, {"capability_id", "taxonomy_version"}, label)
        if "capability_id" not in value or "taxonomy_version" not in value:
            _fail(
                f"{label}: capability_id and taxonomy_version are required",
                "missing_canonical_reference",
            )
        capability_id = _require_identifier(value["capability_id"], f"{label}.capability_id")
        if capability_id not in catalogs.capability_ids:
            _fail(
                f"{label}.capability_id: unknown capability_id {capability_id!r}",
                "unknown_capability_id",
            )
        taxonomy_version = _require_string(value["taxonomy_version"], f"{label}.taxonomy_version")
        if taxonomy_version != catalogs.capability_version:
            _fail(
                f"{label}.taxonomy_version: expected {catalogs.capability_version!r}",
                "invalid_catalog_version",
            )
        canonical = {"capability_id": capability_id, "taxonomy_version": taxonomy_version}
        return canonical, (item_kind, capability_id)

    _fail(f"{label}: unknown item kind {item_kind!r}", "unknown_item_kind")
    raise AssertionError("unreachable")


def _validate_one_item(
    item: Mapping[str, Any],
    catalogs: Catalogs,
    index: int,
) -> ValidatedReviewItem:
    label = f"items[{index}]"
    _check_allowed_keys(
        item,
        {
            "schema_version",
            "review_item_id",
            "item_kind",
            "canonical_ref",
            "source_reference",
            "display_name",
            "status",
        },
        label,
    )
    if item.get("schema_version") != ITEM_SCHEMA_VERSION:
        _fail(
            f"{label}.schema_version: expected {ITEM_SCHEMA_VERSION!r}",
            "invalid_schema_version",
        )
    item_kind = item.get("item_kind")
    if item_kind not in REVIEW_ITEM_KINDS:
        _fail(f"{label}.item_kind: unknown item kind {item_kind!r}", "unknown_item_kind")

    canonical_ref, canonical_key = _validate_canonical_ref(
        item_kind, item.get("canonical_ref"), catalogs, f"{label}.canonical_ref"
    )
    source_reference = _validate_source_reference(
        item.get("source_reference"),
        f"{label}.source_reference",
        require_question_id=item_kind == "question",
    )
    if item_kind == "question":
        if source_reference["source_id"] != canonical_ref["source_id"]:
            _fail(
                f"{label}.source_reference.source_id does not match canonical_ref",
                "invalid_source_reference",
            )
        if source_reference.get("source_question_id") != canonical_ref["source_question_id"]:
            _fail(
                f"{label}.source_reference.source_question_id does not match canonical_ref",
                "invalid_source_reference",
            )

    review_item_id = _require_string(item.get("review_item_id"), f"{label}.review_item_id")
    expected_id = _expected_item_id(item_kind, canonical_ref)
    if review_item_id != expected_id:
        _fail(
            f"{label}.review_item_id: expected stable identity {expected_id!r}",
            "unstable_review_item_id",
        )

    status = item.get("status", "active")
    if status not in {"active", "retired"}:
        _fail(f"{label}.status: expected 'active' or 'retired'")
    if "display_name" in item:
        _require_string(item["display_name"], f"{label}.display_name")

    # Keep the normalized source reference in the returned item without mutating
    # the caller's object.  Identity remains based only on canonical_ref above.
    normalized = dict(item)
    normalized["canonical_ref"] = canonical_ref
    normalized["source_reference"] = source_reference
    normalized["status"] = status
    return ValidatedReviewItem(
        item=normalized,
        review_item_id=review_item_id,
        item_kind=item_kind,
        canonical_ref=canonical_ref,
        canonical_key=canonical_key,
    )


def validate_review_items(
    items: Iterable[Mapping[str, Any]],
    taxonomy: Mapping[str, Any] | Catalogs,
    capabilities: Mapping[str, Any] | None = None,
) -> ReviewItemCatalog:
    """Validate the active/retired Review Item catalog.

    The returned catalog is keyed by the stable ``review_item_id``.  Duplicate
    identities are rejected; aliases must be resolved before this function.
    """
    if isinstance(items, (str, bytes, Mapping)):
        _fail("items must be an iterable of item objects")
    try:
        materialized = list(items)
    except TypeError as exc:
        _fail("items must be an iterable of item objects")
        raise AssertionError("unreachable") from exc

    catalogs = _build_catalogs(taxonomy, capabilities)
    validated: dict[str, ValidatedReviewItem] = {}
    canonical_keys: set[tuple[str, ...]] = set()
    for index, item in enumerate(materialized):
        if not isinstance(item, Mapping):
            _fail(f"items[{index}]: item must be an object")
        candidate = _validate_one_item(item, catalogs, index)
        if candidate.review_item_id in validated:
            _fail(
                f"items[{index}]: duplicate review_item_id {candidate.review_item_id!r}",
                "duplicate_review_item",
            )
        if candidate.canonical_key in canonical_keys:
            _fail(
                f"items[{index}]: duplicate canonical review item {candidate.canonical_key!r}",
                "duplicate_review_item",
            )
        validated[candidate.review_item_id] = candidate
        canonical_keys.add(candidate.canonical_key)

    return ReviewItemCatalog(
        items=validated,
        taxonomy_version=catalogs.taxonomy_version,
        capability_version=catalogs.capability_version,
    )


def _source_index(source_events: Mapping[str, Mapping[str, Any]] | Iterable[Mapping[str, Any]]) -> dict[str, Mapping[str, Any]]:
    if isinstance(source_events, Mapping):
        materialized = list(source_events.values())
    else:
        try:
            materialized = list(source_events)
        except TypeError as exc:
            _fail("source_events must be an iterable of event objects", "invalid_source_event")
            raise AssertionError("unreachable") from exc

    indexed: dict[str, Mapping[str, Any]] = {}
    for index, event in enumerate(materialized):
        if not isinstance(event, Mapping):
            _fail(f"source_events[{index}]: event must be an object", "invalid_source_event")
        event_id = _require_identifier(event.get("event_id"), f"source_events[{index}].event_id")
        if event_id in indexed:
            _fail(f"duplicate source event_id {event_id!r}", "duplicate_source_event")
        indexed[event_id] = event
    return indexed


def _item_matches_source(item: ValidatedReviewItem, source: Mapping[str, Any]) -> None:
    event_type = source.get("event_type")
    if item.item_kind == "question":
        if event_type not in PROGRESS_ATTEMPT_TYPES or not isinstance(source.get("question"), Mapping):
            _fail(
                f"{item.review_item_id}: source event cannot produce question evidence",
                "evidence_item_mismatch",
            )
        question = source["question"]
        if (
            question.get("source_id") != item.canonical_ref["source_id"]
            or question.get("source_question_id") != item.canonical_ref["source_question_id"]
        ):
            _fail(
                f"{item.review_item_id}: source question identity does not match item",
                "evidence_item_mismatch",
            )
        return

    if item.item_kind == "topic":
        if event_type not in PROGRESS_ATTEMPT_TYPES:
            _fail(
                f"{item.review_item_id}: source event cannot produce topic evidence",
                "evidence_item_mismatch",
            )
        if item.canonical_ref["topic_id"] not in source.get("topics", []):
            _fail(
                f"{item.review_item_id}: source event does not reference the topic",
                "evidence_item_mismatch",
            )
        return

    if item.item_kind == "case_capability":
        if event_type != "case_attempt":
            _fail(
                f"{item.review_item_id}: only case_attempt can produce capability evidence",
                "evidence_item_mismatch",
            )
        if item.canonical_ref["capability_id"] not in source.get("capabilities", []):
            _fail(
                f"{item.review_item_id}: source event does not reference the capability",
                "evidence_item_mismatch",
            )
        return

    _fail(f"{item.review_item_id}: unknown item kind", "unknown_item_kind")


def validate_review_events(
    review_events: Iterable[Mapping[str, Any]],
    source_events: Mapping[str, Mapping[str, Any]] | Iterable[Mapping[str, Any]],
    item_catalog: ReviewItemCatalog,
) -> list[ValidatedReviewEvent]:
    """Validate explicit initial-learning/review context events.

    A context event is required to turn a Progress Attempt Fact into Review
    Evidence.  It is intentionally separate from ``progress-event/v0.1``.
    """
    if isinstance(review_events, (str, bytes, Mapping)):
        _fail("review_events must be an iterable of event objects")
    try:
        materialized = list(review_events)
    except TypeError as exc:
        _fail("review_events must be an iterable of event objects")
        raise AssertionError("unreachable") from exc

    sources = _source_index(source_events)
    event_ids: set[str] = set()
    relations: set[tuple[str, str]] = set()
    validated: list[ValidatedReviewEvent] = []
    for index, event in enumerate(materialized):
        label = f"review_events[{index}]"
        if not isinstance(event, Mapping):
            _fail(f"{label}: event must be an object")
        _check_allowed_keys(
            event,
            {
                "schema_version",
                "event_id",
                "event_type",
                "source_event_id",
                "review_item_id",
                "attempt_context",
                "occurred_at",
            },
            label,
        )
        if event.get("schema_version") != REVIEW_EVENT_SCHEMA_VERSION:
            _fail(
                f"{label}.schema_version: expected {REVIEW_EVENT_SCHEMA_VERSION!r}",
                "invalid_schema_version",
            )
        if event.get("event_type") != "review_context":
            _fail(f"{label}.event_type: expected 'review_context'")
        event_id = _require_identifier(event.get("event_id"), f"{label}.event_id")
        if event_id in event_ids:
            _fail(f"{label}: duplicate event_id {event_id!r}", "duplicate_review_event")
        event_ids.add(event_id)

        source_event_id = _require_identifier(event.get("source_event_id"), f"{label}.source_event_id")
        source = sources.get(source_event_id)
        if source is None:
            _fail(
                f"{label}.source_event_id: unknown source event {source_event_id!r}",
                "unknown_source_event",
            )
        review_item_id = _require_string(event.get("review_item_id"), f"{label}.review_item_id")
        item = item_catalog.get(review_item_id)
        if item is None:
            _fail(
                f"{label}.review_item_id: unknown review item {review_item_id!r}",
                "unknown_review_item",
            )
        if item.item.get("status") != "active":
            _fail(
                f"{label}.review_item_id: item is not active",
                "inactive_review_item",
            )
        context = event.get("attempt_context")
        if context not in REVIEW_CONTEXTS:
            _fail(
                f"{label}.attempt_context: expected one of {REVIEW_CONTEXTS!r}",
                "invalid_attempt_context",
            )
        occurred_at = _parse_timestamp(event.get("occurred_at"), f"{label}.occurred_at")
        source_occurred_at = _parse_timestamp(source.get("occurred_at"), f"{label}.source.occurred_at")
        if _utc(occurred_at) != _utc(source_occurred_at):
            _fail(
                f"{label}.occurred_at must equal source event occurred_at",
                "source_timestamp_mismatch",
            )
        _item_matches_source(item, source)

        relation = (source_event_id, review_item_id)
        if relation in relations:
            _fail(
                f"{label}: duplicate context for source event and review item",
                "duplicate_review_context",
            )
        relations.add(relation)
        validated.append(
            ValidatedReviewEvent(
                event=event,
                occurred_at=occurred_at,
                source_event=source,
            )
        )

    return sorted(
        validated,
        key=lambda value: (
            _utc(value.occurred_at),
            value.source_event["event_id"],
            value.event["review_item_id"],
            value.event["event_id"],
        ),
    )


def _validate_score_pair(earned: Any, possible: Any, label: str) -> None:
    if type(earned) is not int or type(possible) is not int:
        _fail(f"{label}: score_earned and score_possible must be integers", "invalid_evidence_value")
    if possible <= 0 or earned < 0 or earned > possible:
        _fail(f"{label}: score must be within 0..score_possible", "invalid_evidence_value")


def _validate_evidence_value(
    evidence_kind: str,
    evidence_status: str,
    evidence_value: Any,
    item_kind: str,
    label: str,
) -> None:
    allowed_kinds: dict[str, tuple[str, str]] = {
        "comprehensive_correctness": ("supported", "question|topic"),
        "case_score": ("supported", "question"),
        "case_capability_score": ("supported", "case_capability"),
        "case_capability_score_missing": ("insufficient_evidence", "case_capability"),
        "case_topic_score_unavailable": ("unsupported", "topic"),
    }
    if evidence_kind not in allowed_kinds:
        _fail(f"{label}.evidence_kind: unknown evidence kind {evidence_kind!r}", "invalid_evidence_kind")
    expected_status, expected_items = allowed_kinds[evidence_kind]
    if evidence_status != expected_status:
        _fail(
            f"{label}: evidence_kind {evidence_kind!r} requires status {expected_status!r}",
            "evidence_item_mismatch",
        )
    if item_kind not in expected_items.split("|"):
        _fail(
            f"{label}: evidence kind {evidence_kind!r} does not match item kind {item_kind!r}",
            "evidence_item_mismatch",
        )

    if evidence_status != "supported":
        if evidence_value is not None:
            _fail(
                f"{label}.evidence_value: insufficient/unsupported evidence must be null",
                "invalid_evidence_value",
            )
        return

    if evidence_kind == "comprehensive_correctness":
        if not isinstance(evidence_value, Mapping) or set(evidence_value) != {"correct"}:
            _fail(
                f"{label}.evidence_value: expected only the boolean correct fact",
                "invalid_evidence_value",
            )
        if type(evidence_value["correct"]) is not bool:
            _fail(f"{label}.evidence_value.correct: expected boolean", "invalid_evidence_value")
        return

    if evidence_kind in {"case_score", "case_capability_score"}:
        if not isinstance(evidence_value, Mapping) or set(evidence_value) != {
            "score_earned",
            "score_possible",
        }:
            _fail(
                f"{label}.evidence_value: expected score_earned and score_possible only",
                "invalid_evidence_value",
            )
        _validate_score_pair(
            evidence_value["score_earned"],
            evidence_value["score_possible"],
            f"{label}.evidence_value",
        )


def _reject_policy_fields(value: Any, label: str) -> None:
    forbidden = {
        "success",
        "failure",
        "mastery",
        "mastered",
        "review_due",
        "review_interval",
        "due_at",
        "schedule",
        "interval",
    }
    if isinstance(value, Mapping):
        for key, child in value.items():
            if key in forbidden:
                _fail(f"{label}: policy/state field {key!r} is not evidence", "policy_field_in_evidence")
            _reject_policy_fields(child, f"{label}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_policy_fields(child, f"{label}[{index}]")


def _validate_one_evidence(
    evidence: Mapping[str, Any],
    item_catalog: ReviewItemCatalog,
    source_events: Mapping[str, Mapping[str, Any]] | None,
    index: int,
) -> None:
    label = f"evidence[{index}]"
    _check_allowed_keys(
        evidence,
        {
            "schema_version",
            "evidence_id",
            "review_item_id",
            "item_kind",
            "source_event_id",
            "source_event_type",
            "review_event_id",
            "occurred_at",
            "attempt_context",
            "evidence_kind",
            "evidence_value",
            "evidence_status",
            "source_reference",
        },
        label,
    )
    if evidence.get("schema_version") != EVIDENCE_SCHEMA_VERSION:
        _fail(
            f"{label}.schema_version: expected {EVIDENCE_SCHEMA_VERSION!r}",
            "invalid_schema_version",
        )
    evidence_id = _require_string(evidence.get("evidence_id"), f"{label}.evidence_id")
    review_item_id = _require_string(evidence.get("review_item_id"), f"{label}.review_item_id")
    item = item_catalog.get(review_item_id)
    if item is None:
        _fail(f"{label}.review_item_id: unknown review item", "unknown_review_item")
    if item.item.get("status") != "active":
        _fail(f"{label}.review_item_id: item is not active", "inactive_review_item")
    if evidence.get("item_kind") != item.item_kind:
        _fail(
            f"{label}.item_kind does not match review item",
            "evidence_item_mismatch",
        )

    source_event_id = _require_identifier(evidence.get("source_event_id"), f"{label}.source_event_id")
    expected_id = f"evidence/{source_event_id}/{review_item_id}"
    if evidence_id != expected_id:
        _fail(
            f"{label}.evidence_id: expected deterministic identity {expected_id!r}",
            "unstable_evidence_id",
        )
    _require_identifier(evidence.get("review_event_id"), f"{label}.review_event_id")
    source_event_type = evidence.get("source_event_type")
    if source_event_type not in PROGRESS_ATTEMPT_TYPES:
        _fail(
            f"{label}.source_event_type: unsupported source event type",
            "invalid_source_event",
        )
    context = evidence.get("attempt_context")
    if context not in REVIEW_CONTEXTS:
        _fail(f"{label}.attempt_context: invalid context", "invalid_attempt_context")
    occurred_at = _parse_timestamp(evidence.get("occurred_at"), f"{label}.occurred_at")
    _validate_source_reference(
        evidence.get("source_reference"),
        f"{label}.source_reference",
        require_question_id=True,
    )
    evidence_status = evidence.get("evidence_status")
    if evidence_status not in EVIDENCE_STATUSES:
        _fail(f"{label}.evidence_status: invalid status", "invalid_evidence_status")
    evidence_kind = _require_string(evidence.get("evidence_kind"), f"{label}.evidence_kind")
    _reject_policy_fields(evidence.get("evidence_value"), f"{label}.evidence_value")
    _validate_evidence_value(
        evidence_kind,
        evidence_status,
        evidence.get("evidence_value"),
        item.item_kind,
        label,
    )

    if source_events is None:
        return
    source = source_events.get(source_event_id)
    if source is None:
        _fail(f"{label}: unknown source event {source_event_id!r}", "unknown_source_event")
    if source.get("event_type") != source_event_type:
        _fail(f"{label}: source event type mismatch", "evidence_item_mismatch")
    source_occurred_at = _parse_timestamp(source.get("occurred_at"), f"{label}.source.occurred_at")
    if _utc(occurred_at) != _utc(source_occurred_at):
        _fail(f"{label}: occurred_at does not match source event", "source_timestamp_mismatch")
    source_reference = evidence["source_reference"]
    if source.get("question") != source_reference:
        _fail(
            f"{label}.source_reference does not match source question reference",
            "invalid_source_reference",
        )
    _item_matches_source(item, source)


def validate_review_evidence(
    evidence: Iterable[Mapping[str, Any]],
    item_catalog: ReviewItemCatalog,
    source_events: Mapping[str, Mapping[str, Any]] | Iterable[Mapping[str, Any]] | None = None,
) -> list[Mapping[str, Any]]:
    """Validate policy-neutral Review Evidence records."""
    if isinstance(evidence, (str, bytes, Mapping)):
        _fail("evidence must be an iterable of evidence objects")
    try:
        materialized = list(evidence)
    except TypeError as exc:
        _fail("evidence must be an iterable of evidence objects")
        raise AssertionError("unreachable") from exc

    indexed_sources: dict[str, Mapping[str, Any]] | None = None
    if source_events is not None:
        indexed_sources = _source_index(source_events)
    evidence_ids: set[str] = set()
    relations: set[tuple[str, str]] = set()
    for index, record in enumerate(materialized):
        if not isinstance(record, Mapping):
            _fail(f"evidence[{index}]: evidence must be an object")
        _validate_one_evidence(record, item_catalog, indexed_sources, index)
        evidence_id = record["evidence_id"]
        relation = (record["source_event_id"], record["review_item_id"])
        if evidence_id in evidence_ids:
            _fail(f"evidence[{index}]: duplicate evidence_id {evidence_id!r}", "duplicate_evidence")
        if relation in relations:
            _fail(
                f"evidence[{index}]: duplicate source event/review item relation",
                "duplicate_evidence",
            )
        evidence_ids.add(evidence_id)
        relations.add(relation)

    return materialized


def _make_evidence(
    context: ValidatedReviewEvent,
    item: ValidatedReviewItem,
) -> dict[str, Any]:
    source = context.source_event
    event_type = source["event_type"]
    evidence_kind: str
    evidence_status: str
    evidence_value: dict[str, Any] | None

    if item.item_kind in {"question", "topic"} and event_type == "comprehensive_attempt":
        evidence_kind = "comprehensive_correctness"
        evidence_status = "supported"
        evidence_value = {"correct": source["correct"]}
    elif item.item_kind == "question" and event_type == "case_attempt":
        evidence_kind = "case_score"
        if "score_earned" in source:
            evidence_status = "supported"
            evidence_value = {
                "score_earned": source["score_earned"],
                "score_possible": source["score_possible"],
            }
        else:
            evidence_status = "insufficient_evidence"
            evidence_value = None
    elif item.item_kind == "topic" and event_type == "case_attempt":
        # A case aggregate score is not a topic score.  Keep the lack of
        # topic-level fact explicit rather than copying the aggregate.
        evidence_kind = "case_topic_score_unavailable"
        evidence_status = "unsupported"
        evidence_value = None
    elif item.item_kind == "case_capability" and event_type == "case_attempt":
        capability_id = item.canonical_ref["capability_id"]
        matching = [
            score
            for score in source.get("capability_scores", [])
            if score.get("capability_id") == capability_id
        ]
        if matching:
            score = matching[0]
            evidence_kind = "case_capability_score"
            evidence_status = "supported"
            evidence_value = {
                "score_earned": score["score_earned"],
                "score_possible": score["score_possible"],
            }
        else:
            evidence_kind = "case_capability_score_missing"
            evidence_status = "insufficient_evidence"
            evidence_value = None
    else:
        _fail(
            f"{item.review_item_id}: source event/item mapping is unsupported",
            "evidence_item_mismatch",
        )

    return {
        "schema_version": EVIDENCE_SCHEMA_VERSION,
        "evidence_id": f"evidence/{source['event_id']}/{item.review_item_id}",
        "review_item_id": item.review_item_id,
        "item_kind": item.item_kind,
        "source_event_id": source["event_id"],
        "source_event_type": event_type,
        "review_event_id": context.event["event_id"],
        "occurred_at": _canonical_timestamp(context.occurred_at),
        "attempt_context": context.event["attempt_context"],
        "evidence_kind": evidence_kind,
        "evidence_value": evidence_value,
        "evidence_status": evidence_status,
        "source_reference": dict(source["question"]),
    }


def project_review_evidence(
    progress_events: Iterable[Mapping[str, Any]],
    review_events: Iterable[Mapping[str, Any]],
    items: Iterable[Mapping[str, Any]] | ReviewItemCatalog,
    taxonomy: Mapping[str, Any] | Catalogs,
    capabilities: Mapping[str, Any] | None = None,
) -> list[Mapping[str, Any]]:
    """Project explicit Review Context Events into deterministic Evidence.

    Existing ``progress-event/v0.1`` semantics are validated unchanged.  A
    source attempt without a matching context event produces no Review Evidence;
    it is not guessed to be initial learning or review.
    """
    catalogs = _build_catalogs(taxonomy, capabilities)
    item_catalog = (
        items if isinstance(items, ReviewItemCatalog) else validate_review_items(items, catalogs)
    )
    try:
        ordered_progress = validate_events(progress_events, catalogs)
    except ProgressValidationError as exc:
        raise ReviewValidationError(str(exc), exc.category) from exc
    source_by_id = {validated.event["event_id"]: validated.event for validated in ordered_progress}
    contexts = validate_review_events(review_events, source_by_id, item_catalog)
    projected = [
        _make_evidence(context, item_catalog.items[context.event["review_item_id"]])
        for context in contexts
    ]
    validate_review_evidence(projected, item_catalog, source_by_id)
    return projected
