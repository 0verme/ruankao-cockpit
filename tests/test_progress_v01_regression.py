"""Phase 4 不得使 Progress Replay v0.1 语义漂移 —— 冻结回归矩阵。

基线文件：`tests/baselines/progress_v01_semantics.json`

* 每个合法 fixture 记录 canonical digest + 人类可读的语义 projection；
* 每个拒绝 fixture 记录 validation category；
* projection 会剔除默认 topic/capability 模板，并单独断言被剔除项确实等于默认值，
  因此 digest + projection 组合是无损的。

重新生成基线（只在确认语义变更经过评审后使用）：

```bash
REGEN_PROGRESS_BASELINE=1 python3 -m unittest discover -s tests -p 'test_progress_v01_regression.py'
```
"""
from __future__ import annotations

import copy
import json
import os
from pathlib import Path
import random
import subprocess
import sys
import unittest

from engine.progress import ProgressValidationError, replay
from reviewkit import canonical_json, state_digest

ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = ROOT / "data/progress/fixtures"
BASELINE_PATH = ROOT / "tests/baselines/progress_v01_semantics.json"
TAXONOMY = json.loads((ROOT / "taxonomy/taxonomy.json").read_text(encoding="utf-8"))
CAPABILITIES = json.loads((ROOT / "taxonomy/capabilities.json").read_text(encoding="utf-8"))

BASELINE_VERSION = "progress-v01-semantics-baseline/v0.1"
SHUFFLE_SEEDS = (0, 7, 20260921)

SCALAR_SECTIONS = (
    "schema_version",
    "replay_rule_version",
    "event_schema_version",
    "taxonomy_version",
    "capability_version",
    "replayed_event_count",
    "global",
    "case",
    "errors",
    "coverage",
    "study",
)
DEFAULT_TOPIC = {"attempt_count": 0, "correct_count": 0, "incorrect_count": 0, "accuracy": None}
DEFAULT_CAPABILITY = {
    "attempt_count": 0,
    "score_earned": 0,
    "score_possible": 0,
    "score_ratio": None,
    "evidence_status": "insufficient_evidence",
}
PHASE4_KEYS = {
    "mastery",
    "mastered",
    "mastery_state",
    "review_due",
    "review_due_at",
    "review_interval",
    "review_interval_days",
    "review_item",
    "review_item_id",
    "due_count",
    "due_projection",
    "forgetting_curve",
    "sm2",
    "fsrs",
    "planner",
}


def load_fixture(fixture_id: str) -> dict:
    return json.loads((FIXTURE_ROOT / f"{fixture_id}.json").read_text(encoding="utf-8"))


def fixture_ids() -> tuple[list[str], list[str]]:
    valid: list[str] = []
    rejected: list[str] = []
    for path in sorted(FIXTURE_ROOT.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        (rejected if "expected_error" in data else valid).append(data["fixture_id"])
    return valid, rejected


def project_progress_state(state: dict) -> dict:
    projection = {key: state[key] for key in SCALAR_SECTIONS}
    projection["topics"] = {key: value for key, value in state["topics"].items() if value != DEFAULT_TOPIC}
    projection["capabilities"] = {
        key: value for key, value in state["capabilities"].items() if value != DEFAULT_CAPABILITY
    }
    projection["default_topic_count"] = len(state["topics"]) - len(projection["topics"])
    projection["default_capability_count"] = len(state["capabilities"]) - len(projection["capabilities"])
    return projection


def walk_keys(value: object) -> set[str]:
    keys: set[str] = set()
    if isinstance(value, dict):
        for key, child in value.items():
            keys.add(key)
            keys |= walk_keys(child)
    elif isinstance(value, list):
        for child in value:
            keys |= walk_keys(child)
    return keys


def record_progress_semantics() -> dict:
    valid_ids, rejected_ids = fixture_ids()
    recorded: dict[str, dict] = {}
    for fixture_id in valid_ids:
        state = replay(load_fixture(fixture_id)["events"], TAXONOMY, CAPABILITIES)
        recorded[fixture_id] = {
            "kind": "state",
            "digest": state_digest(state),
            "projection": project_progress_state(state),
        }
    for fixture_id in rejected_ids:
        fixture = load_fixture(fixture_id)
        try:
            replay(fixture["events"], TAXONOMY, CAPABILITIES)
        except ProgressValidationError as exc:
            recorded[fixture_id] = {"kind": "error", "category": exc.category}
        else:  # pragma: no cover - guards accidental fixture edits
            raise AssertionError(f"{fixture_id}: expected rejection fixture replayed successfully")
    return {
        "baseline_version": BASELINE_VERSION,
        "progress_model_contract": "progress-model/v0.1",
        "recorded_from_commit": subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=False
        ).stdout.strip(),
        "instructions": (
            "Phase 4（Review / Mastery）不得改变 Progress Replay v0.1 语义。"
            "若本基线必须变更，说明 ProgressState 语义发生了有意变更，需要独立评审与版本升级。"
        ),
        "fixtures": recorded,
    }


