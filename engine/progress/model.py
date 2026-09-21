"""Versioned facts and validation primitives for Progress Model v0.1."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import PurePosixPath
import re
from typing import Any, Iterable, Mapping

EVENT_SCHEMA_VERSION = "progress-event/v0.1"
STATE_SCHEMA_VERSION = "progress-state/v0.1"
REPLAY_RULE_VERSION = "progress-replay/v0.1"
TAXONOMY_VERSION = "0.1"

ERROR_CAUSES = (
    "knowledge_gap",
    "reading_error",
    "calculation_error",
    "scoring_point_expression",
)
ACTIVITY_TYPES = (
    "comprehensive_practice",
    "case_practice",
    "review",
    "reading",
    "essay_practice",
    "mock_assessment",
    "other",
)
EVENT_TYPES = (
    "comprehensive_attempt",
    "case_attempt",
    "study_session",
)

ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]*$")
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
WINDOWS_ABSOLUTE_RE = re.compile(r"^(?:[A-Za-z]:[\\/]|\\\\)")
FORBIDDEN_CONTENT_KEYS = {
    "stem",
    "prompt",
    "options",
    "answer",
    "analysis",
    "reference_answer",
    "ocr_text",
    "full_text",
}
FORBIDDEN_LOCAL_PATH_PARTS = (
    "/vol5/",
    "/root/",
    "ruankao-cockpit_base/research",
)


class ProgressValidationError(ValueError):
    """Raised when facts or catalog input cannot be replayed safely."""

    def __init__(self, message: str, category: str = "invalid_event") -> None:
        self.category = category
        super().__init__(message)


@dataclass(frozen=True)
class Catalogs:
    """The immutable taxonomy/capability lookup data required by replay."""

    taxonomy_version: str
    capability_version: str
    topic_ids: frozenset[str]
    topic_parents: Mapping[str, str | None]
    topic_levels: Mapping[str, int]
    taxonomy_totals: Mapping[int, int]
    capability_ids: frozenset[str]

    @classmethod
    def from_documents(
        cls, taxonomy: Mapping[str, Any], capabilities: Mapping[str, Any]
    ) -> "Catalogs":
        if not isinstance(taxonomy, Mapping):
            _fail("taxonomy document must be an object", "invalid_catalog")
        if not isinstance(capabilities, Mapping):
            _fail("capabilities document must be an object", "invalid_catalog")

        taxonomy_version = taxonomy.get("taxonomy_version")
        if taxonomy_version != TAXONOMY_VERSION:
            _fail(
                f"taxonomy: expected version {TAXONOMY_VERSION!r}, got {taxonomy_version!r}",
                "invalid_catalog",
            )
        nodes = taxonomy.get("nodes")
        if not isinstance(nodes, list) or not nodes:
            _fail("taxonomy.nodes must be a non-empty list", "invalid_catalog")

        topic_parents: dict[str, str | None] = {}
        topic_levels: dict[str, int] = {}
        for index, node in enumerate(nodes):
            label = f"taxonomy.nodes[{index}]"
            if not isinstance(node, Mapping):
                _fail(f"{label}: node must be an object", "invalid_catalog")
            topic_id = node.get("id")
            if not isinstance(topic_id, str) or not topic_id:
                _fail(f"{label}: id is required", "invalid_catalog")
            if topic_id in topic_parents:
                _fail(f"{label}: duplicate topic ID {topic_id}", "invalid_catalog")
            level = node.get("level")
            if type(level) is not int or level not in {1, 2, 3}:
                _fail(f"{label}: level must be 1, 2 or 3", "invalid_catalog")
            if len(topic_id.split(".")) != level:
                _fail(f"{label}: ID segments do not match level", "invalid_catalog")
            parent = node.get("parent_id")
            if level == 1:
                if parent is not None:
                    _fail(f"{label}: L1 parent_id must be null", "invalid_catalog")
            elif not isinstance(parent, str) or not parent:
                _fail(f"{label}: parent_id is required", "invalid_catalog")
            topic_parents[topic_id] = parent
            topic_levels[topic_id] = level

        for topic_id, parent in topic_parents.items():
            level = topic_levels[topic_id]
            if parent is not None:
                if parent not in topic_parents:
                    _fail(f"taxonomy: unknown parent {parent!r} for {topic_id}", "invalid_catalog")
                if topic_levels[parent] != level - 1:
                    _fail(f"taxonomy: invalid parent level for {topic_id}", "invalid_catalog")

        for topic_id in topic_parents:
            seen: set[str] = set()
            current: str | None = topic_id
            while current is not None:
                if current in seen:
                    _fail(f"taxonomy: cycle detected at {topic_id}", "invalid_catalog")
                seen.add(current)
                current = topic_parents[current]

        capability_version = capabilities.get("taxonomy_version")
        if capability_version != TAXONOMY_VERSION:
            _fail(
                f"capabilities: expected version {TAXONOMY_VERSION!r}, got {capability_version!r}",
                "invalid_catalog",
            )
        capability_items = capabilities.get("capabilities")
        if not isinstance(capability_items, list) or not capability_items:
            _fail("capabilities.capabilities must be a non-empty list", "invalid_catalog")
        capability_ids: set[str] = set()
        for index, capability in enumerate(capability_items):
            label = f"capabilities[{index}]"
            if not isinstance(capability, Mapping):
                _fail(f"{label}: capability must be an object", "invalid_catalog")
            capability_id = capability.get("id")
            if not isinstance(capability_id, str) or not capability_id.startswith("CASE."):
                _fail(f"{label}: invalid capability ID", "invalid_catalog")
            if capability_id in capability_ids:
                _fail(f"{label}: duplicate capability ID {capability_id}", "invalid_catalog")
            capability_ids.add(capability_id)

        totals = {level: sum(1 for value in topic_levels.values() if value == level) for level in (1, 2, 3)}
        return cls(
            taxonomy_version=taxonomy_version,
            capability_version=capability_version,
            topic_ids=frozenset(topic_parents),
            topic_parents=topic_parents,
            topic_levels=topic_levels,
            taxonomy_totals=totals,
            capability_ids=frozenset(capability_ids),
        )


@dataclass(frozen=True)
class ValidatedEvent:
    """An input event plus its parsed ordering timestamp."""

    event: Mapping[str, Any]
    occurred_at: datetime


def _fail(message: str, category: str = "invalid_event") -> None:
    raise ProgressValidationError(message, category)


def _is_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip()) and "\x00" not in value


def _require_string(value: Any, label: str, category: str = "invalid_event") -> str:
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


def _looks_like_local_path(value: str) -> bool:
    return (
        value.startswith("/")
        or WINDOWS_ABSOLUTE_RE.match(value) is not None
        or any(part in value for part in FORBIDDEN_LOCAL_PATH_PARTS)
    )


def _reject_hidden_content(value: Any, label: str) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            if key in FORBIDDEN_CONTENT_KEYS:
                _fail(f"{label}: disallowed question/content field {key!r}", "forbidden_content")
            _reject_hidden_content(child, f"{label}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_hidden_content(child, f"{label}[{index}]")
    elif isinstance(value, str) and _looks_like_local_path(value):
        _fail(f"{label}: absolute/local path is forbidden", "forbidden_path")


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


def _validate_question_reference(value: Any, label: str) -> None:
    if not isinstance(value, Mapping):
        _fail(f"{label}: question reference must be an object")
    _check_allowed_keys(
        value,
        {"source_id", "source_commit", "source_path", "source_question_id", "golden_set_record_id"},
        label,
    )
    _require_identifier(value.get("source_id"), f"{label}.source_id")
    source_commit = _require_string(value.get("source_commit"), f"{label}.source_commit")
    if COMMIT_RE.fullmatch(source_commit) is None:
        _fail(f"{label}.source_commit: expected a 40-character lowercase immutable revision")
    source_path = _require_string(value.get("source_path"), f"{label}.source_path")
    if source_path.startswith("/") or WINDOWS_ABSOLUTE_RE.match(source_path) is not None:
        _fail(f"{label}.source_path: absolute path is forbidden", "forbidden_path")
    if "\\" in source_path or ".." in PurePosixPath(source_path).parts:
        _fail(f"{label}.source_path: path must be repository-relative without traversal", "forbidden_path")
    if "golden_set_record_id" in value:
        _require_identifier(value["golden_set_record_id"], f"{label}.golden_set_record_id")
    if "source_question_id" not in value:
        _fail(f"{label}.source_question_id: field is required")
    _require_identifier(value.get("source_question_id"), f"{label}.source_question_id")


def _validate_topics(value: Any, catalogs: Catalogs, label: str, required: bool = True) -> tuple[str, ...]:
    if value is None and not required:
        return ()
    if not isinstance(value, list) or (required and not value):
        _fail(f"{label}: expected a non-empty list of topic IDs")
    topics: list[str] = []
    for index, topic_id in enumerate(value):
        topic_id = _require_identifier(topic_id, f"{label}[{index}]")
        if topic_id not in catalogs.topic_ids:
            _fail(f"{label}[{index}]: unknown topic_id {topic_id!r}", "unknown_topic_id")
        if topic_id in topics:
            _fail(f"{label}: duplicate topic_id {topic_id!r}")
        topics.append(topic_id)
    return tuple(topics)


def _validate_capabilities(value: Any, catalogs: Catalogs, label: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not value:
        _fail(f"{label}: expected a non-empty list of capability IDs")
    capabilities: list[str] = []
    for index, capability_id in enumerate(value):
        capability_id = _require_identifier(capability_id, f"{label}[{index}]")
        if capability_id not in catalogs.capability_ids:
            _fail(
                f"{label}[{index}]: unknown capability_id {capability_id!r}",
                "unknown_capability_id",
            )
        if capability_id in capabilities:
            _fail(f"{label}: duplicate capability_id {capability_id!r}")
        capabilities.append(capability_id)
    return tuple(capabilities)


def _validate_score_pair(earned: Any, possible: Any, label: str) -> None:
    if type(earned) is not int or type(possible) is not int:
        _fail(f"{label}: score_earned and score_possible must be integers", "invalid_score")
    if possible <= 0:
        _fail(f"{label}: score_possible must be greater than zero", "invalid_score")
    if earned < 0 or earned > possible:
        _fail(f"{label}: score_earned must be between zero and score_possible", "invalid_score")


def _validate_optional_score_pair(event: Mapping[str, Any], label: str) -> None:
    has_earned = "score_earned" in event
    has_possible = "score_possible" in event
    if has_earned != has_possible:
        _fail(f"{label}: score_earned and score_possible must appear together", "invalid_score")
    if has_earned:
        _validate_score_pair(event["score_earned"], event["score_possible"], label)


def _validate_assessment_id(event: Mapping[str, Any]) -> None:
    if "assessment_id" in event:
        _require_identifier(event["assessment_id"], "event.assessment_id")


def _validate_session_reference(event: Mapping[str, Any]) -> None:
    if "session_id" in event:
        _require_identifier(event["session_id"], "event.session_id")


def _validate_note(event: Mapping[str, Any]) -> None:
    if "note" in event and not isinstance(event["note"], str):
        _fail("event.note: note must be a string")


def _validate_comprehensive(event: Mapping[str, Any], catalogs: Catalogs) -> tuple[str, ...]:
    _check_allowed_keys(
        event,
        {
            "event_id",
            "schema_version",
            "event_type",
            "occurred_at",
            "question",
            "topics",
            "correct",
            "error_cause",
            "assessment_id",
            "session_id",
            "note",
        },
        "comprehensive_attempt",
    )
    _validate_question_reference(event.get("question"), "comprehensive_attempt.question")
    topics = _validate_topics(event.get("topics"), catalogs, "comprehensive_attempt.topics")
    if type(event.get("correct")) is not bool:
        _fail("comprehensive_attempt.correct: expected a boolean")
    if event["correct"]:
        if "error_cause" in event:
            _fail("comprehensive_attempt.error_cause: correct attempts cannot have an error cause")
    elif "error_cause" in event:
        if event["error_cause"] not in ERROR_CAUSES:
            _fail(f"comprehensive_attempt.error_cause: invalid cause {event['error_cause']!r}")
    _validate_assessment_id(event)
    _validate_session_reference(event)
    _validate_note(event)
    return topics


def _validate_case(event: Mapping[str, Any], catalogs: Catalogs) -> tuple[str, ...]:
    _check_allowed_keys(
        event,
        {
            "event_id",
            "schema_version",
            "event_type",
            "occurred_at",
            "question",
            "topics",
            "capabilities",
            "score_earned",
            "score_possible",
            "capability_scores",
            "assessment_id",
            "session_id",
            "note",
        },
        "case_attempt",
    )
    _validate_question_reference(event.get("question"), "case_attempt.question")
    _validate_topics(event.get("topics"), catalogs, "case_attempt.topics")
    capabilities = _validate_capabilities(event.get("capabilities"), catalogs, "case_attempt.capabilities")
    _validate_optional_score_pair(event, "case_attempt")

    if "capability_scores" in event:
        scores = event["capability_scores"]
        if not isinstance(scores, list):
            _fail("case_attempt.capability_scores: expected a list", "invalid_score")
        seen: set[str] = set()
        for index, score in enumerate(scores):
            label = f"case_attempt.capability_scores[{index}]"
            if not isinstance(score, Mapping):
                _fail(f"{label}: expected an object", "invalid_score")
            _check_allowed_keys(score, {"capability_id", "score_earned", "score_possible"}, label)
            capability_id = _require_identifier(score.get("capability_id"), f"{label}.capability_id")
            if capability_id not in catalogs.capability_ids:
                _fail(f"{label}: unknown capability_id {capability_id!r}", "unknown_capability_id")
            if capability_id not in capabilities:
                _fail(
                    f"{label}: capability_id {capability_id!r} is not listed in capabilities",
                    "invalid_score",
                )
            if capability_id in seen:
                _fail(f"{label}: duplicate capability score evidence", "invalid_score")
            seen.add(capability_id)
            if "score_earned" not in score or "score_possible" not in score:
                _fail(f"{label}: score pair is required", "invalid_score")
            _validate_score_pair(score["score_earned"], score["score_possible"], label)

    _validate_assessment_id(event)
    _validate_session_reference(event)
    _validate_note(event)
    return tuple(capabilities)


def _validate_session(event: Mapping[str, Any], catalogs: Catalogs) -> tuple[str, ...]:
    _check_allowed_keys(
        event,
        {
            "event_id",
            "schema_version",
            "event_type",
            "occurred_at",
            "session_id",
            "started_at",
            "ended_at",
            "duration_minutes",
            "activity_type",
            "topics",
            "note",
        },
        "study_session",
    )
    _require_identifier(event.get("session_id"), "study_session.session_id")
    started_at = _parse_timestamp(event.get("started_at"), "study_session.started_at")
    occurred_at = _parse_timestamp(event.get("occurred_at"), "study_session.occurred_at")
    if occurred_at.astimezone(timezone.utc) != started_at.astimezone(timezone.utc):
        _fail("study_session.occurred_at must equal started_at", "invalid_timestamp")
    if event.get("activity_type") not in ACTIVITY_TYPES:
        _fail(f"study_session.activity_type: invalid value {event.get('activity_type')!r}")

    ended_at: datetime | None = None
    if "ended_at" in event:
        ended_at = _parse_timestamp(event["ended_at"], "study_session.ended_at")
        if ended_at.astimezone(timezone.utc) < started_at.astimezone(timezone.utc):
            _fail("study_session.ended_at cannot precede started_at", "invalid_duration")

    has_duration = "duration_minutes" in event
    if has_duration:
        duration = event["duration_minutes"]
        if type(duration) is not int or duration < 0:
            _fail("study_session.duration_minutes must be a non-negative integer", "invalid_duration")
    if ended_at is None and not has_duration:
        _fail("study_session needs ended_at or duration_minutes", "invalid_duration")
    if ended_at is not None and has_duration:
        elapsed_seconds = int(
            (ended_at.astimezone(timezone.utc) - started_at.astimezone(timezone.utc)).total_seconds()
        )
        if elapsed_seconds % 60 != 0 or event["duration_minutes"] != elapsed_seconds // 60:
            _fail(
                "study_session.duration_minutes must equal exact elapsed whole minutes",
                "invalid_duration",
            )
    topics = _validate_topics(event.get("topics"), catalogs, "study_session.topics", required=False)
    _validate_note(event)
    return topics


def validate_events(events: Iterable[Mapping[str, Any]], catalogs: Catalogs) -> list[ValidatedEvent]:
    """Validate all events and return them in deterministic replay order."""
    if isinstance(events, (str, bytes, Mapping)):
        _fail("events must be an iterable of event objects")
    try:
        materialized = list(events)
    except TypeError as exc:
        _fail("events must be an iterable of event objects")
        raise AssertionError("unreachable") from exc

    validated: list[ValidatedEvent] = []
    event_ids: set[str] = set()
    session_ids: set[str] = set()
    for index, event in enumerate(materialized):
        label = f"events[{index}]"
        if not isinstance(event, Mapping):
            _fail(f"{label}: event must be an object")
        _reject_hidden_content(event, label)
        _check_allowed_keys(
            event,
            {
                "event_id",
                "schema_version",
                "event_type",
                "occurred_at",
                "question",
                "topics",
                "correct",
                "error_cause",
                "capabilities",
                "score_earned",
                "score_possible",
                "capability_scores",
                "session_id",
                "started_at",
                "ended_at",
                "duration_minutes",
                "activity_type",
                "assessment_id",
                "note",
            },
            label,
        )
        event_id = _require_identifier(event.get("event_id"), f"{label}.event_id")
        if event_id in event_ids:
            _fail(f"{label}: duplicate event_id {event_id!r}", "duplicate_event_id")
        event_ids.add(event_id)
        if event.get("schema_version") != EVENT_SCHEMA_VERSION:
            _fail(
                f"{label}.schema_version: expected {EVENT_SCHEMA_VERSION!r}",
                "invalid_schema_version",
            )
        event_type = event.get("event_type")
        if event_type not in EVENT_TYPES:
            _fail(f"{label}.event_type: unknown event type {event_type!r}", "unknown_event_type")
        occurred_at = _parse_timestamp(event.get("occurred_at"), f"{label}.occurred_at")

        if event_type == "comprehensive_attempt":
            _validate_comprehensive(event, catalogs)
        elif event_type == "case_attempt":
            _validate_case(event, catalogs)
        else:
            _validate_session(event, catalogs)
            session_id = event["session_id"]
            if session_id in session_ids:
                _fail(f"{label}: duplicate session_id {session_id!r}", "duplicate_session_id")
            session_ids.add(session_id)

        validated.append(ValidatedEvent(event=event, occurred_at=occurred_at))

    return sorted(
        validated,
        key=lambda item: (item.occurred_at.astimezone(timezone.utc), item.event["event_id"]),
    )
