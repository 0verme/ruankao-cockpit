from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from engine.execution import TaskResultError, record_task_result
from engine.planner import plan_today
from engine.progress import replay as progress_replay
from engine.review.replay import replay as review_replay
from task_execution_fixtures import (
    DAY_1,
    DAY_2,
    build_day1_fixture,
    build_planner_input,
    make_attempt,
)
from planner_replay_fixtures import TIMEZONE

ROOT = Path(__file__).resolve().parents[1]


def _plan(root: Path, fixture: dict, progress_events: list, review_events: list, *, as_of: str, capacity: int = 60) -> tuple[dict, dict]:
    planner_input = build_planner_input(
        root,
        fixture,
        progress_events,
        review_events,
        as_of=as_of,
        capacity=capacity,
    )
    return planner_input, plan_today(planner_input, as_of, root=root)


def _task(plan: dict, task_type: str, target_ref: str) -> dict:
    return next(
        task
        for task in plan["days"][0]["tasks"]
        if task["task_type"] == task_type and task["target_ref"] == target_ref
    )


class TaskResultAdapterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = build_day1_fixture(ROOT)
        _, self.plan = _plan(
            ROOT,
            self.fixture,
            self.fixture["progress_events"],
            self.fixture["review_events"],
            as_of=DAY_1,
        )

    def test_new_learning_requires_real_matching_attempt_and_emits_progress_only(self) -> None:
        task = next(task for task in self.plan["days"][0]["tasks"] if task["task_type"] == "new_learning")
        event = make_attempt("explicit-new-learning-attempt", "2026-01-01T11:30:00+08:00", task["target_ref"], correct=False)
        original_plan = copy.deepcopy(self.plan)

        facts = record_task_result(self.plan, task["task_id"], {"progress_event": event})

        self.assertEqual(facts, {"progress_events": [event], "review_events": []})
        self.assertEqual(self.plan, original_plan)
        self.assertFalse(facts["progress_events"][0]["correct"])

    def test_review_requires_matching_topic_attempt_and_explicit_context_identity(self) -> None:
        task = self.plan["days"][0]["tasks"][0]
        topic_id = self.fixture["topic_a"]
        event = make_attempt("explicit-review-attempt", "2026-01-01T11:00:00+08:00", topic_id, correct=True)

        facts = record_task_result(
            self.plan,
            task["task_id"],
            {"progress_event": event, "review_context_event_id": "explicit-review-context"},
        )

        self.assertEqual(facts["progress_events"], [event])
        self.assertEqual(facts["review_events"], [{
            "schema_version": "review-event/v0.1",
            "event_id": "explicit-review-context",
            "event_type": "review_context",
            "source_event_id": "explicit-review-attempt",
            "review_item_id": f"review/topic/{topic_id}",
            "attempt_context": "review",
            "occurred_at": event["occurred_at"],
        }])

    def test_rejects_unknown_unscheduled_and_unmet_demand_tasks(self) -> None:
        with self.assertRaises(TaskResultError) as raised:
            record_task_result(self.plan, "not-in-plan", {"progress_event": {}})
        self.assertEqual(raised.exception.category, "unknown_task")

        _, constrained_plan = _plan(
            ROOT,
            self.fixture,
            self.fixture["progress_events"],
            self.fixture["review_events"],
            as_of=DAY_1,
            capacity=15,
        )
        demand_id = constrained_plan["days"][0]["unmet_demand"][0]["demand_id"]
        with self.assertRaises(TaskResultError) as raised:
            record_task_result(constrained_plan, demand_id, {"progress_event": {}})
        self.assertEqual(raised.exception.category, "task_not_scheduled")

        future_plan = copy.deepcopy(self.plan)
        future_task = copy.deepcopy(future_plan["days"][0]["tasks"][0])
        future_task["task_id"] = "future-day-task"
        future_plan["days"][1]["tasks"] = [future_task]
        with self.assertRaises(TaskResultError) as raised:
            record_task_result(future_plan, "future-day-task", {"progress_event": {}})
        self.assertEqual(raised.exception.category, "task_not_scheduled")

    def test_rejects_topic_mismatch_and_non_fact_completion(self) -> None:
        task = self.plan["days"][0]["tasks"][0]
        wrong_topic = self.fixture["topic_b"]
        wrong_event = make_attempt("wrong-topic-attempt", "2026-01-01T11:00:00+08:00", wrong_topic, correct=True)
        with self.assertRaises(TaskResultError) as raised:
            record_task_result(
                self.plan,
                task["task_id"],
                {"progress_event": wrong_event, "review_context_event_id": "ctx-wrong-topic"},
            )
        self.assertEqual(raised.exception.category, "target_mismatch")

        with self.assertRaises(TaskResultError) as raised:
            record_task_result(self.plan, task["task_id"], {"completed": True})
        self.assertEqual(raised.exception.category, "unsupported_result_type")

    def test_fails_closed_for_question_review_and_case_attempt(self) -> None:
        task = self.plan["days"][0]["tasks"][0]
        question_plan = copy.deepcopy(self.plan)
        question_plan["days"][0]["tasks"][0]["target_ref"] = "review/question/source/q-1"
        event = make_attempt("unsupported-question-review", "2026-01-01T11:00:00+08:00", self.fixture["topic_a"], correct=True)
        with self.assertRaises(TaskResultError) as raised:
            record_task_result(
                question_plan,
                task["task_id"],
                {"progress_event": event, "review_context_event_id": "ctx-unsupported"},
            )
        self.assertEqual(raised.exception.category, "unsupported_execution_target")

        case_event = dict(event, event_type="case_attempt")
        with self.assertRaises(TaskResultError) as raised:
            record_task_result(
                self.plan,
                task["task_id"],
                {"progress_event": case_event, "review_context_event_id": "ctx-case"},
            )
        self.assertEqual(raised.exception.category, "unsupported_result_type")


class DayOneToDayTwoReplanTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = build_day1_fixture(ROOT)
        self.initial_events = copy.deepcopy(self.fixture["progress_events"])
        self.initial_contexts = copy.deepcopy(self.fixture["review_events"])

    def test_real_facts_replay_into_explainable_day_two_plan(self) -> None:
        day1_input, day1_plan = _plan(
            ROOT,
            self.fixture,
            self.initial_events,
            self.initial_contexts,
            as_of=DAY_1,
        )
        day1_tasks = day1_plan["days"][0]["tasks"]
        self.assertEqual(
            [(task["task_type"], task["target_ref"], task["planned_minutes"]) for task in day1_tasks],
            [
                ("review", f"review/topic/{self.fixture['topic_a']}", 15),
                ("review", f"review/topic/{self.fixture['topic_b']}", 15),
                ("new_learning", "ARCH.CLOUD_NATIVE.CONTAINERS_SERVERLESS", 25),
            ],
        )

        task_a = day1_tasks[0]
        task_c = day1_tasks[2]
        review_a = make_attempt(
            "day1-review-a-attempt",
            "2026-01-01T11:00:00+08:00",
            self.fixture["topic_a"],
            correct=True,
        )
        learning_c = make_attempt(
            "day1-new-learning-c-attempt",
            "2026-01-01T11:30:00+08:00",
            task_c["target_ref"],
            correct=False,
        )
        facts_a = record_task_result(
            day1_plan,
            task_a["task_id"],
            {"progress_event": review_a, "review_context_event_id": "day1-review-a-context"},
        )
        facts_c = record_task_result(day1_plan, task_c["task_id"], {"progress_event": learning_c})
        day1_progress_events = self.initial_events + facts_a["progress_events"] + facts_c["progress_events"]
        day1_review_events = self.initial_contexts + facts_a["review_events"] + facts_c["review_events"]

        self.assertEqual([event["event_id"] for event in facts_a["progress_events"]], ["day1-review-a-attempt"])
        self.assertEqual([event["event_id"] for event in facts_a["review_events"]], ["day1-review-a-context"])
        self.assertEqual([event["event_id"] for event in facts_c["progress_events"]], ["day1-new-learning-c-attempt"])
        self.assertEqual(facts_c["review_events"], [])
        self.assertNotIn("day1-review-b-attempt", [event["event_id"] for event in day1_progress_events])
        self.assertEqual([task["target_ref"] for task in day1_tasks if task["task_type"] == "review"], [
            f"review/topic/{self.fixture['topic_a']}", f"review/topic/{self.fixture['topic_b']}",
        ])

        day2_input, day2_plan = _plan(
            ROOT,
            self.fixture,
            day1_progress_events,
            day1_review_events,
            as_of=DAY_2,
        )
        progress_state = day2_input["inputs"]["progress_state"]
        review_state = day2_input["inputs"]["mastery_review_state"]
        a_state = review_state["items"][f"review/topic/{self.fixture['topic_a']}"]
        b_state = review_state["items"][f"review/topic/{self.fixture['topic_b']}"]
        self.assertEqual(a_state["review_interval_days"], 7)
        self.assertEqual(a_state["next_due_local_date"], "2026-01-08")
        self.assertEqual(a_state["review_status"], "scheduled")
        self.assertEqual(b_state["review_status"], "overdue")
        self.assertEqual(progress_state["topics"]["ARCH.CLOUD_NATIVE.CONTAINERS_SERVERLESS"]["incorrect_count"], 1)

        day2_tasks = day2_plan["days"][0]["tasks"]
        self.assertEqual(
            [(task["task_type"], task["target_ref"], task["planned_minutes"]) for task in day2_tasks],
            [
                ("review", f"review/topic/{self.fixture['topic_b']}", 15),
                ("new_learning", "ARCH.CLOUD_NATIVE.EVENT_DRIVEN", 25),
            ],
        )
        self.assertNotIn(f"review/topic/{self.fixture['topic_a']}", [task["target_ref"] for task in day2_tasks])
        self.assertNotIn("ARCH.CLOUD_NATIVE.CONTAINERS_SERVERLESS", [task["target_ref"] for task in day2_tasks])

    def test_no_execution_means_no_new_facts_or_replay_changes(self) -> None:
        _, plan = _plan(
            ROOT,
            self.fixture,
            self.initial_events,
            self.initial_contexts,
            as_of=DAY_1,
        )
        self.assertTrue(plan["days"][0]["tasks"])

        before_progress = progress_replay(
            self.initial_events,
            self.fixture["taxonomy"],
            self.fixture["capabilities"],
        )
        before_review = review_replay(
            self.initial_events,
            self.initial_contexts,
            self.fixture["items"],
            self.fixture["taxonomy"],
            self.fixture["capabilities"],
            as_of=DAY_1,
            timezone=TIMEZONE,
        )
        untouched_events = copy.deepcopy(self.initial_events)
        untouched_contexts = copy.deepcopy(self.initial_contexts)
        after_progress = progress_replay(
            untouched_events,
            self.fixture["taxonomy"],
            self.fixture["capabilities"],
        )
        after_review = review_replay(
            untouched_events,
            untouched_contexts,
            self.fixture["items"],
            self.fixture["taxonomy"],
            self.fixture["capabilities"],
            as_of=DAY_1,
            timezone=TIMEZONE,
        )
        self.assertEqual(untouched_events, self.initial_events)
        self.assertEqual(untouched_contexts, self.initial_contexts)
        self.assertEqual(after_progress, before_progress)
        self.assertEqual(after_review, before_review)

    def test_review_failure_uses_existing_retry_policy_for_day_two(self) -> None:
        _, day1_plan = _plan(
            ROOT,
            self.fixture,
            self.initial_events,
            self.initial_contexts,
            as_of=DAY_1,
        )
        task_a = day1_plan["days"][0]["tasks"][0]
        failed_attempt = make_attempt(
            "day1-review-a-failure",
            "2026-01-01T11:00:00+08:00",
            self.fixture["topic_a"],
            correct=False,
        )
        facts = record_task_result(
            day1_plan,
            task_a["task_id"],
            {"progress_event": failed_attempt, "review_context_event_id": "day1-review-a-failure-context"},
        )
        events = self.initial_events + facts["progress_events"]
        contexts = self.initial_contexts + facts["review_events"]
        day2_input, day2_plan = _plan(ROOT, self.fixture, events, contexts, as_of=DAY_2)
        a_state = day2_input["inputs"]["mastery_review_state"]["items"][f"review/topic/{self.fixture['topic_a']}"]

        self.assertEqual(a_state["failure_count"], 1)
        self.assertEqual(a_state["mastery_state"], "learning")
        self.assertEqual(a_state["review_interval_days"], 1)
        self.assertEqual(a_state["next_due_local_date"], "2026-01-02")
        self.assertEqual(a_state["review_status"], "due")
        day2_reviews = [task["target_ref"] for task in day2_plan["days"][0]["tasks"] if task["task_type"] == "review"]
        self.assertEqual(day2_reviews, [
            f"review/topic/{self.fixture['topic_b']}",
            f"review/topic/{self.fixture['topic_a']}",
        ])


if __name__ == "__main__":
    unittest.main()
