from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from scripts.validate_learning_path import (
    LearningPathValidationError,
    validate_document,
    validate_learning_path,
)

ROOT = Path(__file__).resolve().parents[1]
PATH_DOCUMENT = json.loads(
    (ROOT / "data/learning-paths/system-architect-checkin-v1.json").read_text(encoding="utf-8")
)
TAXONOMY = json.loads((ROOT / "taxonomy/taxonomy.json").read_text(encoding="utf-8"))


class LearningPathValidationTests(unittest.TestCase):
    def test_checked_in_path_has_deterministic_audit_totals(self) -> None:
        result = validate_learning_path(ROOT)
        self.assertEqual(result["source_items"], 112)
        self.assertEqual(result["learning_items"], 110)
        self.assertEqual(result["non_learning_items"], 2)
        self.assertEqual(result["mapped_unique_l3_topics"], 60)
        self.assertEqual(len(result["uncovered_topic_ids"]), 50)
        self.assertEqual(len(result["duplicate_covered_topic_ids"]), 31)
        self.assertEqual(result["source_items_with_multiple_topic_mappings"], 40)

    def test_source_archive_fingerprint_is_frozen(self) -> None:
        source = PATH_DOCUMENT["source"]
        self.assertEqual(source["archive_name"], "系统架构设计师打卡.zip")
        self.assertEqual(source["archive_size_bytes"], 175511)
        self.assertRegex(source["archive_sha256"], r"^[a-f0-9]{64}$")
        candidate = copy.deepcopy(PATH_DOCUMENT)
        candidate["source"]["archive_sha256"] = "0" * 64
        self.assert_invalid(candidate)

    def assert_invalid(self, document: dict) -> None:
        with self.assertRaises(LearningPathValidationError):
            validate_document(document, TAXONOMY)

    def test_split_requires_multiple_active_l3_topics(self) -> None:
        candidate = copy.deepcopy(PATH_DOCUMENT)
        candidate["items"][4]["topic_ids"] = ["SOFTWARE.ENGINEERING.PROCESS"]
        self.assert_invalid(candidate)

    def test_unmapped_item_cannot_claim_a_topic(self) -> None:
        candidate = copy.deepcopy(PATH_DOCUMENT)
        candidate["items"][31]["topic_ids"] = ["QUALITY.ATTRIBUTES.TESTABILITY"]
        self.assert_invalid(candidate)

    def test_non_learning_item_cannot_carry_mapping_confidence_or_topic(self) -> None:
        candidate = copy.deepcopy(PATH_DOCUMENT)
        candidate["items"][19]["topic_ids"] = ["SOFTWARE.ENGINEERING.PROCESS"]
        self.assert_invalid(candidate)

    def test_topic_reference_must_be_active_l3(self) -> None:
        candidate = copy.deepcopy(PATH_DOCUMENT)
        candidate["items"][0]["topic_ids"] = ["ARCH.CLOUD_NATIVE"]
        self.assert_invalid(candidate)

    def test_merge_group_must_share_a_topic(self) -> None:
        candidate = copy.deepcopy(PATH_DOCUMENT)
        candidate["items"][1]["topic_ids"] = ["ARCH.FOUNDATION.CONCEPTS"]
        self.assert_invalid(candidate)

    def test_order_and_identity_are_unique_and_deterministic(self) -> None:
        candidate = copy.deepcopy(PATH_DOCUMENT)
        candidate["items"][1]["order"] = 1
        self.assert_invalid(candidate)

    def test_source_provenance_must_not_be_a_local_absolute_path(self) -> None:
        candidate = copy.deepcopy(PATH_DOCUMENT)
        candidate["items"][0]["source_file"] = "/vol5/private/source.md"
        self.assert_invalid(candidate)


if __name__ == "__main__":
    unittest.main()
