from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from cockpit_service import get_today, get_topic_experience, initialize_cockpit, record_browser_attempt


DAY_1 = "2026-09-27T09:00:00+08:00"
DAY_2 = "2026-09-28T09:00:00+08:00"
QUESTION = {
    "source_id": "test-bank",
    "source_commit": "0123456789abcdef0123456789abcdef01234567",
    "source_path": "questions/index.json",
    "source_question_id": "topic-experience-question-001",
}


class TopicExperienceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.local = Path(self.temporary.name) / ".local"
        initialize_cockpit(self.local)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_experience_uses_taxonomy_payload_and_indexed_sources_without_writing_facts(self) -> None:
        snapshot = get_today(DAY_1, local_dir=self.local)
        topic_id = "ARCH.CLOUD_NATIVE.CONTAINERS_SERVERLESS"
        facts_before = {
            name: (self.local / name).read_bytes()
            for name in ("progress-events.jsonl", "review-events.jsonl", "review-items.json")
        }

        experience = get_topic_experience(topic_id, snapshot)

        self.assertEqual(experience.topic_name, "容器与 Serverless")
        self.assertEqual(
            [crumb.name for crumb in experience.breadcrumb],
            ["系统架构设计基础知识", "云原生架构设计", "容器与 Serverless"],
        )
        self.assertEqual(experience.breadcrumb[-1].topic_id, topic_id)
        self.assertEqual(experience.taxonomy_version, "0.1")
        self.assertTrue(experience.has_learning_payload)
        self.assertEqual(experience.learning_payload_version, "1.0.0")
        self.assertEqual(experience.progress_attempt_count, 0)
        self.assertIsNone(experience.progress_accuracy)
        self.assertIsNone(experience.review_mastery_state)
        self.assertIsNone(experience.review_status)
        self.assertTrue(experience.verification_sources)
        self.assertTrue(any("第 65 题" in source["display_title"] for source in experience.verification_sources))
        self.assertEqual(
            facts_before,
            {
                name: (self.local / name).read_bytes()
                for name in facts_before
            },
        )

    def test_component_payload_is_available_for_its_canonical_topic(self) -> None:
        snapshot = get_today(DAY_1, local_dir=self.local)
        experience = get_topic_experience("SOFTWARE.ENGINEERING.COMPONENTS", snapshot)

        self.assertEqual(experience.topic_name, "构件与组件技术")
        self.assertTrue(experience.has_learning_payload)
        self.assertEqual(experience.learning_payload_version, "1.0.0")
        assert experience.learning_payload is not None
        self.assertEqual(experience.learning_payload["topic_id"], "SOFTWARE.ENGINEERING.COMPONENTS")

    def test_missing_payload_is_explicit_in_read_model(self) -> None:
        snapshot = get_today(DAY_1, local_dir=self.local)
        experience = get_topic_experience("ARCH.CLOUD_NATIVE.MICROSERVICES", snapshot)

        self.assertEqual(experience.topic_name, "微服务架构")
        self.assertFalse(experience.has_learning_payload)
        self.assertIsNone(experience.learning_payload_version)
        self.assertEqual(experience.progress_attempt_count, 0)

    def test_progress_and_review_summaries_are_read_from_deterministic_replay(self) -> None:
        snapshot = get_today(DAY_1, local_dir=self.local)
        task = next(
            task for task in snapshot.planner_output["days"][0]["tasks"]
            if task["task_type"] == "new_learning"
        )
        topic_id = task["target_ref"]
        record_browser_attempt(
            task["task_id"],
            occurred_at=DAY_1,
            question=QUESTION,
            correct=True,
            as_of=snapshot.planner_output["as_of"],
            local_dir=self.local,
        )

        experience = get_topic_experience(topic_id, get_today(DAY_2, local_dir=self.local))

        self.assertEqual(experience.progress_attempt_count, 1)
        self.assertEqual(experience.progress_accuracy, 1.0)
        self.assertEqual(experience.review_mastery_state, "learning")
        self.assertIn(experience.review_status, {"scheduled", "due", "overdue"})
        self.assertEqual(experience.review_policy_version, "review-policy/simple-ladder/v0.1")
        self.assertIsNotNone(experience.review_next_due_local_date)


if __name__ == "__main__":
    unittest.main()
