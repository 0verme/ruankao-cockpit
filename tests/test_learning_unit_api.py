from __future__ import annotations

import asyncio
import unittest
from unittest.mock import patch

import httpx

from api import app
from learning_unit_experience import LearningUnitExperienceError


class SyncASGIClient:
    def __init__(self, application) -> None:
        self.application = application

    def get(self, path: str):
        async def send():
            transport = httpx.ASGITransport(app=self.application)
            async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
                return await client.get(path)
        return asyncio.run(send())


class LearningUnitAPITests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = SyncASGIClient(app)

    def test_valid_merge_unit_returns_static_read_model_without_progress_facts(self) -> None:
        response = self.client.get("/api/learning-units/system-architect-checkin/checkin-001")
        self.assertEqual(response.status_code, 200, response.text)
        body = response.json()
        self.assertEqual(body["path_id"], "system-architect-checkin")
        self.assertEqual(body["path_version"], "1.0.0")
        self.assertEqual(body["item_id"], "checkin-001")
        self.assertEqual(body["mapping_status"], "merge")
        self.assertEqual(body["topics"], [{
            "topic_id": "SOFTWARE.ENGINEERING.PROCESS",
            "name": "软件过程与开发方法",
        }])
        self.assertIn("# 软件工程：生命周期与基本要素", body["content_markdown"])
        self.assertNotIn("content_version:", body["content_markdown"])
        for forbidden in ("progress", "completed", "mastery", "review_due"):
            self.assertNotIn(forbidden, body)

    def test_path_directory_is_manifest_ordered_and_exposes_only_browser_fields(self) -> None:
        response = self.client.get("/api/learning-paths/system-architect-checkin")
        self.assertEqual(response.status_code, 200, response.text)
        body = response.json()
        self.assertEqual(body["path_id"], "system-architect-checkin")
        self.assertEqual(body["version"], "1.0.0")
        self.assertEqual(body["path_status"], "draft")
        self.assertEqual(len(body["items"]), 112)
        self.assertEqual([item["order"] for item in body["items"]], list(range(1, 113)))
        self.assertEqual(body["items"][0]["title"], "软件工程：生命周期与基本要素")
        self.assertEqual(body["items"][19]["kind"], "non_learning")
        self.assertEqual(body["items"][19]["mapping_status"], "non_learning")
        self.assertEqual(body["items"][31]["mapping_status"], "unmapped")
        self.assertEqual(set(body["items"][0]), {"item_id", "order", "title", "kind", "mapping_status"})
        for forbidden in ("progress", "review", "mastery", "completion", "completed", "review_due"):
            self.assertNotIn(forbidden, body)
            for item in body["items"]:
                self.assertNotIn(forbidden, item)

    def test_unknown_directory_path_is_404(self) -> None:
        response = self.client.get("/api/learning-paths/unknown-path")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["error"]["category"], "unknown_learning_path")

    def test_learning_unit_navigation_uses_path_order_and_skips_non_learning(self) -> None:
        cases = (
            ("checkin-001", None, "checkin-002"),
            ("checkin-019", "checkin-018", "checkin-021"),
            ("checkin-021", "checkin-019", "checkin-022"),
            ("checkin-032", "checkin-031", "checkin-033"),
            ("checkin-005", "checkin-004", "checkin-006"),
            ("checkin-112", "checkin-111", None),
        )
        for item_id, previous, following in cases:
            with self.subTest(item_id=item_id):
                response = self.client.get(
                    f"/api/learning-units/system-architect-checkin/{item_id}"
                )
                self.assertEqual(response.status_code, 200, response.text)
                self.assertEqual(response.json()["navigation"], {
                    "previous_item_id": previous,
                    "next_item_id": following,
                })

    def test_split_and_unmapped_units_are_valid_single_read_responses(self) -> None:
        split = self.client.get("/api/learning-units/system-architect-checkin/checkin-005")
        unmapped = self.client.get("/api/learning-units/system-architect-checkin/checkin-032")
        self.assertEqual(split.status_code, 200)
        self.assertEqual(split.json()["item_id"], "checkin-005")
        self.assertEqual([topic["name"] for topic in split.json()["topics"]], ["软件过程与开发方法", "软件测试"])
        self.assertEqual(unmapped.status_code, 200)
        self.assertEqual(unmapped.json()["mapping_status"], "unmapped")
        self.assertEqual(unmapped.json()["topic_ids"], [])
        self.assertIn("# 可观测性：指标、日志与链路追踪", unmapped.json()["content_markdown"])

    def test_missing_path_item_and_non_learning_have_explicit_404_errors(self) -> None:
        cases = (
            ("/api/learning-units/unknown-path/checkin-001", "unknown_learning_path"),
            ("/api/learning-units/system-architect-checkin/checkin-999", "unknown_learning_unit"),
            ("/api/learning-units/system-architect-checkin/checkin-020", "not_a_learning_unit"),
        )
        for path, category in cases:
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 404)
                self.assertEqual(response.json()["error"]["category"], category)

    def test_malformed_or_mismatched_markdown_is_a_server_integrity_error(self) -> None:
        for message in ("identity mismatch", "malformed frontmatter"):
            with self.subTest(message=message):
                with patch(
                    "api.load_learning_unit",
                    side_effect=LearningUnitExperienceError(message, "invalid_learning_unit"),
                ):
                    response = self.client.get(
                        "/api/learning-units/system-architect-checkin/checkin-001"
                    )
                self.assertEqual(response.status_code, 500)
                self.assertEqual(response.json()["error"]["category"], "invalid_learning_unit")


if __name__ == "__main__":
    unittest.main()
