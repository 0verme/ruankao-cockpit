from __future__ import annotations

import copy
import json
from pathlib import Path
import random
import unittest

from engine.review import (
    EVIDENCE_SCHEMA_VERSION,
    ITEM_SCHEMA_VERSION,
    MASTERY_REVIEW_STATE_SCHEMA_VERSION,
    MASTERY_POLICY_FULL_VERSION,
    OUTCOME_ADAPTER_FULL_VERSION,
    REVIEW_EVENT_SCHEMA_VERSION,
    REVIEW_POLICY_FULL_VERSION,
    MasteryReviewReplayError,
    replay,
)
from engine.rules import ReviewPolicyError


ROOT = Path(__file__).resolve().parents[1]
TAXONOMY = json.loads((ROOT / "taxonomy/taxonomy.json").read_text(encoding="utf-8"))
CAPABILITIES = json.loads((ROOT / "taxonomy/capabilities.json").read_text(encoding="utf-8"))
QUESTION_COMMIT = "a" * 40
TOPIC_COMMIT = "b" * 40


def question_reference(question_id: str = "q-001") -> dict:
    return {
        "source_id": "synthetic-bank",
        "source_commit": QUESTION_COMMIT,
        "source_path": "fixtures/question-index.json",
        "source_question_id": question_id,
    }


def question_item(question_id: str = "q-001") -> dict:
    return {
        "schema_version": ITEM_SCHEMA_VERSION,
        "review_item_id": f"review/question/synthetic-bank/{question_id}",
        "item_kind": "question",
        "canonical_ref": {
            "source_id": "synthetic-bank",
            "source_question_id": question_id,
        },
        "source_reference": question_reference(question_id),
        "display_name": f"synthetic {question_id}",
    }


def topic_item(topic_id: str = "DATA.DATABASE.RELATIONAL") -> dict:
    return {
        "schema_version": ITEM_SCHEMA_VERSION,
        "review_item_id": f"review/topic/{topic_id}",
        "item_kind": "topic",
        "canonical_ref": {"topic_id": topic_id, "taxonomy_version": "0.1"},
        "source_reference": {
            "source_id": "synthetic-catalog",
            "source_commit": TOPIC_COMMIT,
            "source_path": "fixtures/topic-index.json",
            "source_value": topic_id,
        },
    }


def comprehensive(
    event_id: str,
    when: str,
    *,
    correct: bool = True,
    question_id: str = "q-001",
) -> dict:
    event = {
        "event_id": event_id,
        "schema_version": "progress-event/v0.1",
        "event_type": "comprehensive_attempt",
        "occurred_at": when,
        "question": question_reference(question_id),
        "topics": ["DATA.DATABASE.RELATIONAL"],
        "correct": correct,
    }
    if not correct:
        event["error_cause"] = "knowledge_gap"
    return event


def case_score(event_id: str, when: str, *, question_id: str = "q-002") -> dict:
    return {
        "event_id": event_id,
        "schema_version": "progress-event/v0.1",
        "event_type": "case_attempt",
        "occurred_at": when,
        "question": question_reference(question_id),
        "topics": ["DATA.DATABASE.RELATIONAL"],
        "capabilities": ["CASE.DATA_DESIGN"],
        "score_earned": 0,
        "score_possible": 10,
        "capability_scores": [
            {
                "capability_id": "CASE.DATA_DESIGN",
                "score_earned": 0,
                "score_possible": 4,
            }
        ],
    }


def context(source: dict, item_id: str, event_id: str | None = None, *, attempt_context: str = "review") -> dict:
    return {
        "schema_version": REVIEW_EVENT_SCHEMA_VERSION,
        "event_id": event_id or f"ctx-{source['event_id']}",
        "event_type": "review_context",
        "source_event_id": source["event_id"],
        "review_item_id": item_id,
        "attempt_context": attempt_context,
        "occurred_at": source["occurred_at"],
    }


def run_replay(
    progress_events: list[dict],
    review_events: list[dict],
    items: list[dict],
    *,
    as_of: str,
    timezone: str = "Asia/Shanghai",
) -> dict:
    return replay(
        progress_events,
        review_events,
        items,
        TAXONOMY,
        CAPABILITIES,
        as_of=as_of,
        timezone=timezone,
    )


