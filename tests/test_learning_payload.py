from __future__ import annotations

import json
from pathlib import Path
import shutil
import tempfile
import unittest

from jsonschema import Draft202012Validator

from learning_payload import (
    LearningPayloadError,
    PROJECT_ROOT,
    learning_source_url,
    load_learning_payload,
)


TOPIC_ID = "ARCH.CLOUD_NATIVE.CONTAINERS_SERVERLESS"
PAYLOAD_FILE = f"data/learning-payloads/{TOPIC_ID}.json"


class LearningPayloadTests(unittest.TestCase):
    def test_static_payload_is_versioned_and_provenance_resolves_deterministically(self) -> None:
        first = load_learning_payload(TOPIC_ID)
        second = load_learning_payload(TOPIC_ID)
        self.assertIsNotNone(first)
        self.assertEqual(first, second)
        assert first is not None
        self.assertEqual(first["schema_version"], "learning-payload/v0.1")
        self.assertEqual(first["version"], "1.0.0")
        self.assertEqual(first["topic_id"], TOPIC_ID)
        self.assertEqual(len(first["objectives"]), 4)
        self.assertTrue(first["core_points"])
        self.assertTrue(first["exam_focus"])
        self.assertEqual(
            {reference["reference_id"] for reference in first["source_references"]},
            {"textbook-containers", "textbook-serverless", "outline-cloud-native", "golden-q65"},
        )
        textbook = next(ref for ref in first["source_references"] if ref["reference_id"] == "textbook-containers")
        serverless = next(ref for ref in first["source_references"] if ref["reference_id"] == "textbook-serverless")
        self.assertEqual(textbook["source_anchor"], "14.3.1 容器技术")
        self.assertEqual(serverless["source_anchor"], "14.3.3 无服务器技术")
        question = next(ref for ref in first["source_references"] if ref["kind"] == "golden_set_question")
        self.assertEqual(question["confidence"], "medium")
        self.assertIn("c467a7cbc16970c52cf6d723badbb22938963ae6", learning_source_url(textbook))
        self.assertIn("/blob/", learning_source_url(question))

    def test_checked_in_json_schema_accepts_payload(self) -> None:
        schema = json.loads((PROJECT_ROOT / "data/learning-payloads/schema.json").read_text(encoding="utf-8"))
        payload = json.loads((PROJECT_ROOT / PAYLOAD_FILE).read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        self.assertEqual(list(Draft202012Validator(schema).iter_errors(payload)), [])

    def test_missing_payload_returns_explicit_absence(self) -> None:
        self.assertIsNone(load_learning_payload("ARCH.CLOUD_NATIVE.EVENT_DRIVEN"))

    def test_non_l3_or_unsafe_topic_id_is_rejected(self) -> None:
        for topic_id in ("ARCH.CLOUD_NATIVE", "../../outside"):
            with self.subTest(topic_id=topic_id), self.assertRaises(LearningPayloadError):
                load_learning_payload(topic_id)

    def test_invalid_source_commit_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for relative in (
                "taxonomy/taxonomy.json",
                "taxonomy/source-mappings.json",
                "data/golden-set/comprehensive.sample.json",
            ):
                destination = root / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(PROJECT_ROOT / relative, destination)
            payload_path = root / PAYLOAD_FILE
            payload_path.parent.mkdir(parents=True, exist_ok=True)
            payload = json.loads((PROJECT_ROOT / PAYLOAD_FILE).read_text(encoding="utf-8"))
            payload["source_references"][0]["source_commit"] = "not-an-immutable-commit"
            payload_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

            with self.assertRaises(LearningPayloadError) as caught:
                load_learning_payload(TOPIC_ID, root=root)
            self.assertEqual(caught.exception.category, "invalid_source_provenance")

    def test_unmapped_source_path_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for relative in (
                "taxonomy/taxonomy.json",
                "taxonomy/source-mappings.json",
                "data/golden-set/comprehensive.sample.json",
            ):
                destination = root / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(PROJECT_ROOT / relative, destination)
            payload_path = root / PAYLOAD_FILE
            payload_path.parent.mkdir(parents=True, exist_ok=True)
            payload = json.loads((PROJECT_ROOT / PAYLOAD_FILE).read_text(encoding="utf-8"))
            payload["source_references"][0]["source_path"] = "../../unverified.md"
            payload_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

            with self.assertRaises(LearningPayloadError) as caught:
                load_learning_payload(TOPIC_ID, root=root)
            self.assertEqual(caught.exception.category, "invalid_source_provenance")

    def test_unknown_evidence_reference_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for relative in (
                "taxonomy/taxonomy.json",
                "taxonomy/source-mappings.json",
                "data/golden-set/comprehensive.sample.json",
            ):
                destination = root / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(PROJECT_ROOT / relative, destination)
            payload_path = root / PAYLOAD_FILE
            payload_path.parent.mkdir(parents=True, exist_ok=True)
            payload = json.loads((PROJECT_ROOT / PAYLOAD_FILE).read_text(encoding="utf-8"))
            payload["exam_focus"][0]["evidence_refs"] = ["missing-reference"]
            payload_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

            with self.assertRaises(LearningPayloadError):
                load_learning_payload(TOPIC_ID, root=root)


if __name__ == "__main__":
    unittest.main()
