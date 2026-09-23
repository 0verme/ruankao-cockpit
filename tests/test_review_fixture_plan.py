"""P4.6 frozen fixture contract and plan integrity tests."""
from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from reviewkit import (
    FIXTURE_SCHEMA_VERSION,
    FixtureContractError,
    cross_check_matrix_refs,
    load_fixture_plan,
    load_fixture_schema,
    load_json,
    load_review_fixture,
    validate_fixture_plan,
    validate_review_fixture_shape,
)

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_POLICY_SYMBOLS = (
    "REVIEW_ITEM_ID_NAMESPACE", "REVIEW_ITEM_KIND_ENUM", "REVIEW_ITEM_REGISTRY",
    "REVIEW_ITEM_ALIAS_RULE", "REVIEW_EVIDENCE_SOURCE", "REVIEW_EVENT_TYPE",
    "EVIDENCE_SUFFICIENCY_RULE", "SUCCESS_DERIVATION_COMPREHENSIVE",
    "SUCCESS_DERIVATION_CASE_SCORE", "SUCCESS_DERIVATION_CAPABILITY", "EVIDENCE_DEDUP_RULE",
    "MASTERY_STATE_ENUM", "MASTERY_FAILURE_TRANSITION", "SCHED_INTERVAL_LADDER",
    "SCHED_FAILURE_RESET_RULE", "SCHED_DUE_COUNT_DEFINITION", "SCHED_DATE_BOUNDARY_TIMEZONE",
    "REPLAY_AS_OF_PARAMETER", "REPLAY_TIE_BREAKER", "REPLAY_FUTURE_EVIDENCE_POLICY",
    "REPLAY_OUTPUT_VERSION_FIELDS", "STATE_ERROR_CATEGORIES",
)
MATRIX_SECTIONS = tuple("ABCDEFGHI")
VALID_FIXTURE = {
    "schema_version": FIXTURE_SCHEMA_VERSION,
    "fixture_id": "mastery-first-success",
    "description": "synthetic loader test",
    "as_of": "2026-01-02T00:00:00Z",
    "timezone": "UTC",
    "policies": {
        "mastery": "mastery-policy/spaced-consecutive/v0.1",
        "review": "review-policy/simple-ladder/v0.1",
        "outcome_adapter": "review-outcome/raw-facts/v0.1",
    },
    "contract_refs": ["docs/review/MASTERY_POLICY_V01.md"],
    "input": {"progress_events": [], "review_events": [], "items": []},
    "expected": {"schema_version": "mastery-review-state/v0.1"},
}


class FixturePlanIntegrityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.plan = load_fixture_plan(ROOT)
        cls.schema = load_fixture_schema(ROOT)

    def test_fixture_plan_matches_skeletons_and_disk(self) -> None:
        self.assertEqual(validate_fixture_plan(self.plan, ROOT), [])

    def test_p4_6_schema_is_frozen_without_checking_future_gates(self) -> None:
        self.assertEqual(self.plan["p4_6"]["status"], "FROZEN")
        self.assertEqual(self.plan["p4_6"]["fixture_schema"], FIXTURE_SCHEMA_VERSION)
        self.assertEqual(self.plan["p4_7"]["status"], "COMPLETE")
        for phase in ("p4_8", "p4_9"):
            if phase in self.plan:
                self.assertNotIn(self.plan[phase].get("status"), {"COMPLETE", "FROZEN", "PASS"})

    def test_every_matrix_ref_is_documented(self) -> None:
        doc = ROOT / "docs/PHASE4_TEST_MATRIX.md"
        self.assertTrue(doc.is_file())
        self.assertEqual(cross_check_matrix_refs(self.plan, doc.read_text(encoding="utf-8")), [])

    def test_every_matrix_section_has_coverage(self) -> None:
        covered = {ref[0] for entry in self.plan["fixtures"] for ref in entry["matrix_refs"]}
        self.assertEqual(sorted(covered), list(MATRIX_SECTIONS))

    def test_implementation_mix_covers_fixture_harness_static_regression(self) -> None:
        self.assertEqual(
            {entry["implementation"] for entry in self.plan["fixtures"]},
            {"fixture", "harness", "static", "regression"},
        )

    def test_invalid_entries_declare_rejection_targets(self) -> None:
        invalid_entries = [e for e in self.plan["fixtures"] if e["fixture_id"].startswith("invalid-")]
        self.assertTrue(invalid_entries)
        for entry in invalid_entries:
            with self.subTest(fixture=entry["fixture_id"]):
                self.assertEqual(entry["expected_kind"], "error")
                self.assertTrue(entry["matrix_refs"])

    def test_policy_dependent_entries_reference_frozen_contracts(self) -> None:
        symbols = self.plan["policy_symbols"]
        for entry in self.plan["fixtures"]:
            if entry["contract_independence"] != "policy_dependent":
                continue
            with self.subTest(fixture=entry["fixture_id"]):
                self.assertTrue(entry["policy_symbols"])
                self.assertTrue(entry["contract_refs"])
                self.assertEqual(entry["blocked_by"], [])
                for name in entry["policy_symbols"]:
                    self.assertEqual(symbols[name]["status"], "frozen")

    def test_required_symbols_are_frozen_and_traceable(self) -> None:
        symbols = self.plan["policy_symbols"]
        for name in REQUIRED_POLICY_SYMBOLS:
            with self.subTest(symbol=name):
                self.assertIn(name, symbols)
                self.assertEqual(symbols[name]["status"], "frozen")
                self.assertIsNotNone(symbols[name]["value"])
                self.assertIsNotNone(symbols[name]["frozen_by"])

    def test_all_fixture_files_match_manifest_without_pending_entries(self) -> None:
        fixture_dir = ROOT / self.plan["fixture_root"]
        shipped = {p.name for p in fixture_dir.glob("*.json")}
        declared = {
            e["file"] for e in self.plan["fixtures"]
            if e["implementation"] == "fixture" and e["status"] == "ready"
        }
        self.assertEqual(shipped, declared)
        self.assertFalse(any(e["status"] == "planned" for e in self.plan["fixtures"]))

    def test_shipped_fixtures_load_with_expectations(self) -> None:
        fixture_dir = ROOT / self.plan["fixture_root"]
        for path in sorted(fixture_dir.glob("*.json")):
            with self.subTest(fixture=path.name):
                fixture = load_review_fixture(path)
                self.assertTrue("expected" in fixture or "expected_error" in fixture)

    def test_progress_compatibility_inventory_matches_frozen_fixtures(self) -> None:
        compat = self.plan["backward_compatibility"]
        progress_dir = ROOT / compat["progress_fixture_root"]
        valid, rejected = set(), set()
        for path in progress_dir.glob("*.json"):
            data = load_json(path)
            (rejected if "expected_error" in data else valid).add(data["fixture_id"])
        self.assertEqual(sorted(valid), sorted(compat["progress_valid_replay"]))
        self.assertEqual(sorted(rejected), sorted(compat["progress_expected_rejections"]))

    def test_review_fixture_root_stays_separate_from_progress(self) -> None:
        self.assertEqual(self.plan["fixture_root"], "data/review/fixtures")
        self.assertNotEqual(ROOT / self.plan["fixture_root"], ROOT / "data/progress/fixtures")


class FrozenFixtureSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.schema = load_fixture_schema(ROOT)

    def test_schema_is_versioned_and_frozen(self) -> None:
        self.assertEqual(self.schema["title"], "Mastery / Review Fixture v0.1")
        self.assertEqual(self.schema["status"], "FROZEN")
        self.assertTrue(self.schema["frozen"])
        self.assertEqual(self.schema["schema_version"], FIXTURE_SCHEMA_VERSION)
        self.assertEqual(self.schema["owner"], "P4.6")

    def test_schema_requires_time_policy_provenance_and_replay_inputs(self) -> None:
        for field in ("fixture_id", "as_of", "timezone", "description", "policies", "contract_refs", "input"):
            self.assertIn(field, self.schema["required"])
        for field in ("expected", "expected_error", "variants"):
            self.assertIn(field, self.schema["properties"])

    def test_schema_does_not_duplicate_policy_parameters(self) -> None:
        serialized = json.dumps(self.schema, ensure_ascii=False)
        self.assertNotIn("interval_ladder_days", serialized)
        self.assertNotIn("MASTERY_MIN_DISTINCT_SUCCESS_DAYS", serialized)


class FixtureLoaderTests(unittest.TestCase):
    def test_valid_fixture_shape_passes(self) -> None:
        validate_review_fixture_shape(VALID_FIXTURE, "valid.json")

    def test_loader_requires_as_of_and_rejects_naive_as_of(self) -> None:
        missing = dict(VALID_FIXTURE)
        missing.pop("as_of")
        with self.assertRaises(FixtureContractError):
            validate_review_fixture_shape(missing, "missing-as-of.json")
        naive = dict(VALID_FIXTURE, as_of="2026-01-02T00:00:00")
        with self.assertRaises(FixtureContractError):
            validate_review_fixture_shape(naive, "naive-as-of.json")

    def test_loader_rejects_conflicting_or_missing_expectations(self) -> None:
        conflict = dict(VALID_FIXTURE, expected_error="unknown_review_item")
        with self.assertRaises(FixtureContractError):
            validate_review_fixture_shape(conflict, "conflict.json")
        pending = dict(VALID_FIXTURE)
        pending.pop("expected")
        with self.assertRaises(FixtureContractError):
            validate_review_fixture_shape(pending, "pending.json", require_expectation=False)

    def test_loader_rejects_third_party_content(self) -> None:
        broken = dict(VALID_FIXTURE, answer="third-party analysis")
        with self.assertRaises(FixtureContractError):
            validate_review_fixture_shape(broken, "content.json")

    def test_loader_validates_variant_shape_and_expectation(self) -> None:
        variant = dict(VALID_FIXTURE, variants=[{
            "variant_id": "exact-due", "as_of": "2026-01-02T00:00:00Z",
            "expected": {"review": {"due_count": 1}},
        }])
        validate_review_fixture_shape(variant, "variants.json")
        broken = dict(VALID_FIXTURE, variants=[{"variant_id": "naive", "as_of": "2026-01-02T00:00:00"}])
        with self.assertRaises(FixtureContractError):
            validate_review_fixture_shape(broken, "variants.json")

    def test_file_backed_loader_requires_matching_fixture_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "different-name.json"
            path.write_text(json.dumps(VALID_FIXTURE, ensure_ascii=False), encoding="utf-8")
            with self.assertRaises(FixtureContractError):
                load_review_fixture(path)


if __name__ == "__main__":
    unittest.main()