class ReplayOutputTests(unittest.TestCase):
    def test_empty_item_is_rebuilt_with_two_independent_axes(self) -> None:
        item = question_item()
        state = run_replay([], [], [item], as_of="2026-03-01T10:00:00+08:00")
        projected = state["items"][item["review_item_id"]]

        self.assertEqual(state["schema_version"], MASTERY_REVIEW_STATE_SCHEMA_VERSION)
        self.assertEqual(state["review_model_version"], "review-model/v0.1")
        self.assertEqual(state["review_event_schema_version"], REVIEW_EVENT_SCHEMA_VERSION)
        self.assertEqual(state["review_evidence_version"], EVIDENCE_SCHEMA_VERSION)
        self.assertEqual(state["progress_event_schema_version"], "progress-event/v0.1")
        self.assertEqual(state["progress_replay_version"], "progress-replay/v0.1")
        self.assertEqual(state["mastery_policy_version"], MASTERY_POLICY_FULL_VERSION)
        self.assertEqual(state["review_policy_version"], REVIEW_POLICY_FULL_VERSION)
        self.assertEqual(state["timezone"], "Asia/Shanghai")
        self.assertEqual(state["schedule_timezone"], "Asia/Shanghai")
        self.assertEqual(state["outcome_adapter"]["adapter"], OUTCOME_ADAPTER_FULL_VERSION)

        self.assertEqual(projected["item_kind"], "question")
        self.assertEqual(projected["canonical_ref"], item["canonical_ref"])
        self.assertEqual(projected["mastery_state"], "new")
        self.assertEqual(projected["review_status"], "not_scheduled")
        self.assertEqual(projected["evidence"], [])
        self.assertEqual(projected["evidence_ids"], [])
        self.assertEqual(state["review"]["due_count"], 0)
        self.assertEqual(state["mastery"]["new_count"], 1)

        schema = json.loads((ROOT / "data/review/mastery-review-state.schema.json").read_text())
        self.assertEqual(set(state), set(schema["properties"]))
        self.assertEqual(
            set(projected),
            set(schema["$defs"]["itemState"]["properties"]),
        )

    def test_comprehensive_fact_drives_mastery_and_schedule(self) -> None:
        item = question_item()
        source = comprehensive("attempt-001", "2026-03-01T10:00:00+08:00")
        state = run_replay(
            [source],
            [context(source, item["review_item_id"], attempt_context="initial_learning")],
            [item],
            as_of="2026-03-02T08:00:00+08:00",
        )
        projected = state["items"][item["review_item_id"]]

        self.assertEqual(projected["mastery_state"], "learning")
        self.assertEqual(projected["mastery_reason"], "success_enters_learning")
        self.assertEqual(projected["review_status"], "due")
        self.assertEqual(projected["review_status_reason"], "due_on_due_local_date")
        self.assertEqual(projected["scheduling_reason"], "success_schedules_ladder_interval")
        self.assertEqual(projected["review_interval_days"], 1)
        self.assertEqual(projected["next_due_at"], "2026-03-01T16:00:00+00:00")
        self.assertEqual(projected["next_due_local_date"], "2026-03-02")
        self.assertEqual(projected["last_review_at"], "2026-03-01T02:00:00+00:00")
        self.assertEqual(projected["evidence"][0]["policy_outcome"], "success")
        self.assertEqual(projected["evidence"][0]["policy_outcome_reason"], "comprehensive_correctness_fact")
        self.assertEqual(state["review"]["due_count"], 1)
        self.assertEqual(state["review"]["due_today_count"], 1)

    def test_three_spaced_successes_master_and_failure_demotes(self) -> None:
        item = question_item()
        sources = [
            comprehensive("attempt-001", "2026-03-01T10:00:00+08:00"),
            comprehensive("attempt-002", "2026-03-02T10:00:00+08:00"),
            comprehensive("attempt-003", "2026-03-05T10:00:00+08:00"),
            comprehensive("attempt-004", "2026-03-12T10:00:00+08:00", correct=False),
        ]
        contexts = [context(source, item["review_item_id"]) for source in sources]

        mastered = run_replay(
            sources[:3],
            contexts[:3],
            [item],
            as_of="2026-03-05T10:00:00+08:00",
        )["items"][item["review_item_id"]]
        demoted = run_replay(
            sources,
            contexts,
            [item],
            as_of="2026-03-12T10:00:00+08:00",
        )["items"][item["review_item_id"]]

        self.assertEqual(mastered["mastery_state"], "mastered")
        self.assertEqual(mastered["review_status"], "scheduled")
        self.assertEqual(mastered["review_interval_days"], 7)
        self.assertEqual(demoted["mastery_state"], "learning")
        self.assertEqual(demoted["mastery_reason"], "mastered_failure_demotes_learning")
        self.assertEqual(demoted["review_interval_days"], 1)
        self.assertEqual(demoted["failure_count"], 1)
        self.assertEqual(demoted["consecutive_success_day_count"], 0)
        self.assertEqual(demoted["scheduling_reason"], "failure_schedules_retry_interval")

    def test_score_fact_is_retained_without_fabricating_failure(self) -> None:
        item = question_item("q-002")
        source = case_score("case-001", "2026-03-01T10:00:00+08:00")
        state = run_replay(
            [source],
            [context(source, item["review_item_id"])],
            [item],
            as_of="2026-03-02T10:00:00+08:00",
        )
        projected = state["items"][item["review_item_id"]]
        trace = projected["evidence"][0]

        self.assertEqual(projected["mastery_state"], "new")
        self.assertEqual(projected["review_status"], "not_scheduled")
        self.assertEqual(projected["evaluated_evidence_count"], 0)
        self.assertEqual(projected["failure_count"], 0)
        self.assertEqual(projected["insufficient_evidence_count"], 1)
        self.assertEqual(trace["evidence_status"], "supported")
        self.assertEqual(trace["evidence_value"], {"score_earned": 0, "score_possible": 10})
        self.assertEqual(trace["policy_outcome"], "insufficient")
        self.assertEqual(trace["policy_outcome_reason"], "score_outcome_mapping_unfrozen")

    def test_due_and_overdue_are_item_counts(self) -> None:
        due_item = question_item("q-001")
        overdue_item = question_item("q-002")
        due_source = comprehensive("attempt-due", "2026-03-01T10:00:00+08:00", question_id="q-001")
        overdue_source = comprehensive("attempt-overdue", "2026-02-20T10:00:00+08:00", question_id="q-002")
        state = run_replay(
            [due_source, overdue_source],
            [
                context(due_source, due_item["review_item_id"]),
                context(overdue_source, overdue_item["review_item_id"]),
            ],
            [due_item, overdue_item],
            as_of="2026-03-02T08:00:00+08:00",
        )
        self.assertEqual(state["review"]["due_today_count"], 1)
        self.assertEqual(state["review"]["overdue_count"], 1)
        self.assertEqual(state["review"]["due_count"], 2)
        self.assertEqual(
            state["review"]["due_count"],
            sum(
                item["review_status"] in {"due", "overdue"}
                for item in state["items"].values()
            ),
        )


