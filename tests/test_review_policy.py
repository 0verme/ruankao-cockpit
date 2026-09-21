from __future__ import annotations

import copy
import json
import random
import unittest
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from engine.rules import (
    FAILURE_INTERVAL_DAYS,
    INTERVAL_LADDER_DAYS,
    MASTERED_MAINTENANCE_INTERVAL_DAYS,
    MASTERY_MIN_DISTINCT_SUCCESS_DAYS,
    MASTERY_POLICY_ID,
    MASTERY_POLICY_VERSION,
    REVIEW_POLICY_ID,
    REVIEW_POLICY_VERSION,
    MASTERY_REASONS,
    MASTERY_STATES,
    REVIEW_STATUS_REASONS,
    SCHEDULING_REASONS,
    PolicyEvidence,
    ReviewPolicyError,
    derive_item_state,
    derive_projection,
    local_date_of,
    policy_parameters,
    start_of_local_day,
    tzdata_version,
)
from engine.rules import review_policy_v01 as policy_module


ROOT = Path(__file__).resolve().parents[1]
REVIEW_DOC_ROOT = ROOT / "docs" / "review"

#: Policy symbols owned by P4.3 / P4.4 in the parallel test-design registry.
P4_3_P4_4_POLICY_SYMBOLS = (
    "MASTERY_STATE_ENUM",
    "MASTERY_INITIAL_STATE",
    "MASTERY_SUCCESS_STREAK_TO_MASTERED",
    "MASTERY_FAILURE_TRANSITION",
    "MASTERY_MASTERED_PERSISTENCE",
    "MASTERY_MASTERED_FAILURE_TRANSITION",
    "MASTERY_INSUFFICIENT_EVIDENCE_STATE",
    "MASTERY_ILLEGAL_TRANSITION_POLICY",
    "STATE_FIELD_NAMES",
    "SCHED_INTERVAL_LADDER",
    "SCHED_FIRST_DUE_RULE",
    "SCHED_SUCCESS_ADVANCE_RULE",
    "SCHED_FAILURE_RESET_RULE",
    "SCHED_MASTERED_MAINTENANCE_RULE",
    "SCHED_OVERDUE_RULE",
    "SCHED_SAME_DAY_REPEAT_RULE",
    "SCHED_DUE_COUNT_DEFINITION",
    "SCHED_DUE_GRANULARITY",
    "SCHED_DATE_BOUNDARY_TIMEZONE",
    "STATE_DUE_PROJECTION_NAMES",
)


SHANGHAI = "Asia/Shanghai"
UTC = timezone.utc


def at(text: str) -> datetime:
    normalized = text[:-1] + "+00:00" if text.endswith("Z") else text
    return datetime.fromisoformat(normalized)


def success(evidence_id: str, when: str) -> PolicyEvidence:
    return PolicyEvidence(evidence_id, at(when), "success")


def failure(evidence_id: str, when: str) -> PolicyEvidence:
    return PolicyEvidence(evidence_id, at(when), "failure")


def insufficient(evidence_id: str, when: str) -> PolicyEvidence:
    return PolicyEvidence(evidence_id, at(when), "insufficient")


def state_of(evidence, as_of: str, item_id: str = "ITEM.A", tz: str = SHANGHAI) -> dict:
    return derive_item_state(item_id, evidence, as_of=at(as_of), schedule_timezone=tz)


