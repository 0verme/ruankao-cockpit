from __future__ import annotations

import copy
import json
from pathlib import Path
import re
import unittest

from planner_contract_fixtures import build_minimal_snapshot
from scripts.validate_planner_contract import (
    PlannerContractError,
    canonical_json,
    validate_fixture_set,
    validate_snapshot,
)


ROOT = Path(__file__).resolve().parents[1]


class PlannerInputContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.snapshot = build_minimal_snapshot(ROOT)

    def assert_category(self, category: str, snapshot: dict) -> None:
        with self.assertRaises(PlannerContractError) as context:
            validate_snapshot(snapshot, ROOT)
        self.assertEqual(context.exception.category, category, str(context.exception))

    def test_contract_fixtures_cover_minimum_acceptance_and_rejection_matrix(self) -> None:
        result = validate_fixture_set(ROOT)
        self.assertEqual(result["fixtures"], 14)
        self.assertEqual(result["accepted"], 2)
        self.assertEqual(result["rejected"], 12)
        self.assertEqual(
            result["rejection_categories"],
            {
                "invalid_catalog_version": 2,
                "invalid_policy_input": 1,
                "invalid_schema_version": 1,
                "invalid_timestamp": 1,
                "invalid_timezone": 1,
                "invalid_user_configuration": 2,
                "unknown_capability_id": 1,
                "unknown_item_kind": 1,
                "unknown_review_item": 1,
                "unknown_topic_id": 1,
            },
        )

    def test_valid_minimal_snapshot_is_accepted_without_plan_fields(self) -> None:
        canonical = validate_snapshot(self.snapshot, ROOT)
        self.assertEqual(canonical["schema_version"], "planner-input/v0.1")
        self.assertNotIn("as_of", canonical["inputs"]["progress_state"])
        self.assertNotIn("tasks", canonical)
        self.assertNotIn("priority", canonical)

    def test_zero_capacity_is_valid_and_never_defaulted(self) -> None:
        candidate = copy.deepcopy(self.snapshot)
        candidate["inputs"]["user_configuration"]["daily_available_minutes"] = 0
        canonical = validate_snapshot(candidate, ROOT)
        self.assertEqual(canonical["inputs"]["user_configuration"]["daily_available_minutes"], 0)

    def test_study_days_accept_empty_and_all_seven_days_and_canonicalize(self) -> None:
        empty = copy.deepcopy(self.snapshot)
        empty["inputs"]["user_configuration"]["study_days"] = []
        self.assertEqual(validate_snapshot(empty, ROOT)["inputs"]["user_configuration"]["study_days"], [])

        all_days = copy.deepcopy(self.snapshot)
        all_days["inputs"]["user_configuration"]["study_days"] = [7, 6, 5, 4, 3, 2, 1]
        self.assertEqual(validate_snapshot(all_days, ROOT)["inputs"]["user_configuration"]["study_days"], [1, 2, 3, 4, 5, 6, 7])

    def test_study_days_duplicates_and_non_iso_values_are_rejected(self) -> None:
        duplicate = copy.deepcopy(self.snapshot)
        duplicate["inputs"]["user_configuration"]["study_days"] = [1, 1]
        self.assert_category("invalid_user_configuration", duplicate)

        invalid = copy.deepcopy(self.snapshot)
        invalid["inputs"]["user_configuration"]["study_days"] = [0]
        self.assert_category("invalid_user_configuration", invalid)

    def test_daily_minutes_require_integer_in_range_and_reject_bool(self) -> None:
        for value in (-1, 1441, 1.5, True):
            with self.subTest(value=value):
                candidate = copy.deepcopy(self.snapshot)
                candidate["inputs"]["user_configuration"]["daily_available_minutes"] = value
                self.assert_category("invalid_user_configuration", candidate)

    def test_timezone_is_explicit_iana_and_dst_zone_is_valid(self) -> None:
        candidate = copy.deepcopy(self.snapshot)
        candidate["timezone"] = "America/New_York"
        candidate["inputs"]["user_configuration"]["timezone"] = "America/New_York"
        candidate["inputs"]["mastery_review_state"]["timezone"] = "America/New_York"
        candidate["inputs"]["mastery_review_state"]["schedule_timezone"] = "America/New_York"
        self.assertEqual(validate_snapshot(candidate, ROOT)["timezone"], "America/New_York")

        missing = copy.deepcopy(self.snapshot)
        missing["timezone"] = ""
        self.assert_category("invalid_timezone", missing)

        machine_local = copy.deepcopy(self.snapshot)
        machine_local["timezone"] = "local"
        self.assert_category("invalid_timezone", machine_local)

    def test_as_of_must_be_aware_and_match_review_state_instant(self) -> None:
        naive = copy.deepcopy(self.snapshot)
        naive["as_of"] = "2026-01-01T00:00:00"
        self.assert_category("invalid_timestamp", naive)

        mismatch = copy.deepcopy(self.snapshot)
        mismatch["inputs"]["mastery_review_state"]["as_of"] = "2026-01-01T00:00:01Z"
        self.assert_category("inconsistent_input", mismatch)

        same_instant_other_offset = copy.deepcopy(self.snapshot)
        same_instant_other_offset["as_of"] = "2026-01-01T08:00:00+08:00"
        self.assertEqual(canonical_json(self.snapshot, ROOT), canonical_json(same_instant_other_offset, ROOT))

    def test_root_timezone_configuration_and_review_timezone_must_match(self) -> None:
        mismatch = copy.deepcopy(self.snapshot)
        mismatch["timezone"] = "Asia/Tokyo"
        self.assert_category("inconsistent_input", mismatch)

        review_mismatch = copy.deepcopy(self.snapshot)
        review_mismatch["inputs"]["mastery_review_state"]["schedule_timezone"] = "Asia/Tokyo"
        self.assert_category("inconsistent_input", review_mismatch)

    def test_schema_catalog_and_policy_versions_fail_closed(self) -> None:
        cases = [
            ("invalid_schema_version", ("schema_version",), "planner-input/v9.9"),
            ("invalid_catalog_version", ("inputs", "taxonomy", "taxonomy_version"), "0.2"),
            ("invalid_catalog_version", ("inputs", "capabilities", "taxonomy_version"), "0.2"),
            ("invalid_policy_input", ("planner_policy", "policy_version"), "v9.9"),
        ]
        for category, path, value in cases:
            with self.subTest(path=path):
                candidate = copy.deepcopy(self.snapshot)
                target = candidate
                for part in path[:-1]:
                    target = target[part]
                target[path[-1]] = value
                self.assert_category(category, candidate)

    def test_progress_and_review_replay_versions_must_match(self) -> None:
        mismatch = copy.deepcopy(self.snapshot)
        mismatch["inputs"]["mastery_review_state"]["progress_replay_version"] = "progress-replay/v9.9"
        self.assert_category("inconsistent_input", mismatch)

        unsupported = copy.deepcopy(self.snapshot)
        unsupported["inputs"]["mastery_review_state"]["schema_version"] = "mastery-review-state/v9.9"
        self.assert_category("invalid_schema_version", unsupported)

    def test_unknown_topic_capability_and_review_item_targets_are_rejected(self) -> None:
        topic = copy.deepcopy(self.snapshot)
        topic["inputs"]["mastery_review_state"]["items"]["review/topic/DATA.DATABASE.RELATIONAL"]["canonical_ref"]["topic_id"] = "UNKNOWN.TOPIC"
        self.assert_category("unknown_topic_id", topic)

        capability = copy.deepcopy(self.snapshot)
        capability["inputs"]["mastery_review_state"]["items"]["review/case_capability/CASE.DATA_DESIGN"]["canonical_ref"]["capability_id"] = "CASE.UNKNOWN"
        self.assert_category("unknown_capability_id", capability)

        item = copy.deepcopy(self.snapshot)
        item["inputs"]["mastery_review_state"]["item_order"] = ["review/topic/UNKNOWN.TOPIC"]
        self.assert_category("unknown_review_item", item)

    def test_unapproved_inputs_and_free_text_are_rejected(self) -> None:
        note = copy.deepcopy(self.snapshot)
        note["note"] = "free text is not planner input"
        self.assert_category("invalid_planner_input", note)

        curriculum = copy.deepcopy(self.snapshot)
        curriculum["inputs"]["curriculum"] = {"topic_order": []}
        self.assert_category("invalid_planner_input", curriculum)

    def test_configuration_is_closed_and_required_values_are_not_guessed(self) -> None:
        missing = copy.deepcopy(self.snapshot)
        del missing["inputs"]["user_configuration"]["timezone"]
        self.assert_category("invalid_user_configuration", missing)

        extra = copy.deepcopy(self.snapshot)
        extra["inputs"]["user_configuration"]["subject_preference"] = {"paper": 1}
        self.assert_category("invalid_user_configuration", extra)

    def test_catalog_and_collection_order_do_not_change_canonical_semantics(self) -> None:
        reordered = copy.deepcopy(self.snapshot)
        reordered["inputs"]["taxonomy"]["topic_ids"].reverse()
        reordered["inputs"]["capabilities"]["capability_ids"].reverse()
        reordered["inputs"]["user_configuration"]["study_days"].reverse()
        review = reordered["inputs"]["mastery_review_state"]
        review["item_order"].reverse()
        review["items"] = dict(reversed(list(review["items"].items())))
        progress = reordered["inputs"]["progress_state"]
        progress["topics"] = dict(reversed(list(progress["topics"].items())))
        progress["capabilities"] = dict(reversed(list(progress["capabilities"].items())))
        self.assertEqual(canonical_json(self.snapshot, ROOT), canonical_json(reordered, ROOT))

    def test_mastery_review_values_are_consumed_not_recomputed(self) -> None:
        original = self.snapshot["inputs"]["mastery_review_state"]
        canonical = validate_snapshot(self.snapshot, ROOT)["inputs"]["mastery_review_state"]
        for item_id in original["item_order"]:
            source = original["items"][item_id]
            result = canonical["items"][item_id]
            for key in ("mastery_state", "review_status", "next_due_at", "next_due_local_date", "review_interval_days", "mastery_reason", "review_status_reason", "scheduling_reason"):
                self.assertEqual(result[key], source[key])

    def test_progress_state_timestamp_limitation_is_not_papered_over(self) -> None:
        state = self.snapshot["inputs"]["progress_state"]
        self.assertNotIn("as_of", state)
        self.assertNotIn("source_digest", state)
        self.assertNotIn("replayed_at", state)

    def test_validator_has_no_hidden_wall_clock_calls(self) -> None:
        source = (ROOT / "scripts/validate_planner_contract.py").read_text(encoding="utf-8")
        self.assertIsNone(re.search(r"\b(?:datetime|date)\.(?:now|today)\s*\(", source))


if __name__ == "__main__":
    unittest.main()
