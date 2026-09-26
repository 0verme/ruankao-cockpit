from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from engine.planner import (
    MVP_NEW_LEARNING_MINUTES,
    MVP_REVIEW_MINUTES,
    plan_today,
)
from planner_replay_fixtures import (
    AS_OF,
    DUE_AT,
    DUE_TOPIC,
    OVERDUE_AT,
    OVERDUE_TOPIC,
    build_today_snapshot,
)
from scripts.validate_planner_contract import PlannerContractError, validate_planner_output

ROOT = Path(__file__).resolve().parents[1]


def leaf_topic_ids() -> list[str]:
    taxonomy = json.loads((ROOT / "taxonomy/taxonomy.json").read_text(encoding="utf-8"))
    return sorted(node["id"] for node in taxonomy["nodes"] if node["level"] == 3)


class TodayPlannerReplayTests(unittest.TestCase):
    def setUp(self) -> None:
        self.review_specs = [(OVERDUE_TOPIC, OVERDUE_AT), (DUE_TOPIC, DUE_AT)]

    def make_plan(self, snapshot: dict) -> dict:
        return plan_today(snapshot, snapshot["as_of"], root=ROOT)

    def test_review_only_when_all_leaf_topics_have_learning_evidence(self) -> None:
        snapshot = build_today_snapshot(
            ROOT,
            review_specs=self.review_specs,
            evidenced_topics=leaf_topic_ids(),
        )
        day = self.make_plan(snapshot)["days"][0]
        self.assertEqual([task["task_type"] for task in day["tasks"]], ["review", "review"])
        self.assertEqual([task["target_ref"] for task in day["tasks"]], [
            f"review/topic/{OVERDUE_TOPIC}", f"review/topic/{DUE_TOPIC}",
        ])

    def test_new_learning_only_selects_one_canonical_unlearned_leaf(self) -> None:
        snapshot = build_today_snapshot(ROOT)
        output = self.make_plan(snapshot)
        day = output["days"][0]
        self.assertEqual(len(day["tasks"]), 1)
        self.assertEqual(day["tasks"][0]["task_type"], "new_learning")
        self.assertEqual(day["tasks"][0]["target_kind"], "topic")
        self.assertEqual(day["tasks"][0]["target_ref"], leaf_topic_ids()[0])
        self.assertEqual(day["tasks"][0]["planned_minutes"], MVP_NEW_LEARNING_MINUTES)
        self.assertEqual(output["explain_traces"][0]["reason_code"], "next_unlearned_topic")

    def test_mixed_plan_spends_capacity_on_review_before_new_learning(self) -> None:
        snapshot = build_today_snapshot(ROOT, review_specs=self.review_specs)
        day = self.make_plan(snapshot)["days"][0]
        self.assertEqual([task["task_type"] for task in day["tasks"]], ["review", "review", "new_learning"])
        self.assertEqual(
            [task["planned_minutes"] for task in day["tasks"]],
            [MVP_REVIEW_MINUTES, MVP_REVIEW_MINUTES, MVP_NEW_LEARNING_MINUTES],
        )
        self.assertEqual(day["planned_minutes"], 55)
        self.assertEqual(day["remaining_minutes"], 5)

    def test_capacity_constrained_plan_keeps_unmet_review_and_learning_demand_visible(self) -> None:
        snapshot = build_today_snapshot(ROOT, capacity=15, review_specs=self.review_specs)
        day = self.make_plan(snapshot)["days"][0]
        self.assertEqual(day["planned_minutes"], 15)
        self.assertLessEqual(day["planned_minutes"], day["capacity_minutes"])
        self.assertEqual(day["tasks"][0]["target_ref"], f"review/topic/{OVERDUE_TOPIC}")
        self.assertEqual([demand["demand_type"] for demand in day["unmet_demand"]], ["review", "new_learning"])
        self.assertEqual(day["unmet_demand"][0]["target_ref"], f"review/topic/{DUE_TOPIC}")
        self.assertEqual(day["unmet_demand"][1]["target_ref"], leaf_topic_ids()[0])
        self.assertEqual(len(day["unmet_demand"]), 2)

    def test_zero_capacity_has_no_tasks_and_zero_planned_minutes(self) -> None:
        snapshot = build_today_snapshot(ROOT, capacity=0, review_specs=self.review_specs)
        day = self.make_plan(snapshot)["days"][0]
        self.assertEqual(day["tasks"], [])
        self.assertEqual(day["planned_minutes"], 0)
        self.assertEqual(day["remaining_minutes"], 0)
        self.assertEqual([demand["demand_type"] for demand in day["unmet_demand"]], ["review", "review"])

    def test_review_order_is_overdue_then_due_then_new_learning(self) -> None:
        snapshot = build_today_snapshot(ROOT, review_specs=self.review_specs)
        day = self.make_plan(snapshot)["days"][0]
        self.assertEqual(
            [(task["task_type"], task["target_ref"]) for task in day["tasks"]],
            [
                ("review", f"review/topic/{OVERDUE_TOPIC}"),
                ("review", f"review/topic/{DUE_TOPIC}"),
                ("new_learning", leaf_topic_ids()[0]),
            ],
        )

    def test_review_tie_break_uses_due_instant_then_review_item_id(self) -> None:
        same_due = "2025-12-28T10:00:00+08:00"
        review_specs = [
            ("QUALITY.ATTRIBUTES.AVAILABILITY", same_due),
            ("ARCH.CLOUD_NATIVE.MICROSERVICES", same_due),
            (DUE_TOPIC, DUE_AT),
        ]
        snapshot = build_today_snapshot(ROOT, capacity=60, review_specs=review_specs)
        day = self.make_plan(snapshot)["days"][0]
        review_targets = [task["target_ref"] for task in day["tasks"] if task["task_type"] == "review"]
        self.assertEqual(review_targets, [
            "review/topic/ARCH.CLOUD_NATIVE.MICROSERVICES",
            "review/topic/QUALITY.ATTRIBUTES.AVAILABILITY",
            f"review/topic/{DUE_TOPIC}",
        ])

    def test_repeat_input_has_stable_task_trace_ids_and_semantic_identity(self) -> None:
        snapshot = build_today_snapshot(ROOT, review_specs=self.review_specs)
        first = self.make_plan(snapshot)
        second = self.make_plan(snapshot)
        self.assertEqual(first, second)
        self.assertEqual(
            [task["task_id"] for task in first["days"][0]["tasks"]],
            [task["task_id"] for task in second["days"][0]["tasks"]],
        )

    def test_input_collection_order_does_not_change_plan(self) -> None:
        snapshot = build_today_snapshot(ROOT, review_specs=self.review_specs)
        reordered = copy.deepcopy(snapshot)
        inputs = reordered["inputs"]
        inputs["taxonomy"]["topic_ids"].reverse()
        inputs["capabilities"]["capability_ids"].reverse()
        inputs["user_configuration"]["study_days"].reverse()
        progress = inputs["progress_state"]
        progress["topics"] = dict(reversed(list(progress["topics"].items())))
        progress["capabilities"] = dict(reversed(list(progress["capabilities"].items())))
        review = inputs["mastery_review_state"]
        review["item_order"].reverse()
        review["items"] = dict(reversed(list(review["items"].items())))
        self.assertEqual(self.make_plan(snapshot), self.make_plan(reordered))

    def test_low_accuracy_is_evidence_not_a_new_learning_candidate(self) -> None:
        first_leaf = leaf_topic_ids()[0]
        snapshot = build_today_snapshot(ROOT, evidenced_topics=[first_leaf])
        first_task = self.make_plan(snapshot)["days"][0]["tasks"][0]
        self.assertEqual(first_task["target_ref"], leaf_topic_ids()[1])
        self.assertGreater(snapshot["inputs"]["progress_state"]["topics"][first_leaf]["attempt_count"], 0)
        self.assertEqual(snapshot["inputs"]["progress_state"]["topics"][first_leaf]["accuracy"], 0.0)

    def test_empty_plan_preserves_capacity_when_every_leaf_has_evidence(self) -> None:
        snapshot = build_today_snapshot(ROOT, evidenced_topics=leaf_topic_ids())
        day = self.make_plan(snapshot)["days"][0]
        self.assertEqual(day["tasks"], [])
        self.assertEqual(day["planned_minutes"], 0)
        self.assertEqual(day["remaining_minutes"], 60)

    def test_non_study_day_has_zero_capacity_and_does_not_schedule_tasks(self) -> None:
        snapshot = build_today_snapshot(
            ROOT,
            review_specs=self.review_specs,
            study_days=[1, 2, 3, 5, 6, 7],
        )
        day = self.make_plan(snapshot)["days"][0]
        self.assertFalse(day["study_day"])
        self.assertEqual(day["capacity_minutes"], 0)
        self.assertEqual(day["tasks"], [])
        self.assertEqual(day["planned_minutes"], 0)

    def test_unknown_input_or_output_target_fails_closed(self) -> None:
        snapshot = build_today_snapshot(ROOT)
        broken_input = copy.deepcopy(snapshot)
        broken_input["inputs"]["taxonomy"]["topic_ids"].append("UNKNOWN.TOPIC")
        with self.assertRaises(PlannerContractError) as context:
            self.make_plan(broken_input)
        self.assertEqual(context.exception.category, "invalid_catalog_version")

        output = self.make_plan(snapshot)
        broken_output = copy.deepcopy(output)
        task = broken_output["days"][0]["tasks"][0]
        task["target_ref"] = "UNKNOWN.TOPIC"
        with self.assertRaises(PlannerContractError) as context:
            validate_planner_output(broken_output, snapshot, ROOT)
        self.assertEqual(context.exception.category, "unknown_topic_id")

    def test_explicit_as_of_must_match_snapshot_without_hidden_clock(self) -> None:
        snapshot = build_today_snapshot(ROOT)
        with self.assertRaises(PlannerContractError) as context:
            plan_today(snapshot, "2026-01-02T00:00:00Z", root=ROOT)
        self.assertEqual(context.exception.category, "inconsistent_input")

    def test_realistic_60_minute_today_plan_example(self) -> None:
        snapshot = build_today_snapshot(ROOT, capacity=60, review_specs=self.review_specs)
        output = self.make_plan(snapshot)
        today = output["days"][0]
        self.assertEqual(today["capacity_minutes"], 60)
        self.assertEqual(today["planned_minutes"], 55)
        self.assertEqual(today["remaining_minutes"], 5)
        self.assertEqual(
            [(task["task_type"], task["target_ref"], task["planned_minutes"]) for task in today["tasks"]],
            [
                ("review", f"review/topic/{OVERDUE_TOPIC}", 15),
                ("review", f"review/topic/{DUE_TOPIC}", 15),
                ("new_learning", "ARCH.CLOUD_NATIVE.CONTAINERS_SERVERLESS", 25),
            ],
        )
        reasons = [trace["reason_code"] for trace in output["explain_traces"]]
        self.assertEqual(reasons, ["overdue_review", "due_today_review", "next_unlearned_topic"])


if __name__ == "__main__":
    unittest.main()
