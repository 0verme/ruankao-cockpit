from __future__ import annotations

import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CLI = PROJECT_ROOT / "cockpit.py"
DAY_1 = "2026-09-27T09:00:00+08:00"
DAY_2 = "2026-09-28T09:00:00+08:00"
TEST_COMMIT = "0123456789abcdef0123456789abcdef01234567"


class CockpitCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.cwd = Path(self.temp_dir.name)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(CLI), *args],
            cwd=self.cwd,
            text=True,
            capture_output=True,
            check=False,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        )

    def init(self) -> None:
        result = self.run_cli("init")
        self.assertEqual(result.returncode, 0, result.stderr)

    def empty_state_bytes(self) -> dict[str, bytes]:
        local = self.cwd / ".local"
        return {
            name: (local / name).read_bytes()
            for name in ("progress-events.jsonl", "review-events.jsonl", "review-items.json")
        }

    def next_new_task(self) -> tuple[str, str, str]:
        result = self.run_cli("today", "--as-of", DAY_1)
        self.assertEqual(result.returncode, 0, result.stderr)
        topic_line = next(line for line in result.stdout.splitlines() if "[NEW] " in line)
        topic_id = topic_line.split("[NEW] ", 1)[1].split(" · ", 1)[0]
        task_id = re.search(r"task: (task-[0-9a-f]+)", result.stdout)
        self.assertIsNotNone(task_id, result.stdout)
        return topic_id, task_id.group(1), result.stdout

    @staticmethod
    def attempt(event_id: str, topic_id: str, *, occurred_at: str = DAY_1) -> dict[str, object]:
        return {
            "event_id": event_id,
            "schema_version": "progress-event/v0.1",
            "event_type": "comprehensive_attempt",
            "occurred_at": occurred_at,
            "question": {
                "source_id": "test-bank",
                "source_commit": TEST_COMMIT,
                "source_path": "question-index.json",
                "source_question_id": f"question-{event_id}",
            },
            "topics": [topic_id],
            "correct": True,
        }

    def save_attempt(self, value: dict[str, object]) -> Path:
        path = self.cwd / "attempt.json"
        path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")
        return path

    def record(self, task_id: str, attempt_path: Path, context_id: str) -> subprocess.CompletedProcess[str]:
        return self.run_cli(
            "record",
            "--task-id", task_id,
            "--attempt", str(attempt_path),
            "--review-context-event-id", context_id,
            "--as-of", DAY_1,
        )

    def test_init_creates_contract_aligned_files_and_is_non_destructive(self) -> None:
        result = self.run_cli("init")
        self.assertEqual(result.returncode, 0, result.stderr)
        local = self.cwd / ".local"
        self.assertEqual(
            {path.name for path in local.iterdir()},
            {"config.json", "progress-events.jsonl", "review-events.jsonl", "review-items.json", "pending"},
        )
        config = json.loads((local / "config.json").read_text(encoding="utf-8"))
        self.assertEqual(config, {
            "schema_version": "user-configuration/v0.1",
            "timezone": "Asia/Shanghai",
            "daily_available_minutes": 60,
            "study_days": [1, 2, 3, 4, 5, 6, 7],
        })
        self.assertEqual((local / "progress-events.jsonl").read_text(encoding="utf-8"), "")
        self.assertEqual((local / "review-events.jsonl").read_text(encoding="utf-8"), "")
        self.assertEqual(json.loads((local / "review-items.json").read_text(encoding="utf-8")), [])

        original_config = (local / "config.json").read_bytes()
        (local / "progress-events.jsonl").write_text('{"kept":true}\n', encoding="utf-8")
        result = self.run_cli("init")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Already initialized", result.stdout)
        self.assertEqual((local / "config.json").read_bytes(), original_config)
        self.assertEqual((local / "progress-events.jsonl").read_text(encoding="utf-8"), '{"kept":true}\n')

    def test_empty_today_and_explicit_as_of_are_deterministic(self) -> None:
        self.init()
        first = self.run_cli("today", "--as-of", DAY_1)
        second = self.run_cli("today", "--as-of", DAY_1)
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertEqual(first.stdout, second.stdout)
        self.assertIn("as_of: 2026-09-27T01:00:00Z", first.stdout)
        self.assertIn("timezone: Asia/Shanghai", first.stdout)
        self.assertIn("[NEW] ", first.stdout)
        self.assertIn("task: task-", first.stdout)

    def test_record_new_learning_and_next_day_replan_via_runtime_cli(self) -> None:
        self.init()
        topic_id, task_id, day1 = self.next_new_task()
        self.assertIn(f"[NEW] {topic_id}", day1)

        attempt_path = self.save_attempt(self.attempt("attempt-day1-001", topic_id))
        result = self.record(task_id, attempt_path, "context-day1-001")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("1 Progress Event", result.stdout)
        self.assertIn("1 Review Item", result.stdout)
        self.assertIn("1 Review Context", result.stdout)

        local = self.cwd / ".local"
        progress = [json.loads(line) for line in (local / "progress-events.jsonl").read_text(encoding="utf-8").splitlines()]
        reviews = [json.loads(line) for line in (local / "review-events.jsonl").read_text(encoding="utf-8").splitlines()]
        items = json.loads((local / "review-items.json").read_text(encoding="utf-8"))
        self.assertEqual([event["event_id"] for event in progress], ["attempt-day1-001"])
        self.assertEqual(reviews[0]["attempt_context"], "initial_learning")
        self.assertEqual(reviews[0]["source_event_id"], "attempt-day1-001")
        self.assertEqual(items[0]["review_item_id"], f"review/topic/{topic_id}")
        self.assertEqual(items[0]["source_reference"], self.attempt("attempt-day1-001", topic_id)["question"])

        day2 = self.run_cli("today", "--as-of", DAY_2)
        self.assertEqual(day2.returncode, 0, day2.stderr)
        self.assertIn(f"[REVIEW] {topic_id}", day2.stdout)
        new_lines = [line for line in day2.stdout.splitlines() if "[NEW] " in line]
        self.assertEqual(len(new_lines), 1, day2.stdout)
        self.assertNotIn(f"[NEW] {topic_id}", day2.stdout)

    def test_invalid_attempts_do_not_change_local_facts(self) -> None:
        self.init()
        topic_id, task_id, _ = self.next_new_task()
        initial_bytes = self.empty_state_bytes()
        other_topic = next(
            node["id"]
            for node in json.loads((PROJECT_ROOT / "taxonomy/taxonomy.json").read_text(encoding="utf-8"))["nodes"]
            if node["id"].count(".") == 2 and node["id"] != topic_id
        )
        invalid_attempts = [
            ("topic-mismatch", self.attempt("attempt-mismatch", other_topic)),
            ("bad-provenance", self.attempt("attempt-provenance", topic_id)),
            ("bad-schema", self.attempt("attempt-schema", topic_id)),
        ]
        invalid_attempts[1][1]["question"]["source_commit"] = "not-a-commit"  # type: ignore[index]
        invalid_attempts[2][1]["schema_version"] = "progress-event/v99"  # type: ignore[index]

        for label, attempt in invalid_attempts:
            with self.subTest(label=label):
                path = self.save_attempt(attempt)
                result = self.record(task_id, path, f"context-{label}")
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("Error:", result.stderr)
                self.assertEqual(self.empty_state_bytes(), initial_bytes)
                self.assertFalse((self.cwd / ".local" / "pending" / "record.json").exists())

    def test_duplicate_attempt_is_reported_without_appending_again(self) -> None:
        self.init()
        topic_id, task_id, _ = self.next_new_task()
        path = self.save_attempt(self.attempt("attempt-duplicate-001", topic_id))
        first = self.record(task_id, path, "context-duplicate-001")
        self.assertEqual(first.returncode, 0, first.stderr)
        persisted = self.empty_state_bytes()

        repeated = self.record(task_id, path, "context-duplicate-001")
        self.assertNotEqual(repeated.returncode, 0)
        self.assertIn("Duplicate progress event ID: attempt-duplicate-001", repeated.stderr)
        self.assertEqual(self.empty_state_bytes(), persisted)


if __name__ == "__main__":
    unittest.main()