class ReplayDeterminismTests(unittest.TestCase):
    def test_repeat_shuffle_and_input_mutation(self) -> None:
        item = question_item()
        sources = [
            comprehensive("attempt-b", "2026-03-01T10:00:00+08:00"),
            comprehensive("attempt-a", "2026-03-01T10:00:00+08:00", correct=False),
        ]
        contexts = [context(source, item["review_item_id"]) for source in sources]
        original_sources = copy.deepcopy(sources)
        original_contexts = copy.deepcopy(contexts)
        baseline = run_replay(
            sources,
            contexts,
            [item],
            as_of="2026-03-02T08:00:00+08:00",
        )
        self.assertEqual(sources, original_sources)
        self.assertEqual(contexts, original_contexts)
        self.assertEqual(
            baseline,
            run_replay(sources, contexts, [item], as_of="2026-03-02T08:00:00+08:00"),
        )

        shuffled_sources = copy.deepcopy(sources)
        shuffled_contexts = copy.deepcopy(contexts)
        random.Random(7).shuffle(shuffled_sources)
        random.Random(11).shuffle(shuffled_contexts)
        self.assertEqual(
            baseline,
            run_replay(
                shuffled_sources,
                shuffled_contexts,
                [copy.deepcopy(item)],
                as_of="2026-03-02T08:00:00+08:00",
            ),
        )
        projected = baseline["items"][item["review_item_id"]]
        self.assertEqual(projected["last_evidence_id"], "evidence/attempt-b/" + item["review_item_id"])
        self.assertEqual(projected["mastery_reason"], "learning_success_below_mastery")

    def test_taxonomy_capability_and_item_inputs_are_not_mutated(self) -> None:
        item = question_item()
        source = comprehensive("attempt-001", "2026-03-01T10:00:00+08:00")
        review = context(source, item["review_item_id"])
        original_taxonomy = copy.deepcopy(TAXONOMY)
        original_capabilities = copy.deepcopy(CAPABILITIES)
        original_item = copy.deepcopy(item)

        run_replay(
            [source],
            [review],
            [item],
            as_of="2026-03-02T08:00:00+08:00",
        )

        self.assertEqual(TAXONOMY, original_taxonomy)
        self.assertEqual(CAPABILITIES, original_capabilities)
        self.assertEqual(item, original_item)

    def test_same_instant_offsets_produce_identical_state(self) -> None:
        item = question_item()
        source_a = comprehensive("attempt-001", "2026-03-01T10:00:00+08:00")
        source_b = comprehensive("attempt-002", "2026-03-02T10:00:00+08:00")
        first = run_replay(
            [source_a, source_b],
            [context(source_a, item["review_item_id"]), context(source_b, item["review_item_id"])],
            [item],
            as_of="2026-03-03T08:00:00+08:00",
        )
        rewritten_a = copy.deepcopy(source_a)
        rewritten_b = copy.deepcopy(source_b)
        rewritten_a["occurred_at"] = "2026-03-01T02:00:00Z"
        rewritten_b["occurred_at"] = "2026-03-02T02:00:00Z"
        second = run_replay(
            [rewritten_b, rewritten_a],
            [
                context(rewritten_b, item["review_item_id"], event_id="ctx-attempt-002"),
                context(rewritten_a, item["review_item_id"], event_id="ctx-attempt-001"),
            ],
            [item],
            as_of="2026-03-03T00:00:00Z",
        )
        self.assertEqual(first, second)

    def test_same_timestamp_uses_source_event_id_tie_breaker(self) -> None:
        item = question_item()
        success_source = comprehensive("attempt-a", "2026-03-01T10:00:00+08:00", correct=True)
        failure_source = comprehensive("attempt-b", "2026-03-01T10:00:00+08:00", correct=False)
        first = run_replay(
            [failure_source, success_source],
            [
                context(failure_source, item["review_item_id"]),
                context(success_source, item["review_item_id"]),
            ],
            [item],
            as_of="2026-03-01T10:00:00+08:00",
        )
        second = run_replay(
            [success_source, failure_source],
            [
                context(success_source, item["review_item_id"]),
                context(failure_source, item["review_item_id"]),
            ],
            [item],
            as_of="2026-03-01T10:00:00+08:00",
        )
        self.assertEqual(first, second)
        projected = first["items"][item["review_item_id"]]
        self.assertEqual(projected["last_evidence_id"], "evidence/attempt-b/" + item["review_item_id"])
        self.assertEqual(projected["mastery_reason"], "learning_failure_keeps_learning")


