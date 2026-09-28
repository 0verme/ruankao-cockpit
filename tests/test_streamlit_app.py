from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
import tempfile
import unittest
from zoneinfo import ZoneInfo
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

from cockpit_service import get_today, initialize_cockpit, record_browser_attempt


APP_FILE = Path(__file__).resolve().parents[1] / "streamlit_app.py"

# Keep Streamlit's internal AppTest runner from making unit-test output noisy.
logging.getLogger("streamlit").setLevel(logging.ERROR)


class StreamlitAppSmokeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.local = Path(self.temporary.name) / ".local"
        self.environment = patch.dict(os.environ, {"COCKPIT_LOCAL_DIR": str(self.local)})
        self.environment.start()

    def tearDown(self) -> None:
        self.environment.stop()
        self.temporary.cleanup()

    def run_app(self) -> AppTest:
        return AppTest.from_file(str(APP_FILE), default_timeout=30).run()

    @staticmethod
    def initialize(at: AppTest) -> AppTest:
        at.button[0].click().run()
        return at

    @staticmethod
    def fill_indexed_attempt(at: AppTest) -> AppTest:
        option = next(
            option for option in at.selectbox[0].options
            if "gs-comp-2024-h1-q65" in option
        )
        at.selectbox[0].select(option).run()
        occurred_at = (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat(timespec="seconds")
        at.text_input[0].set_value(occurred_at)
        at.selectbox[1].select("答对")
        return at

    @staticmethod
    def fill_attempt(at: AppTest, *, source_path: str = "questions/index.json") -> AppTest:
        at.selectbox[0].select("手动填写引用").run()
        values = [
            "test-bank",
            "0123456789abcdef0123456789abcdef01234567",
            source_path,
            "question-streamlit-001",
            (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat(timespec="seconds"),
        ]
        for widget, value in zip(at.text_input, values):
            widget.set_value(value)
        at.selectbox[1].select("答对")
        return at

    def test_uninitialized_init_today_record_success_and_rerun_are_smokeable(self) -> None:
        local = self.local
        at = self.run_app()
        self.assertFalse(at.exception)
        self.assertIn("Cockpit 尚未初始化", [item.value for item in at.warning])

        self.initialize(at)
        self.assertFalse(at.exception)
        self.assertTrue((local / "config.json").is_file())
        self.assertTrue(any("今天 ·" in item.value for item in at.subheader))
        self.assertEqual([metric.label for metric in at.metric], ["今日可用", "已安排", "剩余容量"])
        self.assertTrue(any("NEW LEARNING" in item.value for item in at.markdown))

        self.fill_indexed_attempt(at).button[0].click().run()
        self.assertFalse(at.exception)
        self.assertTrue(any("Progress fact 已写入" in item.value for item in at.success))
        progress_path = local / "progress-events.jsonl"
        events = [json.loads(line) for line in progress_path.read_text(encoding="utf-8").splitlines()]
        self.assertEqual(len(events), 1)
        self.assertTrue(events[0]["event_id"].startswith("browser-attempt-"))
        self.assertEqual(events[0]["question"]["source_question_id"], "2024-h1-comprehensive-q65")

        # A browser refresh/rerun reloads .local and does not resubmit the form.
        at.run()
        refreshed = [json.loads(line) for line in progress_path.read_text(encoding="utf-8").splitlines()]
        self.assertEqual(len(refreshed), 1)
        self.assertFalse(at.exception)

    def test_review_and_new_learning_are_rendered_as_distinct_planner_tasks(self) -> None:
        initialize_cockpit(self.local)
        now = datetime.now(ZoneInfo("Asia/Shanghai"))
        seed_as_of = (now - timedelta(days=7)).isoformat()
        initial = get_today(seed_as_of, local_dir=self.local)
        task = next(
            task for task in initial.planner_output["days"][0]["tasks"]
            if task["task_type"] == "new_learning"
        )
        record_browser_attempt(
            task["task_id"],
            occurred_at=seed_as_of,
            question={
                "source_id": "test-bank",
                "source_commit": "0123456789abcdef0123456789abcdef01234567",
                "source_path": "questions/index.json",
                "source_question_id": "question-review-smoke",
            },
            correct=True,
            as_of=initial.planner_output["as_of"],
            local_dir=self.local,
        )

        at = self.run_app()
        self.assertFalse(at.exception)
        labels = [item.value for item in at.markdown]
        self.assertTrue(any("REVIEW ·" in value for value in labels), labels)
        self.assertTrue(any("NEW LEARNING ·" in value for value in labels), labels)
        self.assertTrue(any("复习今日到期内容" in item.value or "复习已逾期内容" in item.value for item in at.caption))

    def test_invalid_source_is_presented_and_writes_no_fact(self) -> None:
        local = self.local
        at = self.run_app()
        self.initialize(at)
        self.fill_attempt(at, source_path="../outside/questions.json").button[0].click().run()
        self.assertFalse(at.exception)
        self.assertTrue(any("来源路径必须是安全的仓库相对路径" in item.value for item in at.error))
        self.assertEqual((local / "progress-events.jsonl").read_text(encoding="utf-8"), "")
        self.assertEqual((local / "review-events.jsonl").read_text(encoding="utf-8"), "")
        self.assertEqual(json.loads((local / "review-items.json").read_text(encoding="utf-8")), [])


if __name__ == "__main__":
    unittest.main()
