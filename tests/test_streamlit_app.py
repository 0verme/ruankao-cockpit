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
            if "第 65 题：云计算虚拟化技术识别" in option
        )
        at.selectbox[0].select(option).run()
        occurred_at = (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat(timespec="seconds")
        at.text_input[0].set_value(occurred_at)
        at.selectbox[1].select("答对")
        return at

    @staticmethod
    def fill_attempt(at: AppTest, *, source_path: str = "questions/index.json") -> AppTest:
        at.selectbox[0].select("其他来源（手动填写引用）").run()
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
        markdown_values = [item.value for item in at.markdown]
        self.assertTrue(any("NEW LEARNING" in value for value in markdown_values))
        self.assertTrue(any("### 容器与 Serverless" in value for value in markdown_values))
        self.assertTrue(any("今天学会什么" in value for value in markdown_values))
        self.assertTrue(any("Learning Payload 1.0.0" in item.value for item in at.caption))
        self.assertTrue(any("系统架构设计基础知识 › 云原生架构设计 › 容器与 Serverless" in item.value for item in at.caption))
        self.assertEqual((local / "progress-events.jsonl").read_text(encoding="utf-8"), "")
        self.assertTrue(any("说明容器如何封装应用及其依赖" in value for value in markdown_values))
        self.assertTrue(any("容器与虚拟机：看运行边界" in value for value in markdown_values))
        self.assertTrue(any("软考关注点" in value for value in markdown_values))
        self.assertTrue(any("第 14 章 14.3.1 容器技术" in value for value in markdown_values))
        self.assertTrue(any("第 14 章 14.3.3 无服务器技术" in value for value in markdown_values))
        self.assertIn("+08:00", at.text_input[0].value)
        self.assertFalse(any("错误原因" in item.label for item in at.selectbox))

        self.fill_indexed_attempt(at).button[0].click().run()
        self.assertFalse(at.exception)
        self.assertTrue(any("Progress fact 已写入" in item.value for item in at.success))
        progress_path = local / "progress-events.jsonl"
        events = [json.loads(line) for line in progress_path.read_text(encoding="utf-8").splitlines()]
        self.assertEqual(len(events), 1)
        self.assertTrue(events[0]["event_id"].startswith("browser-attempt-"))
        self.assertEqual(events[0]["question"]["source_question_id"], "2024-h1-comprehensive-q65")
        self.assertEqual(events[0]["question"]["golden_set_record_id"], "gs-comp-2024-h1-q65")

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

        current = get_today(local_dir=self.local)
        day_tasks = current.planner_output["days"][0]["tasks"]
        review_topic = task["target_ref"]
        next_new_topic = next(task["target_ref"] for task in day_tasks if task["task_type"] == "new_learning")
        at = self.run_app()
        self.assertFalse(at.exception)
        labels = [item.value for item in at.markdown]
        self.assertIn("#### REVIEW", labels)
        self.assertIn("#### NEW LEARNING", labels)
        self.assertTrue(any("今天到期，需要复习" in item.value or "超过计划复习时间" in item.value for item in at.caption))
        self.assertEqual("\n".join(labels).count("**今天学会什么**"), 1)
        self.assertIn("容器与虚拟机：看运行边界", "\n".join(labels))
        self.assertNotEqual(review_topic, next_new_topic)

    def test_missing_learning_payload_is_explicit_and_does_not_crash(self) -> None:
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
                "source_question_id": "question-missing-payload",
            },
            correct=True,
            as_of=initial.planner_output["as_of"],
            local_dir=self.local,
        )
        at = self.run_app()
        self.assertFalse(at.exception)
        self.assertTrue(any("材料尚未整理" in item.value for item in at.info))
        labels = "\n".join(item.value for item in at.markdown)
        self.assertIn("#### REVIEW", labels)
        self.assertIn("### 容器与 Serverless", labels)
        self.assertIn("#### NEW LEARNING", labels)
        self.assertIn("### 事件驱动架构", labels)
        self.assertIn("容器与虚拟机：看运行边界", labels)

    def test_attempt_time_uses_configured_timezone_and_needs_no_manual_entry(self) -> None:
        at = self.run_app()
        self.initialize(at)
        config_path = self.local / "config.json"
        config = json.loads(config_path.read_text(encoding="utf-8"))
        config["timezone"] = "Asia/Tokyo"
        config_path.write_text(json.dumps(config), encoding="utf-8")

        at = self.run_app()
        self.assertIn("Asia/Tokyo", at.text_input[0].label)
        self.assertTrue(at.text_input[0].value.endswith("+09:00"), at.text_input[0].value)
        option = next(item for item in at.selectbox[0].options if "第 65 题：云计算虚拟化技术识别" in item)
        at.selectbox[0].select(option).run()
        at.selectbox[1].select("答对").run()
        at.button[0].click().run()
        self.assertFalse(at.exception)
        event = json.loads((self.local / "progress-events.jsonl").read_text(encoding="utf-8").splitlines()[0])
        self.assertTrue(event["occurred_at"].endswith("+09:00"), event["occurred_at"])

    def test_error_cause_only_appears_after_wrong_answer(self) -> None:
        at = self.run_app()
        self.initialize(at)
        self.assertFalse(any("错误原因" in item.label for item in at.selectbox))

        at.selectbox[1].select("答错").run()
        self.assertTrue(any("错误原因" in item.label for item in at.selectbox))

        at.selectbox[1].select("答对").run()
        self.assertFalse(any("错误原因" in item.label for item in at.selectbox))

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
