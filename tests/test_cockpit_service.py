from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from cockpit_service import (
    get_today,
    initialize_cockpit,
    record_browser_attempt,
    record_result,
)


DAY_1 = "2026-09-27T09:00:00+08:00"
DAY_2 = "2026-09-28T09:00:00+08:00"
QUESTION = {
    "source_id": "test-bank",
    "source_commit": "0123456789abcdef0123456789abcdef01234567",
    "source_path": "questions/index.json",
    "source_question_id": "question-001",
}


class CockpitServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.local = Path(self.temp_dir.name) / ".local"

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def read_facts(self) -> tuple[bytes, bytes, bytes]:
        return tuple(
            (self.local / name).read_bytes()
            for name in ("progress-events.jsonl", "review-events.jsonl", "review-items.json")
        )  # type: ignore[return-value]

    def test_init_today_record_and_replay_share_the_application_service(self) -> None:
        self.assertTrue(initialize_cockpit(self.local))
        self.assertFalse(initialize_cockpit(self.local))

        day1 = get_today(DAY_1, local_dir=self.local)
        planner_day = day1.planner_output["days"][0]
        new_task = next(task for task in planner_day["tasks"] if task["task_type"] == "new_learning")
        self.assertEqual(planner_day["capacity_minutes"], 60)
        self.assertEqual(new_task["target_kind"], "topic")

        result = record_browser_attempt(
            new_task["task_id"],
            occurred_at=DAY_1,
            question=QUESTION,
            correct=True,
            as_of=day1.planner_output["as_of"],
            local_dir=self.local,
        )
        self.assertEqual(result.progress_event_count, 1)
        self.assertEqual(result.review_item_count, 1)
        self.assertEqual(result.review_context_count, 1)
        self.assertEqual(result.today.progress_state["global"]["attempt_count"], 1)
        self.assertEqual(result.today.review_state["progress_replayed_event_count"], 1)

        progress = [json.loads(line) for line in (self.local / "progress-events.jsonl").read_text().splitlines()]
        review = [json.loads(line) for line in (self.local / "review-events.jsonl").read_text().splitlines()]
        items = json.loads((self.local / "review-items.json").read_text())
        self.assertTrue(progress[0]["event_id"].startswith("browser-attempt-"))
        self.assertEqual(review[0]["event_id"], f"browser-context-{progress[0]['event_id'].removeprefix('browser-attempt-')}")
        self.assertEqual(review[0]["source_event_id"], progress[0]["event_id"])
        self.assertEqual(items[0]["source_reference"], QUESTION)

        day2 = get_today(DAY_2, local_dir=self.local)
        self.assertNotIn(new_task["target_ref"], [task["target_ref"] for task in day2.planner_output["days"][0]["tasks"] if task["task_type"] == "new_learning"])
        self.assertEqual(day2.progress_state["global"]["attempt_count"], 1)

    def test_invalid_provenance_fails_closed_and_deterministic_identity_rejects_duplicates(self) -> None:
        initialize_cockpit(self.local)
        today = get_today(DAY_1, local_dir=self.local)
        task = next(task for task in today.planner_output["days"][0]["tasks"] if task["task_type"] == "new_learning")
        before = self.read_facts()

        invalid_question = {**QUESTION, "source_path": "../outside/questions.json"}
        with self.assertRaises(ValueError):
            record_browser_attempt(
                task["task_id"],
                occurred_at=DAY_1,
                question=invalid_question,
                correct=False,
                as_of=today.planner_output["as_of"],
                local_dir=self.local,
            )
        self.assertEqual(self.read_facts(), before)

        record_browser_attempt(
            task["task_id"],
            occurred_at=DAY_1,
            question=QUESTION,
            correct=True,
            as_of=today.planner_output["as_of"],
            local_dir=self.local,
        )
        after = self.read_facts()
        progress = json.loads((self.local / "progress-events.jsonl").read_text().splitlines()[0])
        review = json.loads((self.local / "review-events.jsonl").read_text().splitlines()[0])
        with self.assertRaisesRegex(ValueError, "Duplicate progress event ID"):
            record_result(
                task["task_id"],
                progress,
                review["event_id"],
                as_of=today.planner_output["as_of"],
                local_dir=self.local,
            )
        self.assertEqual(self.read_facts(), after)


if __name__ == "__main__":
    unittest.main()
