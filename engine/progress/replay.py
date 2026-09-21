"""Pure deterministic replay from immutable Progress Events to ProgressState."""
from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Iterable, Mapping

from .model import (
    Catalogs,
    EVENT_SCHEMA_VERSION,
    ERROR_CAUSES,
    REPLAY_RULE_VERSION,
    STATE_SCHEMA_VERSION,
    validate_events,
)


def _ratio(numerator: int, denominator: int) -> float | None:
    if denominator == 0:
        return None
    value = (Decimal(numerator) / Decimal(denominator)).quantize(
        Decimal("0.0001"), rounding=ROUND_HALF_UP
    )
    return float(value)


def _parse_timestamp(value: str) -> datetime:
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    return datetime.fromisoformat(normalized)


def _duration_minutes(event: Mapping[str, Any]) -> int:
    if "duration_minutes" in event:
        return event["duration_minutes"]
    started = _parse_timestamp(event["started_at"]).astimezone(timezone.utc)
    ended = _parse_timestamp(event["ended_at"]).astimezone(timezone.utc)
    return int((ended - started).total_seconds() // 60)


def _new_topic_metric() -> dict[str, Any]:
    return {
        "attempt_count": 0,
        "correct_count": 0,
        "incorrect_count": 0,
        "accuracy": None,
    }


def _new_capability_metric() -> dict[str, Any]:
    return {
        "attempt_count": 0,
        "score_earned": 0,
        "score_possible": 0,
        "score_ratio": None,
        "evidence_status": "insufficient_evidence",
    }


def _mark_coverage(topic_id: str, catalogs: Catalogs, covered: dict[int, set[str]]) -> None:
    current: str | None = topic_id
    while current is not None:
        level = catalogs.topic_levels[current]
        covered[level].add(current)
        current = catalogs.topic_parents[current]


def replay(
    events: Iterable[Mapping[str, Any]],
    taxonomy: Mapping[str, Any],
    capabilities: Mapping[str, Any],
) -> dict[str, Any]:
    """Replay events into a JSON-compatible, deterministic ProgressState.

    The function validates every event before applying any aggregation. It never
    mutates the input event sequence, taxonomy document, or capability document.
    """
    catalogs = Catalogs.from_documents(taxonomy, capabilities)
    ordered_events = validate_events(events, catalogs)

    global_attempt_count = 0
    global_correct_count = 0
    global_incorrect_count = 0

    case_attempt_count = 0
    case_scored_attempt_count = 0
    case_score_earned = 0
    case_score_possible = 0

    topic_metrics = {topic_id: _new_topic_metric() for topic_id in sorted(catalogs.topic_ids)}
    capability_metrics = {
        capability_id: _new_capability_metric() for capability_id in sorted(catalogs.capability_ids)
    }
    covered: dict[int, set[str]] = {1: set(), 2: set(), 3: set()}
    error_count_by_cause = {cause: 0 for cause in ERROR_CAUSES}
    classified_error_count = 0
    unclassified_error_count = 0
    study_minutes = 0
    study_session_count = 0

    for validated in ordered_events:
        event = validated.event
        event_type = event["event_type"]
        if event_type == "comprehensive_attempt":
            global_attempt_count += 1
            correct = event["correct"]
            if correct:
                global_correct_count += 1
            else:
                global_incorrect_count += 1
                cause = event.get("error_cause")
                if cause is None:
                    unclassified_error_count += 1
                else:
                    classified_error_count += 1
                    error_count_by_cause[cause] += 1

            for topic_id in event["topics"]:
                metric = topic_metrics[topic_id]
                metric["attempt_count"] += 1
                if correct:
                    metric["correct_count"] += 1
                else:
                    metric["incorrect_count"] += 1

            for topic_id in event["topics"]:
                _mark_coverage(topic_id, catalogs, covered)

        elif event_type == "case_attempt":
            case_attempt_count += 1
            for topic_id in event["topics"]:
                _mark_coverage(topic_id, catalogs, covered)

            if "score_earned" in event:
                case_scored_attempt_count += 1
                case_score_earned += event["score_earned"]
                case_score_possible += event["score_possible"]

            for evidence in event.get("capability_scores", []):
                metric = capability_metrics[evidence["capability_id"]]
                metric["attempt_count"] += 1
                metric["score_earned"] += evidence["score_earned"]
                metric["score_possible"] += evidence["score_possible"]

        else:
            study_session_count += 1
            study_minutes += _duration_minutes(event)

    for metric in topic_metrics.values():
        metric["accuracy"] = _ratio(metric["correct_count"], metric["attempt_count"])
    for metric in capability_metrics.values():
        if metric["attempt_count"] > 0:
            metric["score_ratio"] = _ratio(metric["score_earned"], metric["score_possible"])
            metric["evidence_status"] = "sufficient"

    coverage: dict[str, dict[str, Any]] = {}
    for level in (1, 2, 3):
        total = catalogs.taxonomy_totals[level]
        coverage[f"l{level}"] = {
            "covered": len(covered[level]),
            "total": total,
            "ratio": _ratio(len(covered[level]), total),
        }

    error_cause_mix = {
        cause: _ratio(error_count_by_cause[cause], classified_error_count)
        for cause in ERROR_CAUSES
    }

    return {
        "schema_version": STATE_SCHEMA_VERSION,
        "replay_rule_version": REPLAY_RULE_VERSION,
        "event_schema_version": EVENT_SCHEMA_VERSION,
        "taxonomy_version": catalogs.taxonomy_version,
        "capability_version": catalogs.capability_version,
        "replayed_event_count": len(ordered_events),
        "global": {
            "attempt_count": global_attempt_count,
            "correct_count": global_correct_count,
            "incorrect_count": global_incorrect_count,
            "accuracy": _ratio(global_correct_count, global_attempt_count),
        },
        "case": {
            "attempt_count": case_attempt_count,
            "scored_attempt_count": case_scored_attempt_count,
            "score_earned": case_score_earned,
            "score_possible": case_score_possible,
            "score_ratio": _ratio(case_score_earned, case_score_possible),
        },
        "topics": topic_metrics,
        "capabilities": capability_metrics,
        "errors": {
            "error_count": global_incorrect_count,
            "classified_error_count": classified_error_count,
            "unclassified_error_count": unclassified_error_count,
            "error_count_by_cause": error_count_by_cause,
            "error_cause_mix": error_cause_mix,
        },
        "coverage": coverage,
        "study": {
            "session_count": study_session_count,
            "study_minutes": study_minutes,
        },
    }
