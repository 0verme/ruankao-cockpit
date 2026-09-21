from __future__ import annotations

import copy
import json
from pathlib import Path
import random
import unittest

from engine.progress import ProgressValidationError, replay


ROOT = Path(__file__).resolve().parents[1]
TAXONOMY = json.loads((ROOT / "taxonomy/taxonomy.json").read_text(encoding="utf-8"))
CAPABILITIES = json.loads((ROOT / "taxonomy/capabilities.json").read_text(encoding="utf-8"))
FIXTURE_ROOT = ROOT / "data/progress/fixtures"


def load_fixture(name: str) -> dict:
    return json.loads((FIXTURE_ROOT / f"{name}.json").read_text(encoding="utf-8"))


def run_fixture(name: str) -> dict:
    return replay(load_fixture(name)["events"], TAXONOMY, CAPABILITIES)


class ProgressReplayTests(unittest.TestCase):
    def assert_fixture_error(self, name: str, category: str) -> None:
        fixture = load_fixture(name)
        with self.assertRaises(ProgressValidationError) as context:
            replay(fixture["events"], TAXONOMY, CAPABILITIES)
        self.assertEqual(context.exception.category, category)

    def test_basic_comprehensive_attempt_and_zero_semantics(self) -> None:
        state = run_fixture("basic")
        self.assertEqual(state["global"], {
            "attempt_count": 1,
            "correct_count": 1,
            "incorrect_count": 0,
            "accuracy": 1.0,
        })
        self.assertEqual(state["topics"]["DATA.DATABASE.RELATIONAL"]["attempt_count"], 1)
        self.assertEqual(state["topics"]["DATA.DATABASE.RELATIONAL"]["accuracy"], 1.0)

        zero = run_fixture("zero")
        self.assertEqual(zero["global"]["attempt_count"], 0)
        self.assertIsNone(zero["global"]["accuracy"])
        self.assertIsNone(zero["topics"]["DATA.DATABASE.RELATIONAL"]["accuracy"])
        self.assertIsNone(zero["case"]["score_ratio"])
        self.assertIsNone(zero["errors"]["error_cause_mix"]["knowledge_gap"])

    def test_multi_topic_global_count_is_not_topic_sum(self) -> None:
        state = run_fixture("multi-topic")
        self.assertEqual(state["global"]["attempt_count"], 1)
        self.assertEqual(state["topics"]["DATA.CACHE"]["attempt_count"], 1)
        self.assertEqual(state["topics"]["DATA.DISTRIBUTED"]["attempt_count"], 1)
        self.assertNotEqual(
            state["global"]["attempt_count"],
            state["topics"]["DATA.CACHE"]["attempt_count"] + state["topics"]["DATA.DISTRIBUTED"]["attempt_count"],
        )
        self.assertEqual(state["coverage"]["l1"], {"covered": 1, "total": 13, "ratio": 0.0769})
        self.assertEqual(state["coverage"]["l2"]["covered"], 2)
        self.assertEqual(state["coverage"]["l3"]["covered"], 0)

    def test_case_score_uses_weighted_numerator_and_denominator(self) -> None:
        state = run_fixture("case-score")
        self.assertEqual(state["global"]["attempt_count"], 0)
        self.assertEqual(state["case"]["attempt_count"], 2)
        self.assertEqual(state["case"]["score_earned"], 7)
        self.assertEqual(state["case"]["score_possible"], 10)
        self.assertEqual(state["case"]["score_ratio"], 0.7)
        self.assertEqual(state["capabilities"]["CASE.DATA_DESIGN"]["score_ratio"], 0.7)
        self.assertEqual(state["capabilities"]["CASE.SOLUTION_TRADEOFF"]["score_ratio"], 0.6)
        self.assertEqual(
            state["capabilities"]["CASE.ARCHITECTURE_DESIGN"]["evidence_status"],
            "insufficient_evidence",
        )
        self.assertNotIn("capability_accuracy", state["capabilities"]["CASE.DATA_DESIGN"])

    def test_capability_reference_without_score_does_not_create_metric(self) -> None:
        state = run_fixture("case-no-capability-evidence")
        self.assertEqual(state["case"]["attempt_count"], 1)
        self.assertEqual(state["case"]["scored_attempt_count"], 0)
        self.assertIsNone(state["case"]["score_ratio"])
        for capability_id in ("CASE.ARCHITECTURE_SELECTION", "CASE.SOLUTION_TRADEOFF"):
            metric = state["capabilities"][capability_id]
            self.assertEqual(metric["attempt_count"], 0)
            self.assertIsNone(metric["score_ratio"])
            self.assertEqual(metric["evidence_status"], "insufficient_evidence")

    def test_error_cause_mix_excludes_unclassified_denominator(self) -> None:
        state = run_fixture("errors")
        self.assertEqual(state["errors"]["error_count"], 5)
        self.assertEqual(state["errors"]["classified_error_count"], 4)
        self.assertEqual(state["errors"]["unclassified_error_count"], 1)
        self.assertEqual(state["errors"]["error_count_by_cause"]["knowledge_gap"], 1)
        self.assertEqual(state["errors"]["error_cause_mix"]["knowledge_gap"], 0.25)
        self.assertEqual(sum(state["errors"]["error_cause_mix"].values()), 1.0)

    def test_study_minutes_are_measured_duration_only(self) -> None:
        state = run_fixture("study")
        self.assertEqual(state["study"], {"session_count": 2, "study_minutes": 75})
        self.assertEqual(state["global"]["attempt_count"], 0)
        self.assertEqual(state["coverage"]["l1"]["covered"], 0)

    def test_repeatability_and_input_order_independence(self) -> None:
        fixture = load_fixture("ordering")
        events = fixture["events"]
        state = replay(events, TAXONOMY, CAPABILITIES)
        self.assertEqual(state, replay(events, TAXONOMY, CAPABILITIES))
        shuffled = copy.deepcopy(events)
        random.Random(7).shuffle(shuffled)
        self.assertEqual(state, replay(shuffled, TAXONOMY, CAPABILITIES))
        self.assertEqual(state["global"]["accuracy"], 0.6667)

    def test_duplicate_event_id_is_rejected_not_deduplicated(self) -> None:
        self.assert_fixture_error("duplicate-event-id", "duplicate_event_id")

    def test_unknown_references_are_rejected(self) -> None:
        self.assert_fixture_error("unknown-topic", "unknown_topic_id")
        self.assert_fixture_error("unknown-capability", "unknown_capability_id")

    def test_score_timestamp_path_and_error_validation(self) -> None:
        self.assert_fixture_error("invalid-score", "invalid_score")
        self.assert_fixture_error("naive-timestamp", "invalid_timestamp")
        self.assert_fixture_error("source-path-traversal", "forbidden_path")
        self.assert_fixture_error("invalid-error-cause", "invalid_event")

        fixture = load_fixture("basic")
        fixture["events"][0]["question"]["source_path"] = str(ROOT / "temporary-absolute.json")
        with self.assertRaises(ProgressValidationError) as context:
            replay(fixture["events"], TAXONOMY, CAPABILITIES)
        self.assertEqual(context.exception.category, "forbidden_path")

    def test_state_does_not_implement_future_policy(self) -> None:
        state = run_fixture("case-score")
        serialized = json.dumps(state, ensure_ascii=False).lower()
        for forbidden in ("mastery", "review_due", "review_interval", "sm-2", "fsrs", "planner"):
            self.assertNotIn(forbidden, serialized)


if __name__ == "__main__":
    unittest.main()
