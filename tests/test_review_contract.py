from __future__ import annotations

import copy
import json
from pathlib import Path
import random
import unittest

from engine.review import (
    EVIDENCE_SCHEMA_VERSION,
    ITEM_SCHEMA_VERSION,
    REVIEW_EVENT_SCHEMA_VERSION,
    ReviewValidationError,
    project_review_evidence,
    validate_review_evidence,
    validate_review_events,
    validate_review_items,
)


ROOT = Path(__file__).resolve().parents[1]
TAXONOMY = json.loads((ROOT / "taxonomy/taxonomy.json").read_text(encoding="utf-8"))
CAPABILITIES = json.loads((ROOT / "taxonomy/capabilities.json").read_text(encoding="utf-8"))


QUESTION_COMMIT = "a" * 40
TOPIC_COMMIT = "b" * 40
CAPABILITY_COMMIT = "c" * 40


def question_reference(question_id: str, *, path: str = "fixtures/question-index.json") -> dict:
    return {
        "source_id": "synthetic-bank",
        "source_commit": QUESTION_COMMIT,
        "source_path": path,
        "source_question_id": question_id,
    }


def progress_comprehensive() -> dict:
    return {
        "event_id": "attempt-001",
        "schema_version": "progress-event/v0.1",
        "event_type": "comprehensive_attempt",
        "occurred_at": "2026-01-01T10:00:00+08:00",
        "question": question_reference("q-001"),
        "topics": ["DATA.DATABASE.RELATIONAL"],
        "correct": True,
    }


def progress_case_scored() -> dict:
    return {
        "event_id": "case-001",
        "schema_version": "progress-event/v0.1",
        "event_type": "case_attempt",
        "occurred_at": "2026-01-02T10:00:00+08:00",
        "question": question_reference("q-002"),
        "topics": ["DATA.DATABASE.RELATIONAL"],
        "capabilities": ["CASE.DATA_DESIGN"],
        "score_earned": 7,
        "score_possible": 10,
        "capability_scores": [
            {
                "capability_id": "CASE.DATA_DESIGN",
                "score_earned": 4,
                "score_possible": 6,
            }
        ],
    }


def progress_case_without_capability_score() -> dict:
    event = progress_case_scored()
    event["event_id"] = "case-002"
    event["occurred_at"] = "2026-01-03T10:00:00+08:00"
    event["question"] = question_reference("q-003")
    event.pop("score_earned")
    event.pop("score_possible")
    event.pop("capability_scores")
    return event


def item_topic() -> dict:
    return {
        "schema_version": ITEM_SCHEMA_VERSION,
        "review_item_id": "review/topic/DATA.DATABASE.RELATIONAL",
        "item_kind": "topic",
        "canonical_ref": {
            "topic_id": "DATA.DATABASE.RELATIONAL",
            "taxonomy_version": "0.1",
        },
        "source_reference": {
            "source_id": "synthetic-catalog",
            "source_commit": TOPIC_COMMIT,
            "source_path": "fixtures/topic-index.json",
            "source_value": "DATA.DATABASE.RELATIONAL",
        },
        "display_name": "关系数据库",
    }


def item_question(question_id: str = "q-001") -> dict:
    return {
        "schema_version": ITEM_SCHEMA_VERSION,
        "review_item_id": f"review/question/synthetic-bank/{question_id}",
        "item_kind": "question",
        "canonical_ref": {
            "source_id": "synthetic-bank",
            "source_question_id": question_id,
        },
        "source_reference": question_reference(question_id),
        "display_name": f"synthetic question {question_id}",
    }


def item_capability() -> dict:
    return {
        "schema_version": ITEM_SCHEMA_VERSION,
        "review_item_id": "review/case_capability/CASE.DATA_DESIGN",
        "item_kind": "case_capability",
        "canonical_ref": {
            "capability_id": "CASE.DATA_DESIGN",
            "taxonomy_version": "0.1",
        },
        "source_reference": {
            "source_id": "synthetic-catalog",
            "source_commit": CAPABILITY_COMMIT,
            "source_path": "fixtures/capability-index.json",
            "source_value": "CASE.DATA_DESIGN",
        },
        "display_name": "数据方案设计",
    }


def all_items() -> list[dict]:
    return [item_topic(), item_question("q-001"), item_question("q-002"), item_capability()]


def context_event(source: dict, review_item_id: str, *, event_id: str = "ctx-001", context: str = "review") -> dict:
    return {
        "schema_version": REVIEW_EVENT_SCHEMA_VERSION,
        "event_id": event_id,
        "event_type": "review_context",
        "source_event_id": source["event_id"],
        "review_item_id": review_item_id,
        "attempt_context": context,
        "occurred_at": source["occurred_at"],
    }