class ReplayBoundaryTests(unittest.TestCase):
    def test_future_evidence_is_rejected(self) -> None:
        item = question_item()
        source = comprehensive("attempt-future", "2026-03-02T10:00:00+08:00")
        with self.assertRaises(ReviewPolicyError) as raised:
            run_replay(
                [source],
                [context(source, item["review_item_id"])],
                [item],
                as_of="2026-03-01T10:00:00+08:00",
            )
        self.assertEqual(raised.exception.category, "future_evidence")

    def test_naive_as_of_and_timezone_are_rejected(self) -> None:
        item = question_item()
        with self.assertRaises(MasteryReviewReplayError) as raised:
            replay([], [], [item], TAXONOMY, CAPABILITIES, as_of="2026-03-01T10:00:00", timezone="UTC")
        self.assertEqual(raised.exception.category, "invalid_timestamp")

        with self.assertRaises(MasteryReviewReplayError) as raised:
            replay([], [], [item], TAXONOMY, CAPABILITIES, as_of="2026-03-01T10:00:00Z")
        self.assertEqual(raised.exception.category, "invalid_timezone")

    def test_unknown_item_and_duplicate_progress_id_are_rejected(self) -> None:
        source = comprehensive("attempt-001", "2026-03-01T10:00:00+08:00")
        with self.assertRaises(Exception) as raised:
            run_replay(
                [source],
                [context(source, "review/question/synthetic-bank/unknown")],
                [question_item()],
                as_of="2026-03-01T10:00:00+08:00",
            )
        self.assertEqual(getattr(raised.exception, "category", None), "unknown_review_item")

        with self.assertRaises(Exception) as raised:
            run_replay(
                [source, copy.deepcopy(source)],
                [],
                [question_item()],
                as_of="2026-03-01T10:00:00+08:00",
            )
        self.assertEqual(getattr(raised.exception, "category", None), "duplicate_event_id")


if __name__ == "__main__":
    unittest.main()
