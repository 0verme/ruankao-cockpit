from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import httpx

from api import app, get_local_dir
from cockpit_service import get_today, initialize_cockpit, record_browser_attempt
from learning_payload import LearningPayloadError


AS_OF = "2026-09-27T09:00:00+08:00"
QUESTION = {
    "source_id": "test-bank",
    "source_commit": "0123456789abcdef0123456789abcdef01234567",
    "source_path": "questions/index.json",
    "source_question_id": "api-question-001",
}
TOPIC_WITH_PAYLOAD = "ARCH.CLOUD_NATIVE.CONTAINERS_SERVERLESS"
TOPIC_WITHOUT_PAYLOAD = "ARCH.CLOUD_NATIVE.MICROSERVICES"


class FrozenDateTime(datetime):
    @classmethod
    def now(cls, tz=None):
        fixed = datetime(2026, 9, 27, 9, 0, tzinfo=timezone(timedelta(hours=8)))
        return fixed.astimezone(tz) if tz is not None else fixed.replace(tzinfo=None)


class SyncASGIClient:
    """Small synchronous wrapper around HTTPX's in-process ASGI transport."""

    def __init__(self, application) -> None:
        self.application = application

    def request(self, method: str, path: str, **kwargs):
        async def send():
            transport = httpx.ASGITransport(app=self.application)
            async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
                return await client.request(method, path, **kwargs)

        return asyncio.run(send())

    def get(self, path: str, **kwargs):
        return self.request("GET", path, **kwargs)

    def post(self, path: str, **kwargs):
        return self.request("POST", path, **kwargs)

    def close(self) -> None:
        pass


class FastAPITransportTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.local = self.root / ".local"
        app.dependency_overrides[get_local_dir] = lambda: self.local
        self.client = SyncASGIClient(app)

    def tearDown(self) -> None:
        self.client.close()
        app.dependency_overrides.clear()
        self.temporary.cleanup()

    def test_configured_local_dir_is_absolute_and_independent_of_cwd(self) -> None:
        configured = get_local_dir()
        original = Path.cwd()
        self.assertTrue(configured.is_absolute())
        try:
            os.chdir(self.root)
            self.assertEqual(get_local_dir(), configured)
        finally:
            os.chdir(original)

    def fact_bytes(self, local: Path | None = None) -> tuple[bytes, bytes, bytes]:
        target = local or self.local
        return tuple(
            (target / name).read_bytes()
            for name in ("progress-events.jsonl", "review-events.jsonl", "review-items.json")
        )  # type: ignore[return-value]

    def today_task(self) -> tuple[str, dict[str, object]]:
        snapshot = get_today(AS_OF, local_dir=self.local)
        task = next(
            task for task in snapshot.planner_output["days"][0]["tasks"]
            if task["task_type"] == "new_learning"
        )
        return task["task_id"], task

    def test_uninitialized_gets_do_not_create_local_state(self) -> None:
        today = self.client.get("/api/today", params={"as_of": AS_OF})
        topic = self.client.get(f"/api/topics/{TOPIC_WITH_PAYLOAD}", params={"as_of": AS_OF})
        attempt = self.client.post("/api/attempts", json={
            "task_id": "not-scheduled",
            "occurred_at": AS_OF,
            "question": QUESTION,
            "correct": True,
        })

        self.assertEqual(today.status_code, 409)
        self.assertEqual(today.json()["error"]["category"], "not_initialized")
        self.assertEqual(topic.status_code, 409)
        self.assertEqual(topic.json()["error"]["category"], "not_initialized")
        self.assertEqual(attempt.status_code, 409)
        self.assertEqual(attempt.json()["error"]["category"], "not_initialized")
        self.assertFalse(self.local.exists())

    def test_explicit_init_is_idempotent_and_does_not_overwrite_facts(self) -> None:
        created = self.client.post("/api/init")
        self.assertEqual(created.status_code, 200)
        self.assertEqual(created.json(), {"state": "created"})
        task_id, _ = self.today_task()
        record_browser_attempt(
            task_id,
            occurred_at=AS_OF,
            question=QUESTION,
            correct=True,
            as_of=AS_OF,
            local_dir=self.local,
        )
        before = self.fact_bytes()

        existing = self.client.post("/api/init")
        self.assertEqual(existing.status_code, 200)
        self.assertEqual(existing.json(), {"state": "already_exists"})
        self.assertEqual(self.fact_bytes(), before)

    def test_explicit_init_supports_existing_bind_mount_directory_without_touching_other_files(self) -> None:
        self.local.mkdir()
        source_data = self.local / "learning-paths"
        source_data.mkdir()
        marker = source_data / "manifest.json"
        marker.write_text('{"source":"kept"}', encoding="utf-8")

        response = self.client.post("/api/init")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"state": "created"})
        self.assertEqual(marker.read_text(encoding="utf-8"), '{"source":"kept"}')
        self.assertTrue((self.local / "config.json").is_file())
        self.assertTrue((self.local / "progress-events.jsonl").is_file())
        self.assertTrue((self.local / "review-events.jsonl").is_file())
        self.assertTrue((self.local / "review-items.json").is_file())

    def test_today_returns_existing_service_outputs_and_is_deterministic_for_fixed_as_of(self) -> None:
        initialize_cockpit(self.local)
        expected = get_today(AS_OF, local_dir=self.local)

        first = self.client.get("/api/today", params={"as_of": AS_OF})
        second = self.client.get("/api/today", params={"as_of": AS_OF})
        naive_time = self.client.get("/api/today", params={"as_of": "2026-09-27T09:00:00"})

        self.assertEqual(first.status_code, 200)
        self.assertEqual(naive_time.status_code, 422)
        self.assertEqual(naive_time.json()["error"]["category"], "invalid_timestamp")
        payload = first.json()
        self.assertEqual(payload, second.json())
        self.assertEqual(payload["planner"], expected.planner_output)
        self.assertEqual(payload["progress"], expected.progress_state)
        self.assertEqual(payload["review"]["state"], expected.review_state)
        self.assertEqual(payload["review"]["items"], expected.review_items)
        self.assertTrue(payload["task_topics"])
        topic = next(iter(payload["task_topics"].values()))
        self.assertIn("topic_name", topic)
        self.assertIn("breadcrumb", topic)
        self.assertIn(topic["learning_payload_status"], {"available", "unavailable"})

    def test_topic_payload_available_unavailable_unknown_and_non_active_are_distinct(self) -> None:
        initialize_cockpit(self.local)
        available = self.client.get(f"/api/topics/{TOPIC_WITH_PAYLOAD}", params={"as_of": AS_OF})
        unavailable = self.client.get(f"/api/topics/{TOPIC_WITHOUT_PAYLOAD}", params={"as_of": AS_OF})
        unknown = self.client.get("/api/topics/UNKNOWN.TOPIC.ID", params={"as_of": AS_OF})
        non_active = self.client.get("/api/topics/ARCH.CLOUD_NATIVE", params={"as_of": AS_OF})

        self.assertEqual(available.status_code, 200)
        self.assertEqual(available.json()["learning_payload_status"], "available")
        self.assertIsNotNone(available.json()["learning_payload"])
        self.assertEqual(unavailable.status_code, 200)
        self.assertEqual(unavailable.json()["learning_payload_status"], "unavailable")
        self.assertIsNone(unavailable.json()["learning_payload"])
        self.assertIsNone(unavailable.json()["learning_payload_version"])
        self.assertEqual(unknown.status_code, 404)
        self.assertEqual(unknown.json()["error"]["category"], "unknown_topic")
        self.assertEqual(non_active.status_code, 422)
        self.assertEqual(non_active.json()["error"]["category"], "non_active_topic")

    def test_invalid_payload_provenance_fails_closed_over_http(self) -> None:
        initialize_cockpit(self.local)
        before = self.fact_bytes()
        with patch(
            "cockpit_service.load_learning_payload",
            side_effect=LearningPayloadError("unverifiable source", "invalid_source_provenance"),
        ):
            response = self.client.get(f"/api/topics/{TOPIC_WITH_PAYLOAD}", params={"as_of": AS_OF})

        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["error"]["category"], "invalid_source_provenance")
        self.assertEqual(self.fact_bytes(), before)

    def test_attempt_reuses_service_and_returns_replay_results_with_deterministic_identity(self) -> None:
        initialize_cockpit(self.local)
        task_id, _ = self.today_task()
        direct_local = self.root / "direct" / ".local"
        initialize_cockpit(direct_local)
        body = {
            "task_id": task_id,
            "occurred_at": AS_OF,
            "question": QUESTION,
            "correct": True,
        }

        with patch("cockpit_service.datetime", FrozenDateTime):
            response = self.client.post("/api/attempts", json=body)
            direct = record_browser_attempt(
                task_id,
                occurred_at=AS_OF,
                question=QUESTION,
                correct=True,
                local_dir=direct_local,
            )

        self.assertEqual(response.status_code, 200, response.text)
        result = response.json()
        self.assertEqual(result["recorded"], {
            "progress_event_count": 1,
            "review_item_count": 1,
            "review_context_count": 1,
        })
        self.assertEqual(result["today"]["planner"], direct.today.planner_output)
        self.assertEqual(result["today"]["progress"], direct.today.progress_state)
        self.assertEqual(result["today"]["review"]["state"], direct.today.review_state)
        self.assertEqual(result["today"]["review"]["items"], direct.today.review_items)
        self.assertEqual(self.fact_bytes(), self.fact_bytes(direct_local))

        progress = json.loads((self.local / "progress-events.jsonl").read_text().splitlines()[0])
        self.assertTrue(progress["event_id"].startswith("browser-attempt-"))
        self.assertNotIn("mastered", progress)
        self.assertNotIn("completed", progress)

        after_first_write = self.fact_bytes()
        with patch("cockpit_service.datetime", FrozenDateTime):
            duplicate = self.client.post("/api/attempts", json=body)
        self.assertEqual(duplicate.status_code, 409)
        self.assertIn(
            duplicate.json()["error"]["category"],
            {"duplicate_event", "task_not_scheduled"},
        )
        self.assertEqual(self.fact_bytes(), after_first_write)

    def test_invalid_attempt_and_client_supplied_progress_flags_do_not_write(self) -> None:
        initialize_cockpit(self.local)
        task_id, _ = self.today_task()
        before = self.fact_bytes()
        invalid = {
            "task_id": task_id,
            "occurred_at": AS_OF,
            "question": {**QUESTION, "source_path": "../outside/questions.json"},
            "correct": False,
        }
        with patch("cockpit_service.datetime", FrozenDateTime):
            invalid_result = self.client.post("/api/attempts", json=invalid)
            forbidden_flag = self.client.post(
                "/api/attempts",
                json={**invalid, "question": QUESTION, "mastered": True},
            )

        self.assertEqual(invalid_result.status_code, 422)
        self.assertEqual(forbidden_flag.status_code, 422)
        self.assertEqual(forbidden_flag.json()["error"]["category"], "invalid_request")
        self.assertEqual(self.fact_bytes(), before)


if __name__ == "__main__":
    unittest.main()