class ProgressV01RegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8")) if BASELINE_PATH.is_file() else {}
        cls.valid_ids, cls.rejected_ids = fixture_ids()

    def require_baseline(self) -> dict:
        if not self.baseline:
            self.fail(
                "baseline missing: run REGEN_PROGRESS_BASELINE=1 "
                "python3 -m unittest discover -s tests -p 'test_progress_v01_regression.py'"
            )
        return self.baseline["fixtures"]

    def write_baseline(self) -> None:
        BASELINE_PATH.parent.mkdir(parents=True, exist_ok=True)
        BASELINE_PATH.write_text(
            json.dumps(record_progress_semantics(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

    @unittest.skipUnless(
        os.environ.get("REGEN_PROGRESS_BASELINE") == "1", "set REGEN_PROGRESS_BASELINE=1 to rewrite the baseline"
    )
    def test_regenerate_baseline(self) -> None:
        self.write_baseline()
        self.assertTrue(BASELINE_PATH.is_file())

    def test_baseline_covers_every_progress_fixture(self) -> None:
        fixtures = self.require_baseline()
        self.assertEqual(self.baseline["baseline_version"], BASELINE_VERSION)
        self.assertEqual(sorted(fixtures), sorted(self.valid_ids + self.rejected_ids))
        self.assertEqual(len(self.valid_ids), 9)
        self.assertEqual(len(self.rejected_ids), 7)

    def test_valid_fixtures_match_frozen_semantics(self) -> None:
        fixtures = self.require_baseline()
        for fixture_id in self.valid_ids:
            with self.subTest(fixture=fixture_id):
                expected = fixtures[fixture_id]
                self.assertEqual(expected["kind"], "state")
                events = load_fixture(fixture_id)["events"]
                state = replay(events, TAXONOMY, CAPABILITIES)
                self.assertEqual(state_digest(state), expected["digest"])
                self.assertEqual(canonical_json(project_progress_state(state)), canonical_json(expected["projection"]))
                self.assertEqual(state, replay(events, TAXONOMY, CAPABILITIES))
                for seed in SHUFFLE_SEEDS:
                    shuffled = copy.deepcopy(events)
                    random.Random(seed).shuffle(shuffled)
                    self.assertEqual(state, replay(shuffled, TAXONOMY, CAPABILITIES))

    def test_projection_is_lossless_for_default_metrics(self) -> None:
        for fixture_id in self.valid_ids:
            with self.subTest(fixture=fixture_id):
                state = replay(load_fixture(fixture_id)["events"], TAXONOMY, CAPABILITIES)
                projection = project_progress_state(state)
                for topic_id, metric in state["topics"].items():
                    if topic_id not in projection["topics"]:
                        self.assertEqual(metric, DEFAULT_TOPIC, f"{fixture_id}:{topic_id}")
                for capability_id, metric in state["capabilities"].items():
                    if capability_id not in projection["capabilities"]:
                        self.assertEqual(metric, DEFAULT_CAPABILITY, f"{fixture_id}:{capability_id}")

    def test_rejection_categories_match_frozen_semantics(self) -> None:
        fixtures = self.require_baseline()
        for fixture_id in self.rejected_ids:
            with self.subTest(fixture=fixture_id):
                expected = fixtures[fixture_id]
                self.assertEqual(expected["kind"], "error")
                fixture = load_fixture(fixture_id)
                with self.assertRaises(ProgressValidationError) as context:
                    replay(fixture["events"], TAXONOMY, CAPABILITIES)
                self.assertEqual(context.exception.category, expected["category"])
                self.assertEqual(fixture["expected_error"], expected["category"])

    def test_progress_state_stays_free_of_phase4_policy_fields(self) -> None:
        for fixture_id in self.valid_ids:
            with self.subTest(fixture=fixture_id):
                state = replay(load_fixture(fixture_id)["events"], TAXONOMY, CAPABILITIES)
                leaked = walk_keys(state) & PHASE4_KEYS
                self.assertEqual(leaked, set(), f"{fixture_id}: Phase 4 keys leaked into ProgressState")
                self.assertNotIn("mastery", canonical_json(state).lower())


class ValidatorBackwardCompatibilityTests(unittest.TestCase):
    def run_script(self, relative: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, relative],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_progress_validator_still_passes(self) -> None:
        result = self.run_script("scripts/validate_progress.py")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("PASS progress contract schema validation", result.stdout)

    def test_taxonomy_validator_still_passes(self) -> None:
        result = self.run_script("scripts/validate_taxonomy.py")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("PASS", result.stdout)


if __name__ == "__main__":
    unittest.main()