class MasteryTransitionTests(unittest.TestCase):
    def test_no_evidence_is_new_and_not_scheduled(self) -> None:
        state = state_of([], "2026-03-01T10:00+08:00")
        self.assertEqual(state["mastery_state"], "new")
        self.assertEqual(state["mastery_reason"], "no_evaluated_evidence")
        self.assertEqual(state["review_status"], "not_scheduled")
        self.assertIsNone(state["next_due_at"])
        self.assertIsNone(state["review_interval_days"])
        self.assertEqual(state["evaluated_evidence_count"], 0)

    def test_first_success_enters_learning_and_schedules_one_day(self) -> None:
        state = state_of([success("e1", "2026-03-01T10:00+08:00")], "2026-03-01T10:00+08:00")
        self.assertEqual(state["mastery_state"], "learning")
        self.assertEqual(state["mastery_reason"], "success_enters_learning")
        self.assertEqual(state["review_interval_days"], INTERVAL_LADDER_DAYS[0])
        self.assertEqual(state["next_due_at"], "2026-03-01T16:00:00+00:00")
        self.assertEqual(state["next_due_local_date"], "2026-03-02")
        self.assertEqual(state["review_status"], "scheduled")
        self.assertEqual(state["scheduling_reason"], "success_schedules_ladder_interval")
        self.assertEqual(state["last_review_at"], "2026-03-01T02:00:00+00:00")

    def test_first_failure_enters_learning_and_schedules_one_day(self) -> None:
        state = state_of([failure("e1", "2026-03-01T23:50+08:00")], "2026-03-02T08:00+08:00")
        self.assertEqual(state["mastery_state"], "learning")
        self.assertEqual(state["mastery_reason"], "failure_enters_learning")
        self.assertEqual(state["review_interval_days"], FAILURE_INTERVAL_DAYS)
        self.assertEqual(state["next_due_local_date"], "2026-03-02")
        self.assertEqual(state["review_status"], "due")

    def test_spaced_successes_climb_the_ladder_and_reach_mastery(self) -> None:
        evidence = [
            success("e1", "2026-03-01T10:00+08:00"),
            success("e2", "2026-03-02T10:00+08:00"),
            success("e3", "2026-03-05T10:00+08:00"),
        ]
        first = state_of(evidence[:1], "2026-03-01T10:00+08:00")
        second = state_of(evidence[:2], "2026-03-02T10:00+08:00")
        third = state_of(evidence, "2026-03-05T10:00+08:00")

        self.assertEqual(first["review_interval_days"], 1)
        self.assertEqual(first["consecutive_success_day_count"], 1)
        self.assertEqual(second["review_interval_days"], 3)
        self.assertEqual(second["mastery_state"], "learning")
        self.assertEqual(second["mastery_reason"], "learning_success_below_mastery")
        self.assertEqual(second["next_due_local_date"], "2026-03-05")

        self.assertEqual(third["review_interval_days"], 7)
        self.assertEqual(third["mastery_state"], "mastered")
        self.assertEqual(third["mastery_reason"], "learning_success_reaches_mastery")
        self.assertEqual(third["consecutive_success_count"], 3)
        self.assertEqual(third["consecutive_success_day_count"], 3)
        self.assertEqual(third["next_due_local_date"], "2026-03-12")

    def test_fourth_spaced_success_uses_maintenance_interval(self) -> None:
        evidence = [
            success("e1", "2026-03-01T10:00+08:00"),
            success("e2", "2026-03-02T10:00+08:00"),
            success("e3", "2026-03-05T10:00+08:00"),
            success("e4", "2026-03-12T09:00+08:00"),
        ]
        state = state_of(evidence, "2026-03-12T09:00+08:00")
        self.assertEqual(state["mastery_state"], "mastered")
        self.assertEqual(state["mastery_reason"], "mastered_success_maintenance")
        self.assertEqual(state["review_interval_days"], MASTERED_MAINTENANCE_INTERVAL_DAYS)
        self.assertEqual(state["review_interval_days"], INTERVAL_LADDER_DAYS[-1])
        self.assertEqual(state["consecutive_success_day_count"], 4)

    def test_failure_while_learning_resets_the_run(self) -> None:
        evidence = [
            success("e1", "2026-03-01T10:00+08:00"),
            success("e2", "2026-03-02T10:00+08:00"),
            failure("e3", "2026-03-05T10:00+08:00"),
        ]
        state = state_of(evidence, "2026-03-05T10:00+08:00")
        self.assertEqual(state["mastery_state"], "learning")
        self.assertEqual(state["mastery_reason"], "learning_failure_keeps_learning")
        self.assertEqual(state["failure_count"], 1)
        self.assertEqual(state["successful_review_count"], 2)
        self.assertEqual(state["consecutive_success_count"], 0)
        self.assertEqual(state["consecutive_success_day_count"], 0)
        self.assertEqual(state["review_interval_days"], 1)
        self.assertEqual(state["next_due_local_date"], "2026-03-06")

    def test_failure_after_mastery_demotes_to_learning(self) -> None:
        evidence = [
            success("e1", "2026-03-01T10:00+08:00"),
            success("e2", "2026-03-02T10:00+08:00"),
            success("e3", "2026-03-05T10:00+08:00"),
            failure("e4", "2026-03-12T10:00+08:00"),
        ]
        mastered = state_of(evidence[:3], "2026-03-12T10:00+08:00")
        demoted = state_of(evidence, "2026-03-12T10:00+08:00")
        self.assertEqual(mastered["mastery_state"], "mastered")
        self.assertEqual(demoted["mastery_state"], "learning")
        self.assertEqual(demoted["mastery_reason"], "mastered_failure_demotes_learning")
        self.assertEqual(demoted["review_interval_days"], 1)
        self.assertEqual(demoted["consecutive_success_day_count"], 0)

        remastered = state_of(
            evidence + [success("e5", "2026-03-13T10:00+08:00")],
            "2026-03-13T10:00+08:00",
        )
        self.assertEqual(remastered["mastery_state"], "learning")
        self.assertEqual(remastered["mastery_reason"], "learning_success_below_mastery")

    def test_same_local_day_repeat_success_is_a_scheduling_noop(self) -> None:
        morning = success("e1", "2026-03-01T09:00+08:00")
        evening = success("e2", "2026-03-01T21:00+08:00")
        single = state_of([morning], "2026-03-01T21:00+08:00")
        repeated = state_of([morning, evening], "2026-03-01T21:00+08:00")

        self.assertEqual(repeated["next_due_local_date"], single["next_due_local_date"])
        self.assertEqual(repeated["review_interval_days"], single["review_interval_days"])
        self.assertEqual(repeated["mastery_state"], single["mastery_state"])
        self.assertEqual(repeated["scheduling_reason"], "same_day_success_keeps_schedule")
        self.assertEqual(repeated["consecutive_success_count"], 2)
        self.assertEqual(repeated["consecutive_success_day_count"], 1)

    def test_same_day_failure_is_not_undone_by_a_later_success(self) -> None:
        evidence = [
            success("e1", "2026-03-01T09:00+08:00"),
            failure("e2", "2026-03-20T09:00+08:00"),
            success("e3", "2026-03-20T21:00+08:00"),
        ]
        state = state_of(evidence, "2026-03-20T21:00+08:00")
        self.assertEqual(state["failure_count"], 1)
        self.assertEqual(state["mastery_state"], "learning")
        self.assertEqual(state["review_interval_days"], 1)
        self.assertEqual(state["next_due_local_date"], "2026-03-21")

    def test_same_day_success_failure_success_does_not_skip_the_ladder(self) -> None:
        evidence = [
            success("e1", "2026-03-20T09:00+08:00"),
            failure("e2", "2026-03-20T10:00+08:00"),
            success("e3", "2026-03-20T11:00+08:00"),
        ]
        state = state_of(evidence, "2026-03-20T11:00+08:00")
        self.assertEqual(state["review_interval_days"], 1)
        self.assertEqual(state["consecutive_success_day_count"], 1)
        self.assertEqual(state["next_due_local_date"], "2026-03-21")

    def test_mastery_does_not_depend_on_cumulative_counts(self) -> None:
        evidence = [
            success("e1", "2026-03-01T10:00+08:00"),
            success("e2", "2026-03-02T10:00+08:00"),
            failure("e3", "2026-03-03T10:00+08:00"),
            success("e4", "2026-03-04T10:00+08:00"),
            success("e5", "2026-03-05T10:00+08:00"),
            success("e6", "2026-03-06T10:00+08:00"),
        ]
        state = state_of(evidence, "2026-03-06T10:00+08:00")
        self.assertEqual(state["successful_review_count"], 5)
        self.assertEqual(state["mastery_state"], "mastered")
        self.assertEqual(state["consecutive_success_day_count"], MASTERY_MIN_DISTINCT_SUCCESS_DAYS)
        self.assertEqual(state["next_due_local_date"], "2026-03-13")

    def test_insufficient_evidence_is_not_a_failure(self) -> None:
        state = state_of([insufficient("e1", "2026-03-01T10:00+08:00")], "2026-03-01T10:00+08:00")
        self.assertEqual(state["mastery_state"], "new")
        self.assertEqual(state["review_status"], "not_scheduled")
        self.assertEqual(state["insufficient_evidence_count"], 1)
        self.assertEqual(state["evaluated_evidence_count"], 0)
        self.assertEqual(state["failure_count"], 0)
        self.assertIsNone(state["next_due_at"])
        self.assertIsNone(state["last_review_at"])

    def test_insufficient_evidence_does_not_change_existing_state(self) -> None:
        evidence = [
            success("e1", "2026-03-01T10:00+08:00"),
            insufficient("e2", "2026-03-02T10:00+08:00"),
        ]
        baseline = state_of(evidence[:1], "2026-03-02T10:00+08:00")
        with_insufficient = state_of(evidence, "2026-03-02T10:00+08:00")
        for key in (
            "mastery_state",
            "mastery_reason",
            "review_interval_days",
            "next_due_at",
            "next_due_local_date",
            "consecutive_success_count",
            "consecutive_success_day_count",
        ):
            self.assertEqual(with_insufficient[key], baseline[key], key)
        self.assertEqual(with_insufficient["insufficient_evidence_count"], 1)

    def test_input_order_and_repeatability(self) -> None:
        evidence = [
            success("e1", "2026-03-01T10:00+08:00"),
            failure("e2", "2026-03-04T10:00+08:00"),
            success("e3", "2026-03-05T10:00+08:00"),
            insufficient("e4", "2026-03-05T11:00+08:00"),
        ]
        baseline = state_of(evidence, "2026-03-06T10:00+08:00")
        self.assertEqual(baseline, state_of(evidence, "2026-03-06T10:00+08:00"))
        shuffled = copy.deepcopy(evidence)
        random.Random(11).shuffle(shuffled)
        self.assertEqual(baseline, state_of(shuffled, "2026-03-06T10:00+08:00"))

    def test_same_instant_evidence_is_ordered_by_evidence_id(self) -> None:
        first = state_of(
            [success("e-a", "2026-03-01T10:00+08:00"), failure("e-b", "2026-03-01T10:00+08:00")],
            "2026-03-01T10:00+08:00",
        )
        second = state_of(
            [failure("e-a", "2026-03-01T10:00+08:00"), success("e-b", "2026-03-01T10:00+08:00")],
            "2026-03-01T10:00+08:00",
        )
        self.assertEqual(first["mastery_reason"], "learning_failure_keeps_learning")
        self.assertEqual(first["successful_review_count"], 1)
        self.assertEqual(first["failure_count"], 1)
        self.assertEqual(second["mastery_reason"], "learning_success_below_mastery")
        self.assertEqual(second["successful_review_count"], 1)
        self.assertEqual(second["failure_count"], 1)


