"""P4.6/P4.7 frozen Review fixture replay and edge-case tests."""
from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
import unittest

from engine.review import (
    EVIDENCE_STATUSES,
    IDENTITY_NAMESPACE,
    ITEM_SCHEMA_VERSION,
    REVIEW_EVENT_SCHEMA_VERSION,
    REVIEW_ITEM_KINDS,
    replay,
)
from reviewkit import (
    assert_expected_projection,
    assert_review_replay_properties,
    fixture_cases,
    load_fixture_plan,
    load_fixture_schema,
    load_json,
    load_review_fixture,
    validate_mastery_review_state,
)

ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = ROOT / "data/review/fixtures"
TAXONOMY = load_json(ROOT / "taxonomy/taxonomy.json")
CAPABILITIES = load_json(ROOT / "taxonomy/capabilities.json")
FIXTURE_SCHEMA = load_fixture_schema(ROOT)
STATE_SCHEMA = load_json(ROOT / "data/review/mastery-review-state.schema.json")
PLAN = load_fixture_plan(ROOT)
POLICIES = {
    "mastery": "mastery-policy/spaced-consecutive/v0.1",
    "review": "review-policy/simple-ladder/v0.1",
    "outcome_adapter": "review-outcome/raw-facts/v0.1",
}


def run_case(fixture, case):
    return replay(
        case["input"]["progress_events"],
        case["input"]["review_events"],
        case["input"]["items"],
        TAXONOMY,
        CAPABILITIES,
        as_of=case["as_of"],
        timezone=case["timezone"],
        mastery_policy=fixture["policies"]["mastery"],
        review_policy=fixture["policies"]["review"],
    )


def load_fixture(fixture_id):
    return load_review_fixture(FIXTURE_DIR / f"{fixture_id}.json", schema=FIXTURE_SCHEMA)


def only_item(value):
    if isinstance(value, Mapping):
        items = value.get("items", value)
        return next(iter(items.values()))
    return next(iter(value))


def expected_state(fixture_id, variant_id="base"):
    fixture = load_fixture(fixture_id)
    case = next(c for c in fixture_cases(fixture) if c["case_id"] == variant_id)
    return case["expected"]


class ManifestContractSyncTests(unittest.TestCase):
    def test_frozen_model_evidence_and_replay_symbols_match_public_contract(self) -> None:
        symbols = PLAN["policy_symbols"]
        self.assertEqual(symbols["REVIEW_ITEM_ID_NAMESPACE"]["value"]["namespace"], IDENTITY_NAMESPACE)
        self.assertEqual(symbols["REVIEW_ITEM_KIND_ENUM"]["value"], list(REVIEW_ITEM_KINDS))
        self.assertEqual(symbols["REVIEW_EVENT_TYPE"]["value"]["schema_version"], REVIEW_EVENT_SCHEMA_VERSION)
        self.assertEqual(symbols["EVIDENCE_SUFFICIENCY_RULE"]["value"]["statuses"], list(EVIDENCE_STATUSES))
        self.assertEqual(symbols["SUCCESS_DERIVATION_CASE_SCORE"]["value"]["supported_score"], "insufficient")
        self.assertEqual(symbols["SUCCESS_DERIVATION_CAPABILITY"]["value"]["supported_capability_score"], "insufficient")
        self.assertEqual(symbols["REPLAY_FUTURE_EVIDENCE_POLICY"]["value"]["policy"], "reject")
        self.assertEqual(symbols["REPLAY_TIE_BREAKER"]["value"]["key"], ["occurred_at_utc", "evidence_id"])
        state = replay([], [], [], TAXONOMY, CAPABILITIES, as_of="2026-01-01T00:00:00Z", timezone="UTC")
        for field in symbols["REPLAY_OUTPUT_VERSION_FIELDS"]["value"]:
            self.assertIn(field, state)
        self.assertEqual(ITEM_SCHEMA_VERSION, "review-item/v0.1")


