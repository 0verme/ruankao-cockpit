"""Build small synthetic, self-contained snapshots for P5.1 contract fixtures."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from engine.progress import replay as progress_replay
from engine.review.replay import replay as review_replay


FIXTURE_AS_OF = "2026-01-01T00:00:00Z"
FIXTURE_TIMEZONE = "Asia/Shanghai"
SYNTHETIC_COMMIT = "a" * 40


def build_minimal_snapshot(root: Path) -> dict[str, Any]:
    """Build real v0.1 domain outputs with empty facts and two synthetic items."""
    taxonomy = json.loads((root / "taxonomy/taxonomy.json").read_text(encoding="utf-8"))
    capabilities = json.loads((root / "taxonomy/capabilities.json").read_text(encoding="utf-8"))
    topics = sorted(node["id"] for node in taxonomy["nodes"])
    capability_ids = sorted(item["id"] for item in capabilities["capabilities"])
    topic_id = "DATA.DATABASE.RELATIONAL"
    capability_id = "CASE.DATA_DESIGN"
    item_rows = [
        {
            "schema_version": "review-item/v0.1",
            "review_item_id": f"review/topic/{topic_id}",
            "item_kind": "topic",
            "canonical_ref": {"topic_id": topic_id, "taxonomy_version": taxonomy["taxonomy_version"]},
            "source_reference": {
                "source_id": "synthetic-planner-contract",
                "source_commit": SYNTHETIC_COMMIT,
                "source_path": "fixtures/planner/topic-index.json",
                "source_value": topic_id,
            },
        },
        {
            "schema_version": "review-item/v0.1",
            "review_item_id": f"review/case_capability/{capability_id}",
            "item_kind": "case_capability",
            "canonical_ref": {"capability_id": capability_id, "taxonomy_version": capabilities["taxonomy_version"]},
            "source_reference": {
                "source_id": "synthetic-planner-contract",
                "source_commit": SYNTHETIC_COMMIT,
                "source_path": "fixtures/planner/capability-index.json",
                "source_value": capability_id,
            },
        },
    ]
    progress_state = progress_replay([], taxonomy, capabilities)
    mastery_state = review_replay(
        [], [], item_rows, taxonomy, capabilities,
        as_of=FIXTURE_AS_OF, timezone=FIXTURE_TIMEZONE,
    )
    return {
        "schema_version": "planner-input/v0.1",
        "as_of": FIXTURE_AS_OF,
        "timezone": FIXTURE_TIMEZONE,
        "planner_policy": {
            "policy_id": "planner-policy/input-contract",
            "policy_version": "v0.1",
        },
        "inputs": {
            "progress_state": progress_state,
            "mastery_review_state": mastery_state,
            "taxonomy": {"taxonomy_version": taxonomy["taxonomy_version"], "topic_ids": topics},
            "capabilities": {"taxonomy_version": capabilities["taxonomy_version"], "capability_ids": capability_ids},
            "user_configuration": {
                "schema_version": "user-configuration/v0.1",
                "timezone": FIXTURE_TIMEZONE,
                "daily_available_minutes": 120,
                "study_days": [1, 2, 3, 4, 5],
            },
        },
    }