class SchedulingProjectionTests(unittest.TestCase):
    def test_exact_due_instant_is_due(self) -> None:
        state = state_of([success("e1", "2026-03-01T10:00+08:00")], "2026-03-02T00:00+08:00")
        self.assertEqual(state["next_due_at"], "2026-03-01T16:00:00+00:00")
        self.assertEqual(state["review_status"], "due")
        self.assertEqual(state["review_status_reason"], "due_on_due_local_date")

    def test_one_microsecond_before_due_is_scheduled(self) -> None:
        just_before = at("2026-03-02T00:00+08:00") - timedelta(microseconds=1)
        state = derive_item_state(
            "ITEM.A",
            [success("e1", "2026-03-01T10:00+08:00")],
            as_of=just_before,
            schedule_timezone=SHANGHAI,
        )
        self.assertEqual(state["review_status"], "scheduled")
        self.assertEqual(state["review_status_reason"], "scheduled_due_in_future")

    def test_one_microsecond_after_due_is_still_due(self) -> None:
        just_after = at("2026-03-02T00:00+08:00") + timedelta(microseconds=1)
        state = derive_item_state(
            "ITEM.A",
            [success("e1", "2026-03-01T10:00+08:00")],
            as_of=just_after,
            schedule_timezone=SHANGHAI,
        )
        self.assertEqual(state["review_status"], "due")

    def test_overdue_starts_at_the_next_local_midnight(self) -> None:
        last_moment = at("2026-03-02T23:59:59.999999+08:00")
        next_day = at("2026-03-03T00:00+08:00")
        evidence = [success("e1", "2026-03-01T10:00+08:00")]
        self.assertEqual(
            derive_item_state(
                "ITEM.A", evidence, as_of=last_moment, schedule_timezone=SHANGHAI
            )["review_status"],
            "due",
        )
        overdue = derive_item_state(
            "ITEM.A", evidence, as_of=next_day, schedule_timezone=SHANGHAI
        )
        self.assertEqual(overdue["review_status"], "overdue")
        self.assertEqual(overdue["review_status_reason"], "overdue_since_next_local_date")
        self.assertEqual(overdue["next_due_local_date"], "2026-03-02")
        self.assertEqual(overdue["review_interval_days"], 1)

    def test_review_today_removes_the_item_from_todays_due_set(self) -> None:
        evidence = [success("e1", "2026-03-01T10:00+08:00")]
        before = derive_item_state("ITEM.A", evidence, as_of=at("2026-03-02T08:00+08:00"), schedule_timezone=SHANGHAI)
        after = derive_item_state(
            "ITEM.A",
            evidence + [success("e2", "2026-03-02T09:00+08:00")],
            as_of=at("2026-03-02T09:01+08:00"),
            schedule_timezone=SHANGHAI,
        )
        self.assertEqual(before["review_status"], "due")
        self.assertEqual(after["review_status"], "scheduled")
        self.assertEqual(after["next_due_local_date"], "2026-03-05")

    def test_same_instant_different_offsets_and_utc_equivalence(self) -> None:
        variants = [
            "2026-03-01T10:00+08:00",
            "2026-03-01T02:00:00Z",
            "2026-03-01T03:00+01:00",
        ]
        states = [
            state_of([success("e1", value)], "2026-03-02T08:00+08:00") for value in variants
        ]
        self.assertEqual(states[0], states[1])
        self.assertEqual(states[1], states[2])

    def test_same_evidence_different_as_of_representations(self) -> None:
        evidence = [success("e1", "2026-03-01T10:00+08:00")]
        shanghai_as_of = derive_item_state(
            "ITEM.A", evidence, as_of="2026-03-02T00:30+08:00", schedule_timezone=SHANGHAI
        )
        utc_as_of = derive_item_state(
            "ITEM.A", evidence, as_of="2026-03-01T16:30Z", schedule_timezone=SHANGHAI
        )
        self.assertEqual(shanghai_as_of["review_status"], "due")
        self.assertEqual(shanghai_as_of, utc_as_of)

    def test_timezone_is_explicit_and_changes_the_result(self) -> None:
        # 2026-03-01T16:30Z is 2026-03-02 00:30 in Shanghai but still 2026-03-01 17:30 in Berlin.
        evidence = [success("e1", "2026-03-01T16:30Z")]
        as_of = "2026-03-02T00:00Z"
        shanghai = derive_item_state("ITEM.A", evidence, as_of=as_of, schedule_timezone=SHANGHAI)
        berlin = derive_item_state("ITEM.A", evidence, as_of=as_of, schedule_timezone="Europe/Berlin")

        self.assertEqual(shanghai["next_due_local_date"], "2026-03-03")
        self.assertEqual(shanghai["next_due_at"], "2026-03-02T16:00:00+00:00")
        self.assertEqual(berlin["next_due_local_date"], "2026-03-02")
        self.assertEqual(berlin["next_due_at"], "2026-03-01T23:00:00+00:00")
        self.assertEqual(shanghai["review_status"], "scheduled")
        self.assertEqual(berlin["review_status"], "due")

    def test_due_count_equals_item_level_projection(self) -> None:
        projection = derive_projection(
            {
                "ITEM.DUE": [success("a1", "2026-03-01T10:00+08:00")],
                "ITEM.SCHEDULED": [success("b1", "2026-03-02T07:00+08:00")],
                "ITEM.OVERDUE": [success("c1", "2026-02-20T10:00+08:00")],
                "ITEM.NEW": [],
            },
            as_of=at("2026-03-02T08:00+08:00"),
            schedule_timezone=SHANGHAI,
        )
        items = projection["items"]
        item_level = [
            item_id
            for item_id, item in items.items()
            if item["review_status"] in {"due", "overdue"}
        ]
        self.assertEqual(len(item_level), 2)
        self.assertEqual(projection["review"]["due_count"], len(item_level))
        self.assertEqual(projection["review"]["due_today_count"], 1)
        self.assertEqual(projection["review"]["overdue_count"], 1)
        self.assertEqual(
            projection["review"]["due_count"],
            projection["review"]["due_today_count"] + projection["review"]["overdue_count"],
        )
        self.assertEqual(projection["review"]["total_items"], 4)
        self.assertEqual(projection["review"]["not_scheduled_count"], 1)
        self.assertEqual(projection["review"]["scheduled_count"], 1)
        self.assertEqual(items["ITEM.DUE"]["review_status"], "due")
        self.assertEqual(items["ITEM.SCHEDULED"]["next_due_local_date"], "2026-03-03")
        self.assertEqual(items["ITEM.OVERDUE"]["review_status"], "overdue")

    def test_projection_metadata_reports_policy_timezone_and_tzdata(self) -> None:
        projection = derive_projection(
            {}, as_of="2026-03-03T08:00+08:00", schedule_timezone=SHANGHAI, item_ids=["ITEM.A"]
        )
        self.assertEqual(projection["policy"]["mastery_policy_id"], MASTERY_POLICY_ID)
        self.assertEqual(projection["policy"]["mastery_policy_version"], MASTERY_POLICY_VERSION)
        self.assertEqual(projection["policy"]["review_policy_id"], REVIEW_POLICY_ID)
        self.assertEqual(projection["policy"]["review_policy_version"], REVIEW_POLICY_VERSION)
        self.assertEqual(projection["policy"]["parameters"], policy_parameters())
        self.assertEqual(projection["schedule_timezone"], SHANGHAI)
        self.assertEqual(projection["as_of"], "2026-03-03T00:00:00+00:00")
        self.assertIsInstance(projection["tzdata_version"], str)
        self.assertTrue(projection["tzdata_version"])
        self.assertEqual(projection["items"]["ITEM.A"]["review_status"], "not_scheduled")


