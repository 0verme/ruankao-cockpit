"""P4.6 fixture-plan / draft-schema integrity tests.

这些测试不验证 mastery / scheduling 业务规则，只保证：

* fixture plan 与设计文档、骨架模块、盘上文件互相一致；
* policy-dependent 的 expected 值不会被提前写死；
* draft fixture schema 保持 draft 状态，并覆盖 as_of / timezone / 拒绝语义；
* backward-compatibility 清单与 Phase 3 现有 fixture 完全对齐。
"""
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
    load_fixture_schema_draft,
    load_json,
    load_review_fixture,
    validate_fixture_plan,
    validate_review_fixture_shape,
)

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_POLICY_SYMBOLS = (
    "REVIEW_ITEM_ID_NAMESPACE",
    "REVIEW_ITEM_ALIAS_RULE",
    "REVIEW_EVIDENCE_SOURCE",
    "SUCCESS_DERIVATION_CAPABILITY",
    "EVIDENCE_SUFFICIENCY_RULE",
    "MASTERY_STATE_ENUM",
    "MASTERY_FAILURE_TRANSITION",
    "MASTERY_MASTERED_FAILURE_TRANSITION",
    "SCHED_INTERVAL_LADDER",
    "SCHED_FAILURE_RESET_RULE",
    "SCHED_DUE_COUNT_DEFINITION",
    "SCHED_DATE_BOUNDARY_TIMEZONE",
    "REPLAY_TIE_BREAKER",
    "REPLAY_FUTURE_EVIDENCE_POLICY",
    "STATE_ERROR_CATEGORIES",
)

MATRIX_SECTIONS = tuple("ABCDEFGHI")

VALID_FIXTURE = {
    "schema_version": FIXTURE_SCHEMA_VERSION,
    "fixture_id": "mastery-first-success",
    "description": "loader-only placeholder, not a policy claim",
    "as_of": "2026-01-02T00:00:00Z",
    "timezone": "UTC",
    "events": [{"event_id": "evt-1", "occurred_at": "2026-01-01T00:00:00Z"}],
    "expected": {"state": "PLACEHOLDER_FOR_LOADER_TEST"},
}


class FixturePlanIntegrityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.plan = load_fixture_plan(ROOT)
        cls.schema = load_fixture_schema_draft(ROOT)

    def test_fixture_plan_is_consistent_with_skeletons_and_disk(self) -> None:
        self.assertEqual(validate_fixture_plan(self.plan, ROOT), [])

    def test_every_matrix_ref_is_documented(self) -> None:
        doc = ROOT / "docs/PHASE4_TEST_MATRIX.md"
        self.assertTrue(doc.is_file(), "docs/PHASE4_TEST_MATRIX.md is required")
        self.assertEqual(cross_check_matrix_refs(self.plan, doc.read_text(encoding="utf-8")), [])

    def test_every_matrix_section_has_at_least_one_entry(self) -> None:
        covered = {
            ref[0]
            for entry in self.plan["fixtures"]
            for ref in entry["matrix_refs"]
        }
        self.assertEqual(sorted(covered), list(MATRIX_SECTIONS))

    def test_implementation_mix_covers_fixture_harness_static_regression(self) -> None:
        implementations = {entry["implementation"] for entry in self.plan["fixtures"]}
        self.assertEqual(implementations, {"fixture", "harness", "static", "regression"})

    def test_invalid_prefix_carries_rejection_matrix(self) -> None:
        invalid_entries = [entry for entry in self.plan["fixtures"] if entry["fixture_id"].startswith("invalid-")]
        self.assertTrue(invalid_entries)
        for entry in invalid_entries:
            with self.subTest(fixture=entry["fixture_id"]):
                self.assertEqual(entry["expected_kind"], "error")
                self.assertTrue(entry["matrix_refs"])

    def test_policy_dependent_entries_are_traceable_to_symbols(self) -> None:
        symbols = self.plan["policy_symbols"]
        for entry in self.plan["fixtures"]:
            if entry["contract_independence"] != "policy_dependent":
                continue
            with self.subTest(fixture=entry["fixture_id"]):
                self.assertTrue(entry["policy_symbols"], "policy-dependent entry needs symbols")
                for name in entry["policy_symbols"]:
                    self.assertIn(name, symbols)
                self.assertTrue(entry["blocked_by"], "policy-dependent entry needs an owner")

    def test_required_contract_gap_symbols_are_registered(self) -> None:
        symbols = self.plan["policy_symbols"]
        for name in REQUIRED_POLICY_SYMBOLS:
            with self.subTest(symbol=name):
                self.assertIn(name, symbols)
                self.assertIn(symbols[name]["owner"], {"P4.1", "P4.2", "P4.3", "P4.4", "P4.5"})

    def test_unfrozen_symbols_carry_no_values(self) -> None:
        for name, symbol in self.plan["policy_symbols"].items():
            with self.subTest(symbol=name):
                if symbol["status"] == "unfrozen":
                    self.assertIsNone(symbol["value"])
                    self.assertIsNone(symbol["frozen_by"])
                else:
                    self.assertIsNotNone(symbol["value"])
                    self.assertIsNotNone(symbol["frozen_by"])

    def test_planned_fixtures_are_not_faked_on_disk(self) -> None:
        fixture_dir = ROOT / self.plan["fixture_root"]
        shipped = {path.name for path in fixture_dir.glob("*.json")}
        planned = {
            entry["file"]
            for entry in self.plan["fixtures"]
            if entry["implementation"] == "fixture" and entry["status"] == "planned"
        }
        self.assertEqual(shipped & planned, set())

    def test_shipped_fixtures_load_and_declare_expectations(self) -> None:
        fixture_dir = ROOT / self.plan["fixture_root"]
        for path in sorted(fixture_dir.glob("*.json")):
            with self.subTest(fixture=path.name):
                fixture = load_review_fixture(path)
                self.assertTrue("expected" in fixture or "expected_error" in fixture)

    def test_backward_compatibility_section_matches_progress_fixtures(self) -> None:
        compat = self.plan["backward_compatibility"]
        progress_dir = ROOT / compat["progress_fixture_root"]
        valid: set[str] = set()
        rejected: set[str] = set()
        for path in sorted(progress_dir.glob("*.json")):
            data = load_json(path)
            (rejected if "expected_error" in data else valid).add(data["fixture_id"])
        self.assertEqual(sorted(valid), sorted(compat["progress_valid_replay"]))
        self.assertEqual(sorted(rejected), sorted(compat["progress_expected_rejections"]))

    def test_review_fixtures_are_separate_from_progress_fixtures(self) -> None:
        self.assertEqual(self.plan["fixture_root"], "data/review/fixtures")
        review_dir = ROOT / self.plan["fixture_root"]
        self.assertNotEqual(review_dir, ROOT / "data/progress/fixtures")


class DraftSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.schema = load_fixture_schema_draft(ROOT)

    def test_draft_schema_is_marked_draft(self) -> None:
        self.assertEqual(self.schema["status"], "draft")
        self.assertFalse(self.schema["frozen"])
        self.assertEqual(self.schema["schema_version"], FIXTURE_SCHEMA_VERSION)
        self.assertTrue(any("P4.1" in dependency for dependency in self.schema["depends_on"]))
        self.assertTrue(any("P4.2" in dependency for dependency in self.schema["depends_on"]))

    def test_draft_schema_requires_time_and_identity(self) -> None:
        for field in ("fixture_id", "as_of", "timezone", "description"):
            self.assertIn(field, self.schema["required"])
        self.assertIn("expected", self.schema["expected_alternatives"])
        self.assertIn("expected_error", self.schema["expected_alternatives"])

    def test_draft_schema_keeps_contract_values_out(self) -> None:
        serialized = json.dumps(self.schema, ensure_ascii=False)
        self.assertNotIn("1/3/7/15", serialized)
        self.assertIn("review_item_id 最终格式", self.schema["out_of_scope"])


class FixtureLoaderTests(unittest.TestCase):
    def test_valid_fixture_shape_passes(self) -> None:
        validate_review_fixture_shape(VALID_FIXTURE, "valid.json")

    def test_loader_rejects_missing_as_of(self) -> None:
        broken = dict(VALID_FIXTURE)
        broken.pop("as_of")
        with self.assertRaises(FixtureContractError):
            validate_review_fixture_shape(broken, "no-as-of.json")

    def test_loader_rejects_naive_timestamp(self) -> None:
        broken = dict(VALID_FIXTURE, as_of="2026-01-02T00:00:00")
        with self.assertRaises(FixtureContractError):
            validate_review_fixture_shape(broken, "naive.json")

    def test_loader_rejects_conflicting_expectations(self) -> None:
        broken = dict(VALID_FIXTURE, expected_error="unknown_review_item")
        with self.assertRaises(FixtureContractError):
            validate_review_fixture_shape(broken, "conflict.json")

    def test_loader_requires_expectation_for_shipped_fixtures(self) -> None:
        pending = dict(VALID_FIXTURE)
        pending.pop("expected")
        with self.assertRaises(FixtureContractError):
            validate_review_fixture_shape(pending, "pending.json")
        validate_review_fixture_shape(pending, "pending.json", require_expectation=False)

    def test_loader_rejects_third_party_content(self) -> None:
        broken = dict(VALID_FIXTURE, answer="<third-party analysis>")
        with self.assertRaises(FixtureContractError):
            validate_review_fixture_shape(broken, "content.json")

    def test_loader_validates_variants(self) -> None:
        with_variant = dict(
            VALID_FIXTURE,
            variants=[{"variant_id": "before-due", "as_of": "2026-01-01T00:00:00Z", "expected_error": "not_due"}],
        )
        validate_review_fixture_shape(with_variant, "variants.json")
        broken = dict(VALID_FIXTURE, variants=[{"variant_id": "naive", "as_of": "2026-01-01T00:00:00"}])
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
