"""Synthetic facts for the Day 1 execution → replay → Day 2 replan proof."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable, Mapping

from engine.progress import replay as progress_replay
from engine.review.replay import replay as review_replay
from planner_replay_fixtures import (
    DUE_TOPIC,
    OVERDUE_TOPIC,
    SYNTHETIC_COMMIT,
    TIMEZONE,
    _item,
)

DAY_1 = "2026-01-01T10:00:00+08:00"
DAY_2 = "2026-01-02T10:00:00+08:00"
TOPIC_A = OVERDUE_TOPIC
TOPIC_B = DUE_TOPIC


def _attempt(
    event_id: str,
    occurred_at: str,
    topic_id: str,
    *,
    correct: bool = True,
) -> dict[str, Any]:
    event = {
        "event_id": event_id,
        "schema_version": "progress-event/v0.1",
        "event_type": "comprehensive_attempt",
        "occurred_at": occurred_at,
        "question": {
            "source_id": "synthetic-task-execution-bank",
            "source_commit": SYNTHETIC_COMMIT,
            "source_path": "fixtures/question-index.json",
            "source_question_id": event_id,
        },
        "topics": [topic_id],
        "correct": correct,
    }
    if not correct:
        event["error_cause"] = "knowledge_gap"
    return event


def _context(event: Mapping[str, Any], review_item_id: str, context: str, event_id: str) -> dict[str, Any]:
    return {
        "schema_version": "review-event/v0.1",
        "event_id": event_id,
        "event_type": "review_context",
        "source_event_id": event["event_id"],
        "review_item_id": review_item_id,
        "attempt_context": context,
        "occurred_at": event["occurred_at"],
    }


def build_day1_fixture(root: Path) -> dict[str, Any]:
    """Create two existing scheduled topics with different Day 1 due states.

    A had an initial success on Dec 20 and a spaced review success on Dec 21;
    its three-day interval made it overdue by Jan 1. B's Dec 31 initial success
    makes it due Jan 1. C/D are the first two otherwise-unlearned L3 topics.
    """
    taxonomy = json.loads((root / "taxonomy/taxonomy.json").read_text(encoding="utf-8"))
    capabilities = json.loads((root / "taxonomy/capabilities.json").read_text(encoding="utf-8"))
    review_item_a = f"review/topic/{TOPIC_A}"
    review_item_b = f"review/topic/{TOPIC_B}"

    a_initial = _attempt("seed-a-initial", "2025-12-20T10:00:00+08:00", TOPIC_A)
    a_spaced = _attempt("seed-a-spaced", "2025-12-21T10:00:00+08:00", TOPIC_A)
    b_initial = _attempt("seed-b-initial", "2025-12-31T10:00:00+08:00", TOPIC_B)
    progress_events = [a_initial, a_spaced, b_initial]
    review_events = [
        _context(a_initial, review_item_a, "initial_learning", "seed-a-initial-context"),
        _context(a_spaced, review_item_a, "review", "seed-a-spaced-context"),
        _context(b_initial, review_item_b, "initial_learning", "seed-b-initial-context"),
    ]
    items = [_item(TOPIC_A), _item(TOPIC_B)]
    return {
        "taxonomy": taxonomy,
        "capabilities": capabilities,
        "progress_events": progress_events,
        "review_events": review_events,
        "items": items,
        "topic_a": TOPIC_A,
        "topic_b": TOPIC_B,
    }


def build_planner_input(
    root: Path,
    fixture: Mapping[str, Any],
    progress_events: Iterable[Mapping[str, Any]],
    review_events: Iterable[Mapping[str, Any]],
    *,
    as_of: str,
    capacity: int = 60,
) -> dict[str, Any]:
    taxonomy = fixture["taxonomy"]
    capabilities = fixture["capabilities"]
    progress_state = progress_replay(progress_events, taxonomy, capabilities)
    mastery_state = review_replay(
        progress_events,
        review_events,
        fixture["items"],
        taxonomy,
        capabilities,
        as_of=as_of,
        timezone=TIMEZONE,
    )
    topic_ids = sorted(node["id"] for node in taxonomy["nodes"])
    capability_ids = sorted(item["id"] for item in capabilities["capabilities"])
    return {
        "schema_version": "planner-input/v0.1",
        "as_of": as_of,
        "timezone": TIMEZONE,
        "planner_policy": {"policy_id": "planner-policy/input-contract", "policy_version": "v0.1"},
        "inputs": {
            "progress_state": progress_state,
            "mastery_review_state": mastery_state,
            "taxonomy": {"taxonomy_version": taxonomy["taxonomy_version"], "topic_ids": topic_ids},
            "capabilities": {
                "taxonomy_version": capabilities["taxonomy_version"],
                "capability_ids": capability_ids,
            },
            "user_configuration": {
                "schema_version": "user-configuration/v0.1",
                "timezone": TIMEZONE,
                "daily_available_minutes": capacity,
                "study_days": [1, 2, 3, 4, 5, 6, 7],
            },
        },
    }


def make_attempt(
    event_id: str,
    occurred_at: str,
    topic_id: str,
    *,
    correct: bool,
) -> dict[str, Any]:
    """Build an objective caller-supplied fact for an execution test."""
    return _attempt(event_id, occurred_at, topic_id, correct=correct)