class TimeSemanticsTests(unittest.TestCase):
    def test_start_of_local_day_fixed_cases(self) -> None:
        self.assertEqual(
            start_of_local_day(date(2026, 3, 2), ZoneInfo(SHANGHAI)),
            at("2026-03-01T16:00:00Z"),
        )
        # historical, tzdata-frozen cases
        self.assertEqual(
            start_of_local_day(date(2020, 3, 8), ZoneInfo("America/New_York")),
            at("2020-03-08T05:00:00Z"),
        )
        # local midnight does not exist: the day starts at 01:00 local
        santiago = start_of_local_day(date(2019, 9, 8), ZoneInfo("America/Santiago"))
        self.assertEqual(santiago, at("2019-09-08T04:00:00Z"))
        self.assertEqual(local_date_of(santiago, ZoneInfo("America/Santiago")), date(2019, 9, 8))

    def test_start_of_local_day_is_the_first_instant_of_that_local_date(self) -> None:
        apia = ZoneInfo("Pacific/Apia")
        skipped = start_of_local_day(date(2011, 12, 30), apia)
        next_day = start_of_local_day(date(2011, 12, 31), apia)
        self.assertEqual(skipped, next_day)
        self.assertEqual(local_date_of(skipped, apia), date(2011, 12, 31))
        for tz_name in (SHANGHAI, "America/New_York", "Europe/Berlin", "Asia/Kathmandu"):
            tz = ZoneInfo(tz_name)
            for day in (date(2026, 3, 2), date(2026, 11, 3)):
                boundary = start_of_local_day(day, tz)
                self.assertGreaterEqual(local_date_of(boundary, tz), day)
                self.assertLess(local_date_of(boundary - timedelta(microseconds=1), tz), day)

    def test_local_date_of_uses_the_explicit_timezone(self) -> None:
        instant = at("2026-03-01T23:30+08:00")
        self.assertEqual(local_date_of(instant, ZoneInfo(SHANGHAI)), date(2026, 3, 1))
        self.assertEqual(local_date_of(instant, ZoneInfo("Europe/Berlin")), date(2026, 3, 1))
        late = at("2026-03-01T17:30Z")
        self.assertEqual(local_date_of(late, ZoneInfo(SHANGHAI)), date(2026, 3, 2))
        self.assertEqual(local_date_of(late, ZoneInfo("America/New_York")), date(2026, 3, 1))