class FrozenFixtureReplayTests(unittest.TestCase):
    def test_every_ready_fixture_replays_expected_state_or_category(self) -> None:
        entries = [e for e in PLAN["fixtures"] if e["implementation"] == "fixture"]
        self.assertEqual(len(entries), PLAN["p4_6"]["synthetic_fixtures"])
        for entry in entries:
            fixture = load_fixture(entry["fixture_id"])
            self.assertEqual(fixture["policy_symbols"], entry["policy_symbols"])
            for case in fixture_cases(fixture):
                label = f"{entry['fixture_id']}[{case['case_id']}]"
                if case["expected_error"] is not None:
                    with self.subTest(case=label):
                        with self.assertRaises(Exception) as caught:
                            run_case(fixture, case)
                        self.assertEqual(getattr(caught.exception, "category", None), case["expected_error"])
                    continue
                with self.subTest(case=label):
                    state = run_case(fixture, case)
                    validate_mastery_review_state(
                        state,
                        as_of=case["as_of"],
                        timezone_name=case["timezone"],
                        state_schema=STATE_SCHEMA,
                    )
                    assert_expected_projection(state, case["expected"], label)
                    assert_review_replay_properties(
                        replay,
                        case["input"],
                        as_of=case["as_of"],
                        timezone_name=case["timezone"],
                        policies=fixture["policies"],
                        taxonomy=TAXONOMY,
                        capabilities=CAPABILITIES,
                        label=label,
                    )

    def test_no_evidence_is_not_failure_or_zero(self) -> None:
        fixture = load_fixture("mastery-new-item")
        state = run_case(fixture, fixture_cases(fixture)[0])
        item = only_item(state)
        self.assertEqual(item["mastery_state"], "new")
        self.assertEqual(item["review_status"], "not_scheduled")
        self.assertEqual(item["evaluated_evidence_count"], 0)
        self.assertEqual(item["failure_count"], 0)
        self.assertEqual(item["insufficient_evidence_count"], 0)
        self.assertIsNone(item["next_due_at"])
        self.assertEqual(state["review"]["due_count"], 0)

    def test_frozen_success_ladder_and_mastered_maintenance(self) -> None:
        expected = {
            "mastery-first-success": (1, "learning", 1),
            "mastery-repeated-success": (3, "learning", 2),
            "mastery-mastered": (7, "mastered", 3),
            "mastery-mastered-success": (15, "mastered", 4),
        }
        for fixture_id, (interval, mastery, day_count) in expected.items():
            with self.subTest(fixture=fixture_id):
                item = only_item(expected_state(fixture_id)["items"])
                self.assertEqual(item["review_interval_days"], interval)
                self.assertEqual(item["mastery_state"], mastery)
                self.assertEqual(item["consecutive_success_day_count"], day_count)
        maintenance = only_item(expected_state("mastery-mastered-success")["items"])
        self.assertEqual(maintenance["mastery_reason"], "mastered_success_maintenance")

    def test_failure_from_new_learning_and_mastered_resets_counters_and_schedule(self) -> None:
        first = only_item(expected_state("mastery-first-failure")["items"])
        learning = only_item(expected_state("mastery-learning-failure")["items"])
        mastered = only_item(expected_state("mastery-mastered-failure")["items"])
        for item in (first, learning, mastered):
            self.assertEqual(item["mastery_state"], "learning")
            self.assertEqual(item["failure_count"], 1)
            self.assertEqual(item["consecutive_success_count"], 0)
            self.assertEqual(item["consecutive_success_day_count"], 0)
            self.assertEqual(item["review_interval_days"], 1)
            self.assertEqual(item["scheduling_reason"], "failure_schedules_retry_interval")
        self.assertEqual(first["mastery_reason"], "failure_enters_learning")
        self.assertEqual(learning["mastery_reason"], "learning_failure_keeps_learning")
        self.assertEqual(mastered["mastery_reason"], "mastered_failure_demotes_learning")

    def test_same_day_repeat_counts_attempt_without_advancing_ladder(self) -> None:
        item = only_item(expected_state("mastery-same-day-repeat")["items"])
        self.assertEqual(item["successful_review_count"], 2)
        self.assertEqual(item["consecutive_success_count"], 2)
        self.assertEqual(item["consecutive_success_day_count"], 1)
        self.assertEqual(item["review_interval_days"], 1)
        self.assertEqual(item["scheduling_reason"], "same_day_success_keeps_schedule")

    def test_due_calendar_boundaries_are_inclusive_and_local_date_based(self) -> None:
        fixture = load_fixture("sched-before-due")
        states = {case["case_id"]: run_case(fixture, case) for case in fixture_cases(fixture)}
        self.assertEqual(only_item(states["base"]["items"].values())["review_status"], "scheduled")
        self.assertEqual(only_item(states["exact-due"]["items"].values())["review_status"], "due")
        self.assertEqual(only_item(states["one-microsecond-after"]["items"].values())["review_status"], "due")
        self.assertEqual(only_item(states["local-day-end"]["items"].values())["review_status"], "due")
        self.assertEqual(only_item(states["overdue-at-local-midnight"]["items"].values())["review_status"], "overdue")

    def test_timezone_rollover_and_dst_gap_follow_explicit_iana_calendar(self) -> None:
        fixture = load_fixture("time-local-date-boundary")
        cases = {case["case_id"]: case for case in fixture_cases(fixture)}
        shanghai = run_case(fixture, cases["base"])
        berlin = run_case(fixture, cases["Europe-Berlin"])
        self.assertEqual(only_item(shanghai["items"].values())["review_status"], "scheduled")
        self.assertEqual(only_item(berlin["items"].values())["review_status"], "due")
        self.assertNotEqual(
            only_item(shanghai["items"].values())["next_due_local_date"],
            only_item(berlin["items"].values())["next_due_local_date"],
        )
        dst_item = only_item(expected_state("time-dst-sensitive")["items"])
        self.assertEqual(dst_item["next_due_local_date"], "2019-09-08")
        self.assertEqual(dst_item["next_due_at"], "2019-09-08T04:00:00+00:00")

    def test_score_zero_and_high_remain_insufficient_not_failure(self) -> None:
        for fixture_id, earned in (("evidence-zero-score", 0), ("evidence-case-score", 7), ("evidence-case-score-high", 10)):
            with self.subTest(fixture=fixture_id):
                item = only_item(expected_state(fixture_id)["items"])
                trace = item["evidence"][0]
                self.assertEqual(trace["evidence_value"]["score_earned"], earned)
                self.assertEqual(trace["policy_outcome"], "insufficient")
                self.assertEqual(trace["policy_outcome_reason"], "score_outcome_mapping_unfrozen")
                self.assertEqual(item["mastery_state"], "new")
                self.assertEqual(item["failure_count"], 0)
                self.assertEqual(item["insufficient_evidence_count"], 1)
        failure = only_item(expected_state("mastery-first-failure")["items"])
        self.assertEqual(failure["evidence"][0]["policy_outcome"], "failure")
        self.assertEqual(failure["failure_count"], 1)

    def test_item_and_aggregate_counts_are_consistent(self) -> None:
        expected = expected_state("sched-due-count-consistency")
        self.assertEqual(expected["review"]["due_today_count"], 1)
        self.assertEqual(expected["review"]["overdue_count"], 1)
        self.assertEqual(expected["review"]["due_count"], 2)
        self.assertEqual(
            expected["review"]["due_count"],
            sum(item["review_status"] in {"due", "overdue"} for item in expected["items"].values()),
        )
        self.assertEqual(expected["mastery"], {"new_count": 1, "learning_count": 3, "mastered_count": 0})

    def test_same_timestamp_tie_break_is_stable_by_evidence_identity(self) -> None:
        item = only_item(expected_state("determinism-same-timestamp-ordering")["items"])
        self.assertEqual([trace["source_event_id"] for trace in item["evidence"]], ["attempt-a", "attempt-b"])
        self.assertEqual(item["last_evidence_id"].split("/")[1], "attempt-b")
        self.assertEqual(item["mastery_reason"], "learning_failure_keeps_learning")

    def test_invalid_fixtures_use_frozen_rejection_categories(self) -> None:
        expected = {
            "invalid-duplicate-event-id": "duplicate_event_id",
            "invalid-duplicate-item": "duplicate_review_item",
            "invalid-duplicate-review-context": "duplicate_review_context",
            "invalid-unknown-review-item": "unknown_review_item",
            "invalid-unknown-topic": "unknown_topic_id",
            "invalid-unknown-capability": "unknown_capability_id",
            "invalid-naive-timestamp": "invalid_timestamp",
            "invalid-timezone": "invalid_timezone",
            "invalid-future-evidence": "future_evidence",
            "invalid-source-event-mismatch": "source_timestamp_mismatch",
            "invalid-evidence-kind-mismatch": "evidence_item_mismatch",
            "invalid-malformed-review-item": "invalid_review_contract",
            "invalid-missing-source-reference": "missing_source_reference",
            "invalid-source-reference": "invalid_source_reference",
            "invalid-illegal-source-path": "forbidden_path",
        }
        for fixture_id, category in expected.items():
            with self.subTest(fixture=fixture_id):
                fixture = load_fixture(fixture_id)
                self.assertEqual(fixture["expected_error"], category)

    def test_runtime_policy_parameters_are_not_injected_into_v01(self) -> None:
        fixture = load_fixture("mastery-new-item")
        item = fixture["input"]["items"][0]
        with self.assertRaises(Exception) as raised:
            replay(
                [], [], [item], TAXONOMY, CAPABILITIES,
                as_of=fixture["as_of"], timezone=fixture["timezone"],
                review_policy={
                    "policy_id": "review-policy/simple-ladder",
                    "policy_version": "v0.1",
                    "interval_ladder_days": [1, -1],
                },
            )
        self.assertEqual(getattr(raised.exception, "category", None), "invalid_policy_input")


if __name__ == "__main__":
    unittest.main()
