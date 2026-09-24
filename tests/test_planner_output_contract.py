from __future__ import annotations

import copy
from datetime import datetime
from pathlib import Path
import unittest

from engine.rules.review_policy_v01 import resolve_timezone
from planner_contract_fixtures import build_minimal_snapshot
from planner_output_fixtures import build_minimal_output
from scripts.validate_planner_contract import (
    PlannerContractError,
    validate_output_fixture_set,
    validate_planner_output,
)


ROOT = Path(__file__).resolve().parents[1]
TOPIC_REF = "review/topic/DATA.DATABASE.RELATIONAL"
POLICY = {"policy_id": "planner-policy/contract-fixture", "policy_version": "v0.1"}


def add_task(output: dict, *, planned_minutes: int = 10) -> None:
    task_id = "task-fixture-review-topic-day0"
    trace_id = "trace-fixture-task"
    task = {
        "task_id": task_id,
        "task_type": "review",
        "target_kind": "review_item",
        "target_ref": TOPIC_REF,
        "planned_minutes": planned_minutes,
        "explain_trace_id": trace_id,
    }
    trace = {
        "trace_id": trace_id,
        "subject_kind": "plan_task",
        "subject_id": task_id,
        "decision_category": "task_scheduled",
        "reason_code": "contract_fixture",
        "planner_policy": copy.deepcopy(POLICY),
        "input_references": ["/inputs/mastery_review_state/items/review~1topic~1DATA.DATABASE.RELATIONAL/review_status"],
        "target_kind": "review_item",
        "target_ref": TOPIC_REF,
        "structured_inputs": {"fixture_kind": "shape_only"},
    }
    output["days"][0]["tasks"] = [task]
    output["days"][0]["planned_minutes"] = planned_minutes
    output["days"][0]["remaining_minutes"] -= planned_minutes
    output["explain_traces"] = [trace]


class PlannerOutputContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.input_snapshot, self.output = build_minimal_output(ROOT)

    def assert_output_category(self, category: str, output: dict | None = None, input_snapshot: dict | None = None) -> None:
        with self.assertRaises(PlannerContractError) as context:
            validate_planner_output(output or self.output, input_snapshot or self.input_snapshot, ROOT)
        self.assertEqual(context.exception.category, category, str(context.exception))

    def test_output_fixture_matrix_covers_valid_shapes_and_rejections(self) -> None:
        result = validate_output_fixture_set(ROOT)
        self.assertEqual(result["fixtures"], 17)
        self.assertEqual(result["accepted"], 4)
        self.assertEqual(result["rejected"], 13)
        self.assertEqual(result["rejection_categories"]["capacity_invariant"], 2)
        self.assertEqual(result["rejection_categories"]["invalid_explain_trace"], 1)
        self.assertEqual(result["rejection_categories"]["invalid_horizon"], 2)
        self.assertEqual(result["rejection_categories"]["unknown_review_item"], 1)

    def test_empty_and_zero_capacity_projection_are_valid(self) -> None:
        self.assertEqual(validate_planner_output(self.output, self.input_snapshot, ROOT)["days"][0]["tasks"], [])
        self.input_snapshot["inputs"]["user_configuration"]["daily_available_minutes"] = 0
        for day in self.output["days"]:
            day["capacity_minutes"] = 0
            day["remaining_minutes"] = 0
        self.assertEqual(validate_planner_output(self.output, self.input_snapshot, ROOT)["days"][0]["capacity_minutes"], 0)

    def test_today_is_a_single_days_zero_alias_not_a_second_payload(self) -> None:
        candidate = copy.deepcopy(self.output)
        candidate["today"] = copy.deepcopy(candidate["days"][0])
        self.assert_output_category("invalid_planner_output", candidate)

    def test_day_dates_and_study_days_are_local_calendar_projections(self) -> None:
        snapshot = build_minimal_snapshot(ROOT)
        snapshot["as_of"] = "2026-03-08T07:30:00Z"
        snapshot["timezone"] = "America/New_York"
        config = snapshot["inputs"]["user_configuration"]
        config["timezone"] = "America/New_York"
        review = snapshot["inputs"]["mastery_review_state"]
        review["as_of"] = snapshot["as_of"]
        review["timezone"] = "America/New_York"
        review["schedule_timezone"] = "America/New_York"
        _, output = build_minimal_output(ROOT, snapshot)
        local = datetime.fromisoformat(snapshot["as_of"].replace("Z", "+00:00")).astimezone(resolve_timezone("America/New_York"))
        self.assertEqual(output["generated_for_local_date"], local.date().isoformat())
        self.assertEqual([day["local_date"] for day in output["days"]], [
            "2026-03-08", "2026-03-09", "2026-03-10", "2026-03-11", "2026-03-12", "2026-03-13", "2026-03-14",
        ])
        self.assertEqual(validate_planner_output(output, snapshot, ROOT)["horizon"]["day_count"], 7)

    def test_supported_review_task_requires_matching_structured_explain(self) -> None:
        candidate = copy.deepcopy(self.output)
        add_task(candidate)
        self.assertEqual(validate_planner_output(candidate, self.input_snapshot, ROOT)["days"][0]["planned_minutes"], 10)
        candidate["explain_traces"][0]["reason_code"] = "Because it is due"
        self.assert_output_category("invalid_explain_trace", candidate)

    def test_capacity_and_task_minutes_are_exact_and_zero_capacity_has_no_tasks(self) -> None:
        candidate = copy.deepcopy(self.output)
        add_task(candidate)
        candidate["days"][0]["remaining_minutes"] -= 1
        self.assert_output_category("capacity_invariant", candidate)

        zero_input = copy.deepcopy(self.input_snapshot)
        zero_input["inputs"]["user_configuration"]["daily_available_minutes"] = 0
        zero_output = copy.deepcopy(self.output)
        for day in zero_output["days"]:
            day["capacity_minutes"] = 0
            day["remaining_minutes"] = 0
        add_task(zero_output, planned_minutes=0)
        zero_output["days"][0]["remaining_minutes"] = 0
        self.assert_output_category("capacity_invariant", zero_output, zero_input)

    def test_unmet_demand_is_separate_from_tasks_and_references_a_valid_trace(self) -> None:
        candidate = copy.deepcopy(self.output)
        candidate["days"][0]["unmet_demand"] = [{
            "demand_id": "demand-fixture-review-topic-day0",
            "demand_type": "review",
            "target_kind": "review_item",
            "target_ref": TOPIC_REF,
            "requested_minutes": 15,
            "explain_trace_id": "trace-fixture-demand",
        }]
        candidate["explain_traces"] = [{
            "trace_id": "trace-fixture-demand",
            "subject_kind": "unmet_demand",
            "subject_id": "demand-fixture-review-topic-day0",
            "decision_category": "demand_unmet",
            "reason_code": "contract_fixture",
            "planner_policy": copy.deepcopy(POLICY),
            "input_references": ["/inputs/mastery_review_state/items/review~1topic~1DATA.DATABASE.RELATIONAL/review_status"],
            "target_kind": "review_item",
            "target_ref": TOPIC_REF,
            "structured_inputs": {"fixture_kind": "shape_only"},
        }]
        self.assertEqual(validate_planner_output(candidate, self.input_snapshot, ROOT)["days"][0]["unmet_demand"][0]["requested_minutes"], 15)

    def test_unfrozen_fields_and_execution_facts_are_rejected(self) -> None:
        candidate = copy.deepcopy(self.output)
        candidate["days"][0]["priority"] = 1
        self.assert_output_category("invalid_plan_day", candidate)

        candidate = copy.deepcopy(self.output)
        add_task(candidate)
        candidate["days"][0]["tasks"][0]["completed"] = False
        self.assert_output_category("invalid_plan_task", candidate)

    def test_task_type_target_and_input_trace_references_fail_closed(self) -> None:
        candidate = copy.deepcopy(self.output)
        add_task(candidate)
        candidate["days"][0]["tasks"][0]["task_type"] = "new_learning"
        self.assert_output_category("unsupported_task_type", candidate)

        candidate = copy.deepcopy(self.output)
        add_task(candidate)
        candidate["explain_traces"][0]["input_references"] = ["/inputs/no_such_signal"]
        self.assert_output_category("invalid_explain_trace", candidate)

    def test_snapshot_metadata_must_match_output(self) -> None:
        candidate = copy.deepcopy(self.output)
        candidate["timezone"] = "UTC"
        self.assert_output_category("inconsistent_input", candidate)

        candidate = copy.deepcopy(self.output)
        candidate["input_snapshot_schema_version"] = "planner-input/v9.9"
        self.assert_output_category("inconsistent_input", candidate)


if __name__ == "__main__":
    unittest.main()