class RejectionTests(unittest.TestCase):
    def assert_category(self, category: str, func, *args, **kwargs) -> None:
        with self.assertRaises(ReviewPolicyError) as context:
            func(*args, **kwargs)
        self.assertEqual(context.exception.category, category)

    def test_naive_timestamps_are_rejected(self) -> None:
        self.assert_category(
            "invalid_timestamp",
            derive_item_state,
            "ITEM.A",
            [PolicyEvidence("e1", datetime(2026, 3, 1, 10, 0), "success")],
            as_of=at("2026-03-02T10:00+08:00"),
            schedule_timezone=SHANGHAI,
        )
        self.assert_category(
            "invalid_timestamp",
            derive_item_state,
            "ITEM.A",
            [],
            as_of=datetime(2026, 3, 2, 10, 0),
            schedule_timezone=SHANGHAI,
        )
        self.assert_category(
            "invalid_timestamp",
            derive_item_state,
            "ITEM.A",
            [{"evidence_id": "e1", "occurred_at": "2026-03-01T10:00:00", "outcome": "success"}],
            as_of=at("2026-03-02T10:00+08:00"),
            schedule_timezone=SHANGHAI,
        )

    def test_future_evidence_is_rejected(self) -> None:
        self.assert_category(
            "future_evidence",
            derive_item_state,
            "ITEM.A",
            [success("e1", "2026-03-05T10:00+08:00")],
            as_of=at("2026-03-04T10:00+08:00"),
            schedule_timezone=SHANGHAI,
        )

    def test_evidence_at_as_of_is_accepted(self) -> None:
        state = state_of([success("e1", "2026-03-04T10:00+08:00")], "2026-03-04T10:00+08:00")
        self.assertEqual(state["mastery_state"], "learning")

    def test_duplicate_evidence_ids_are_rejected(self) -> None:
        self.assert_category(
            "duplicate_evidence_id",
            derive_item_state,
            "ITEM.A",
            [success("e1", "2026-03-01T10:00+08:00"), failure("e1", "2026-03-02T10:00+08:00")],
            as_of=at("2026-03-03T10:00+08:00"),
            schedule_timezone=SHANGHAI,
        )

    def test_invalid_outcomes_and_shapes_are_rejected(self) -> None:
        self.assert_category(
            "invalid_evidence_outcome",
            derive_item_state,
            "ITEM.A",
            [{"evidence_id": "e1", "occurred_at": "2026-03-01T10:00+08:00", "outcome": "zero"}],
            as_of=at("2026-03-02T10:00+08:00"),
            schedule_timezone=SHANGHAI,
        )
        self.assert_category(
            "invalid_policy_input",
            derive_item_state,
            "ITEM.A",
            [{"evidence_id": "e1", "occurred_at": "2026-03-01T10:00+08:00", "outcome": "success", "score": 0}],
            as_of=at("2026-03-02T10:00+08:00"),
            schedule_timezone=SHANGHAI,
        )

    def test_timezone_must_be_explicit(self) -> None:
        for value in (None, "", "local", "system", "Mars/Olympus"):
            self.assert_category(
                "invalid_timezone",
                derive_item_state,
                "ITEM.A",
                [],
                as_of=at("2026-03-02T10:00+08:00"),
                schedule_timezone=value,
            )

    def test_unknown_evidence_keys_are_rejected(self) -> None:
        self.assert_category(
            "invalid_policy_input",
            derive_projection,
            {"ITEM.A": [{"evidence_id": "e1", "occurred_at": "2026-03-01T10:00+08:00", "outcome": "success", "kind": "topic"}]},
            as_of=at("2026-03-02T10:00+08:00"),
            schedule_timezone=SHANGHAI,
        )