class ReviewContractTests(unittest.TestCase):
    def assert_category(self, category: str, function) -> None:
        with self.assertRaises(ReviewValidationError) as context:
            function()
        self.assertEqual(context.exception.category, category, str(context.exception))

    def catalog(self, items: list[dict] | None = None):
        return validate_review_items(items or all_items(), TAXONOMY, CAPABILITIES)

    def test_item_identity_is_stable_across_display_and_source_changes(self) -> None:
        original = item_question()
        changed = copy.deepcopy(original)
        changed["display_name"] = "题面名称更新"
        changed["source_reference"]["source_commit"] = "d" * 40
        changed["source_reference"]["source_path"] = "renamed/question-index.json"
        first = self.catalog([original])
        second = self.catalog([changed])
        self.assertEqual(set(first.items), {"review/question/synthetic-bank/q-001"})
        self.assertEqual(set(first.items), set(second.items))

    def test_unknown_item_kind_is_rejected(self) -> None:
        item = item_topic()
        item["item_kind"] = "essay_capability"
        self.assert_category("unknown_item_kind", lambda: self.catalog([item]))

    def test_missing_canonical_reference_is_rejected(self) -> None:
        item = item_topic()
        item.pop("canonical_ref")
        self.assert_category("missing_canonical_reference", lambda: self.catalog([item]))

    def test_missing_source_reference_is_rejected(self) -> None:
        item = item_capability()
        item.pop("source_reference")
        self.assert_category("missing_source_reference", lambda: self.catalog([item]))

    def test_duplicate_item_is_rejected(self) -> None:
        item = item_question()
        self.assert_category("duplicate_review_item", lambda: self.catalog([item, copy.deepcopy(item)]))

    def test_question_identity_does_not_depend_on_question_text(self) -> None:
        first = item_question()
        second = copy.deepcopy(first)
        first["display_name"] = "old text is not identity"
        second["display_name"] = "new text is not identity"
        first_catalog = self.catalog([first])
        second_catalog = self.catalog([second])
        self.assertEqual(
            next(iter(first_catalog.items)),
            "review/question/synthetic-bank/q-001",
        )
        self.assertEqual(set(first_catalog.items), set(second_catalog.items))

    def test_unknown_topic_and_capability_are_rejected(self) -> None:
        topic = item_topic()
        topic["canonical_ref"]["topic_id"] = "UNKNOWN.TOPIC"
        topic["review_item_id"] = "review/topic/UNKNOWN.TOPIC"
        self.assert_category("unknown_topic_id", lambda: self.catalog([topic]))

        capability = item_capability()
        capability["canonical_ref"]["capability_id"] = "CASE.UNKNOWN"
        capability["review_item_id"] = "review/case_capability/CASE.UNKNOWN"
        self.assert_category("unknown_capability_id", lambda: self.catalog([capability]))

    def test_explicit_context_is_required_and_initial_review_are_not_guessed(self) -> None:
        source = progress_comprehensive()
        items = [item_question()]
        self.assertEqual(
            project_review_evidence([source], [], items, TAXONOMY, CAPABILITIES),
            [],
        )
        initial = project_review_evidence(
            [source],
            [context_event(source, "review/question/synthetic-bank/q-001", context="initial_learning")],
            items,
            TAXONOMY,
            CAPABILITIES,
        )
        self.assertEqual(initial[0]["attempt_context"], "initial_learning")
        self.assertEqual(initial[0]["evidence_value"], {"correct": True})

        review = project_review_evidence(
            [source],
            [context_event(source, "review/question/synthetic-bank/q-001", context="review")],
            items,
            TAXONOMY,
            CAPABILITIES,
        )
        self.assertEqual(review[0]["attempt_context"], "review")
        self.assertEqual(review[0]["evidence_id"], initial[0]["evidence_id"])

    def test_duplicate_initial_and_review_context_is_rejected(self) -> None:
        source = progress_comprehensive()
        catalog = self.catalog([item_question()])
        contexts = [
            context_event(source, "review/question/synthetic-bank/q-001", event_id="ctx-a", context="initial_learning"),
            context_event(source, "review/question/synthetic-bank/q-001", event_id="ctx-b", context="review"),
        ]
        self.assert_category(
            "duplicate_review_context",
            lambda: validate_review_events(contexts, [source], catalog),
        )

    def test_evidence_item_kind_mismatch_is_rejected(self) -> None:
        source = progress_comprehensive()
        items = [item_question()]
        evidence = project_review_evidence(
            [source],
            [context_event(source, "review/question/synthetic-bank/q-001")],
            items,
            TAXONOMY,
            CAPABILITIES,
        )
        evidence[0]["item_kind"] = "topic"
        self.assert_category(
            "evidence_item_mismatch",
            lambda: validate_review_evidence(evidence, self.catalog(items), [source]),
        )

    def test_insufficient_capability_evidence_is_explicit(self) -> None:
        source = progress_case_without_capability_score()
        item = item_capability()
        evidence = project_review_evidence(
            [source],
            [context_event(source, item["review_item_id"])],
            [item],
            TAXONOMY,
            CAPABILITIES,
        )
        self.assertEqual(evidence[0]["evidence_status"], "insufficient_evidence")
        self.assertIsNone(evidence[0]["evidence_value"])
        self.assertEqual(evidence[0]["evidence_kind"], "case_capability_score_missing")

    def test_case_aggregate_is_not_copied_to_topic_or_capability(self) -> None:
        source = progress_case_scored()
        topic = item_topic()
        evidence = project_review_evidence(
            [source],
            [context_event(source, topic["review_item_id"])],
            [topic],
            TAXONOMY,
            CAPABILITIES,
        )
        self.assertEqual(evidence[0]["evidence_status"], "unsupported")
        self.assertIsNone(evidence[0]["evidence_value"])

    def test_source_path_traversal_is_rejected(self) -> None:
        item = item_topic()
        item["source_reference"]["source_path"] = "../outside.json"
        self.assert_category("forbidden_path", lambda: self.catalog([item]))

    def test_timezone_naive_evidence_timestamp_is_rejected(self) -> None:
        source = progress_comprehensive()
        items = [item_question()]
        evidence = project_review_evidence(
            [source],
            [context_event(source, "review/question/synthetic-bank/q-001")],
            items,
            TAXONOMY,
            CAPABILITIES,
        )
        evidence[0]["occurred_at"] = "2026-01-01T02:00:00"
        self.assert_category(
            "invalid_timestamp",
            lambda: validate_review_evidence(evidence, self.catalog(items), [source]),
        )

    def test_missing_evidence_source_reference_is_rejected(self) -> None:
        source = progress_comprehensive()
        items = [item_question()]
        evidence = project_review_evidence(
            [source],
            [context_event(source, "review/question/synthetic-bank/q-001")],
            items,
            TAXONOMY,
            CAPABILITIES,
        )
        evidence[0].pop("source_reference")
        self.assert_category(
            "missing_source_reference",
            lambda: validate_review_evidence(evidence, self.catalog(items), [source]),
        )

    def test_study_session_review_activity_is_not_item_evidence(self) -> None:
        source = {
            "event_id": "session-001",
            "schema_version": "progress-event/v0.1",
            "event_type": "study_session",
            "occurred_at": "2026-01-01T10:00:00+08:00",
            "session_id": "session-001",
            "started_at": "2026-01-01T10:00:00+08:00",
            "duration_minutes": 30,
            "activity_type": "review",
        }
        self.assert_category(
            "evidence_item_mismatch",
            lambda: project_review_evidence(
                [source],
                [context_event(source, "review/question/synthetic-bank/q-001")],
                [item_question()],
                TAXONOMY,
                CAPABILITIES,
            ),
        )

    def test_policy_fields_are_not_evidence(self) -> None:
        source = progress_comprehensive()
        items = [item_question()]
        evidence = project_review_evidence(
            [source],
            [context_event(source, "review/question/synthetic-bank/q-001")],
            items,
            TAXONOMY,
            CAPABILITIES,
        )
        evidence[0]["evidence_value"] = {"success": True}
        self.assert_category(
            "policy_field_in_evidence",
            lambda: validate_review_evidence(evidence, self.catalog(items), [source]),
        )

    def test_evidence_is_order_independent_and_uses_utc_instant(self) -> None:
        source_a = progress_comprehensive()
        source_b = progress_case_scored()
        items = [item_question("q-001"), item_question("q-002")]
        contexts = [
            context_event(source_a, "review/question/synthetic-bank/q-001", event_id="ctx-a"),
            context_event(source_b, "review/question/synthetic-bank/q-002", event_id="ctx-b"),
        ]
        first = project_review_evidence(
            [source_a, source_b], contexts, items, TAXONOMY, CAPABILITIES
        )
        shuffled_sources = [source_b, source_a]
        shuffled_contexts = list(contexts)
        random.Random(7).shuffle(shuffled_contexts)
        second = project_review_evidence(
            shuffled_sources, shuffled_contexts, items, TAXONOMY, CAPABILITIES
        )
        self.assertEqual(first, second)
        self.assertEqual(first[0]["occurred_at"], "2026-01-01T02:00:00Z")
        self.assertEqual(first[1]["occurred_at"], "2026-01-02T02:00:00Z")
        self.assertEqual(first[1]["evidence_value"], {"score_earned": 7, "score_possible": 10})
        self.assertEqual(first[0]["schema_version"], EVIDENCE_SCHEMA_VERSION)


if __name__ == "__main__":
    unittest.main()
