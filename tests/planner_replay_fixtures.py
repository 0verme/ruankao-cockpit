"""Synthetic, replay-backed inputs for the minimal Today Planner tests."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

from engine.progress import replay as progress_replay
from engine.review.replay import replay as review_replay

AS_OF = "2026-01-01T00:00:00Z"
TIMEZONE = "Asia/Shanghai"
SYNTHETIC_COMMIT = "c" * 40
OVERDUE_TOPIC = "DATA.CACHE.CACHE_FAILURE"
DUE_TOPIC = "QUALITY.ATTRIBUTES.PERFORMANCE"
OVERDUE_AT = "2025-12-28T10:00:00+08:00"
DUE_AT = "2025-12-31T10:00:00+08:00"


def _item(topic_id: str) -> dict[str, Any]:
    return {
        "schema_version": "review-item/v0.1",
        "review_item_id": f"review/topic/{topic_id}",
        "item_kind": "topic",
        "canonical_ref": {"topic_id": topic_id, "taxonomy_version": "0.1"},
        "source_reference": {
            "source_id": "synthetic-planner-index",
            "source_commit": SYNTHETIC_COMMIT,
            "source_path": "fixtures/topic-index.json",
            "source_value": topic_id,
        },
    }


def build_today_snapshot(
    root: Path,
    *,
    capacity: int = 60,
    review_specs: Iterable[tuple[str, str]] = (),
    evidenced_topics: Iterable[str] = (),
    as_of: str = AS_OF,
    timezone_name: str = TIMEZONE,
    study_days: Iterable[int] = (1, 2, 3, 4, 5),
) -> dict[str, Any]:
    """Build a full input snapshot through the real Progress/Review replays.

    ``review_specs`` maps topic IDs to the timestamp of a supported initial
    learning fact; its resulting review due status is determined only by the
    frozen upstream review replay.
    """
    taxonomy = json.loads((root / "taxonomy/taxonomy.json").read_text(encoding="utf-8"))
    capabilities = json.loads((root / "taxonomy/capabilities.json").read_text(encoding="utf-8"))
    review_times = dict(review_specs)
    evidenced = set(evidenced_topics)
    topic_times = {topic_id: "2025-12-30T10:00:00+08:00" for topic_id in evidenced}
    topic_times.update(review_times)
    events: list[dict[str, Any]] = []
    contexts: list[dict[str, Any]] = []
    items = [_item(topic_id) for topic_id in sorted(review_times)]

    for index, (topic_id, occurred_at) in enumerate(sorted(topic_times.items())):
        event_id = f"planner-attempt-{index:04d}"
        source_question_id = f"q-{index:04d}"
        source = {
            "event_id": event_id,
            "schema_version": "progress-event/v0.1",
            "event_type": "comprehensive_attempt",
            "occurred_at": occurred_at,
            "question": {
                "source_id": "synthetic-planner-bank",
                "source_commit": SYNTHETIC_COMMIT,
                "source_path": "fixtures/question-index.json",
                "source_question_id": source_question_id,
            },
            "topics": [topic_id],
            # Wrong answers are still explicit learning evidence and must not
            # make a topic look unlearned.
            "correct": topic_id not in evidenced,
        }
        if not source["correct"]:
            source["error_cause"] = "knowledge_gap"
        events.append(source)
        if topic_id in review_times:
            contexts.append({
                "schema_version": "review-event/v0.1",
                "event_id": f"planner-context-{index:04d}",
                "event_type": "review_context",
                "source_event_id": event_id,
                "review_item_id": f"review/topic/{topic_id}",
                "attempt_context": "initial_learning",
                "occurred_at": occurred_at,
            })

    progress_state = progress_replay(events, taxonomy, capabilities)
    mastery_state = review_replay(
        events,
        contexts,
        items,
        taxonomy,
        capabilities,
        as_of=as_of,
        timezone=timezone_name,
    )
    topic_ids = sorted(node["id"] for node in taxonomy["nodes"])
    capability_ids = sorted(item["id"] for item in capabilities["capabilities"])
    return {
        "schema_version": "planner-input/v0.1",
        "as_of": as_of,
        "timezone": timezone_name,
        "planner_policy": {"policy_id": "planner-policy/input-contract", "policy_version": "v0.1"},
        "inputs": {
            "progress_state": progress_state,
            "mastery_review_state": mastery_state,
            "taxonomy": {"taxonomy_version": taxonomy["taxonomy_version"], "topic_ids": topic_ids},
            "capabilities": {"taxonomy_version": capabilities["taxonomy_version"], "capability_ids": capability_ids},
            "user_configuration": {
                "schema_version": "user-configuration/v0.1",
                "timezone": timezone_name,
                "daily_available_minutes": capacity,
                "study_days": list(study_days),
            },
        },
    }