class FrozenContractTests(unittest.TestCase):
    def test_policy_constants_are_frozen(self) -> None:
        self.assertEqual(MASTERY_POLICY_ID, "mastery-policy/spaced-consecutive")
        self.assertEqual(MASTERY_POLICY_VERSION, "v0.1")
        self.assertEqual(REVIEW_POLICY_ID, "review-policy/simple-ladder")
        self.assertEqual(REVIEW_POLICY_VERSION, "v0.1")
        self.assertEqual(INTERVAL_LADDER_DAYS, (1, 3, 7, 15))
        self.assertEqual(FAILURE_INTERVAL_DAYS, 1)
        self.assertEqual(MASTERY_MIN_DISTINCT_SUCCESS_DAYS, 3)
        self.assertEqual(MASTERED_MAINTENANCE_INTERVAL_DAYS, 15)

    def test_policy_module_has_no_implicit_time_source(self) -> None:
        source = Path(policy_module.__file__).read_text(encoding="utf-8")
        for forbidden in ("datetime.now", "utcnow", "date.today", "time.time(", "astimezone()"):
            self.assertNotIn(forbidden, source)

    def test_tzdata_version_is_reported(self) -> None:
        self.assertIsInstance(tzdata_version(), str)


class DocumentationSyncTests(unittest.TestCase):
    """The policy documents are part of the frozen contract."""

    def read(self, name: str) -> str:
        return (REVIEW_DOC_ROOT / name).read_text(encoding="utf-8")

    def test_policy_identifiers_and_parameters_are_documented(self) -> None:
        mastery = self.read("MASTERY_POLICY_V01.md")
        scheduling = self.read("REVIEW_SCHEDULING_POLICY_V01.md")
        self.assertIn(MASTERY_POLICY_ID, mastery)
        self.assertIn(MASTERY_POLICY_VERSION, mastery)
        self.assertIn(REVIEW_POLICY_ID, scheduling)
        self.assertIn(REVIEW_POLICY_VERSION, scheduling)
        self.assertIn("[1, 3, 7, 15]", scheduling)
        self.assertIn(f">= {MASTERY_MIN_DISTINCT_SUCCESS_DAYS} 个不同本地日期", mastery)

    def test_every_reason_code_is_documented(self) -> None:
        corpus = "\n".join(
            self.read(name)
            for name in (
                "MASTERY_POLICY_V01.md",
                "REVIEW_SCHEDULING_POLICY_V01.md",
                "POLICY_TEST_MATRIX_V01.md",
            )
        )
        for code in MASTERY_REASONS + SCHEDULING_REASONS + REVIEW_STATUS_REASONS:
            self.assertIn(code, corpus, code)

    def test_assumptions_register_exists(self) -> None:
        assumptions = self.read("ASSUMPTIONS_PENDING_P4_1_P4_2.md")
        self.assertIn("UNRESOLVED", assumptions)
        for dependency in ("P4.1", "P4.2"):
            self.assertIn(dependency, assumptions)

    def test_policy_symbol_freeze_record_covers_owned_symbols(self) -> None:
        freeze = self.read("POLICY_SYMBOL_FREEZE_V01.md")
        for symbol in P4_3_P4_4_POLICY_SYMBOLS:
            self.assertIn(symbol, freeze, symbol)
        for gap in ("GAP-07", "GAP-08", "GAP-09", "GAP-10", "GAP-11", "GAP-12", "GAP-13"):
            self.assertIn(gap, freeze, gap)

    def test_frozen_symbol_values_are_valid_json(self) -> None:
        freeze = self.read("POLICY_SYMBOL_FREEZE_V01.md")
        validated: set[str] = set()
        for line in freeze.splitlines():
            if not line.startswith("| `"):
                continue
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            if len(cells) != 2:
                continue
            symbol_cell, value_cell = cells
            if not symbol_cell.startswith("`") or not value_cell.startswith("`"):
                continue
            symbol = symbol_cell.strip("`")
            if symbol not in P4_3_P4_4_POLICY_SYMBOLS:
                continue
            payload = value_cell.strip("`")
            try:
                json.loads(payload)
            except json.JSONDecodeError:
                # STATE_FIELD_NAMES points at the JSON block in section 3.
                continue
            validated.add(symbol)
        self.assertEqual(validated, set(P4_3_P4_4_POLICY_SYMBOLS) - {"STATE_FIELD_NAMES"})

    def test_frozen_state_field_names_match_the_kernel(self) -> None:
        freeze = self.read("POLICY_SYMBOL_FREEZE_V01.md")
        section = freeze.split("## 3.", 1)[1].split("## 4.", 1)[0]
        block = section.split("```json", 1)[1].split("```", 1)[0]
        declared = set(json.loads(block)["item_fields"])
        produced = set(state_of([], "2026-03-01T10:00+08:00"))
        self.assertEqual(declared, produced)
        self.assertNotIn("last_success_local_date", declared)


if __name__ == "__main__":
    unittest.main()
