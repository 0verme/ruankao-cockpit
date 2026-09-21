"""Mastery / Review Scheduling policy kernel v0.1 (deterministic, versioned).

This module freezes the **policy semantics** of:

```text
mastery-policy/spaced-consecutive/v0.1
review-policy/simple-ladder/v0.1
```

It is a pure policy kernel. It is intentionally *not* a replay implementation.

Scope boundary
--------------

In scope (this module):

- the per-item mastery state machine (`new` / `learning` / `mastered`);
- the scheduling projection (`not_scheduled` / `scheduled` / `due` / `overdue`);
- the interval ladder transition (`1 / 3 / 7 / 15` days, failure -> 1 day);
- explicit time semantics (UTC instants + explicit IANA timezone + local-day
  anchoring), including `start_of_local_day`.

Out of scope (owned by other Phase 4 work items):

- `DEPENDS_ON_P4_1_P4_2`: what a `review_item` is, its identity, its kind, and
  how Progress Events project onto policy-eligible evidence records. This module
  consumes a *policy-eligible evidence stream* described by the frozen
  :class:`PolicyEvidence` adapter shape; it does not define the Review Evidence
  schema.
- P4.5: `MasteryReviewState v0.1` replay over Progress Events.
- P4.6 / P4.7: fixtures, validators and the frozen state schema.

The functions here never read the current system time and never read a machine
timezone. Every time-dependent result is a pure function of explicit inputs:
`evidence`, `as_of` and an explicit IANA `schedule_timezone`.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
import re
from typing import Any, Iterable, Mapping, Sequence
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

# ---------------------------------------------------------------------------
# Frozen policy identity
# ---------------------------------------------------------------------------

MASTERY_POLICY_ID = "mastery-policy/spaced-consecutive"
MASTERY_POLICY_VERSION = "v0.1"
REVIEW_POLICY_ID = "review-policy/simple-ladder"
REVIEW_POLICY_VERSION = "v0.1"
PROJECTION_SCHEMA_VERSION = "review-policy-projection/v0.1"

#: Applied review intervals in whole local calendar days.
#: The interval applied after a successful review is `INTERVAL_LADDER_DAYS[min(d - 1, 3)]`
#: where `d` is the number of distinct local dates in the current success run.
INTERVAL_LADDER_DAYS = (1, 3, 7, 15)
MAX_LADDER_INDEX = len(INTERVAL_LADDER_DAYS) - 1

#: A failure always schedules the next review one local day later.
FAILURE_INTERVAL_DAYS = INTERVAL_LADDER_DAYS[0]

#: Mastery is bound to a review item, a run of successes and distinct local
#: dates: at least this many *different local dates* must carry a successful
#: review inside the current (unbroken) success run.
MASTERY_MIN_DISTINCT_SUCCESS_DAYS = 3

#: `mastered` items keep a maintenance review at the longest interval.
MASTERED_MAINTENANCE_INTERVAL_DAYS = INTERVAL_LADDER_DAYS[MAX_LADDER_INDEX]

EVIDENCE_OUTCOMES = ("success", "failure", "insufficient")

MASTERY_STATES = ("new", "learning", "mastered")
REVIEW_STATUSES = ("not_scheduled", "scheduled", "due", "overdue")

MASTERY_REASONS = (
    "no_evaluated_evidence",
    "failure_enters_learning",
    "success_enters_learning",
    "learning_failure_keeps_learning",
    "learning_success_below_mastery",
    "learning_success_reaches_mastery",
    "mastered_success_maintenance",
    "mastered_failure_demotes_learning",
)

SCHEDULING_REASONS = (
    "no_evidence_not_scheduled",
    "success_schedules_ladder_interval",
    "same_day_success_keeps_schedule",
    "failure_schedules_retry_interval",
)

REVIEW_STATUS_REASONS = (
    "not_scheduled_no_evaluated_evidence",
    "scheduled_due_in_future",
    "due_on_due_local_date",
    "overdue_since_next_local_date",
)

RESERVED_TIMEZONE_NAMES = frozenset(
    {"", "local", "machine", "system", "default", "localtime", "tzlocal"}
)


class ReviewPolicyError(ValueError):
    """Raised when policy inputs cannot be evaluated deterministically."""

    def __init__(self, message: str, category: str = "invalid_policy_input") -> None:
        self.category = category
        super().__init__(message)


@dataclass(frozen=True)
class PolicyEvidence:
    """Adapter shape for one policy-eligible evidence record.

    `DEPENDS_ON_P4_1_P4_2`: the Review Model / Evidence contract decides what a
    review item is, which facts become policy-eligible evidence, and how an
    evidence record is identified. This dataclass is only the *policy input*
    abstraction: item identity is supplied by the caller (the mapping key of
    :func:`derive_projection`), and `evidence_id` is an opaque stable string.

    `outcome` is a policy outcome primitive:

    - ``success``: the item was demonstrably recalled correctly;
    - ``failure``: the item was demonstrably not recalled correctly;
    - ``insufficient``: a record exists but yields no policy outcome
      (for example a missing answer). It is *never* treated as a failure.

    How a concrete fact (boolean `correct`, a case `score_earned`, a skipped
    question) maps onto these primitives is a P4.2 decision, not a P4.3/P4.4
    decision.
    """

    evidence_id: str
    occurred_at: datetime
    outcome: str


# ---------------------------------------------------------------------------
# Frozen parameters (machine readable mirror of the policy documents)
# ---------------------------------------------------------------------------


def policy_parameters() -> dict[str, Any]:
    """Return the frozen v0.1 policy parameters as a JSON-compatible object."""
    return {
        "interval_ladder_days": list(INTERVAL_LADDER_DAYS),
        "failure_interval_days": FAILURE_INTERVAL_DAYS,
        "mastery_min_distinct_success_days": MASTERY_MIN_DISTINCT_SUCCESS_DAYS,
        "mastered_maintenance_interval_days": MASTERED_MAINTENANCE_INTERVAL_DAYS,
        "same_day_success_advances_interval": False,
        "overdue_changes_interval": False,
        "insufficient_evidence_changes_state": False,
        "due_boundary": "local_day_start_inclusive",
        "overdue_boundary": "first_local_midnight_after_due_local_date",
        "evidence_ordering": "utc_instant_then_evidence_id",
        "future_evidence": "reject",
    }


def policy_identity() -> dict[str, Any]:
    """Return the policy identity block recorded next to every projection."""
    return {
        "mastery_policy_id": MASTERY_POLICY_ID,
        "mastery_policy_version": MASTERY_POLICY_VERSION,
        "review_policy_id": REVIEW_POLICY_ID,
        "review_policy_version": REVIEW_POLICY_VERSION,
        "parameters": policy_parameters(),
    }


def tzdata_version() -> str:
    """Best-effort IANA tzdata version of the running environment.

    Local day boundaries depend on tzdata, so the version is *recorded* next to
    the projection. It is metadata, not a computed policy value.
    """
    try:  # pragma: no cover - depends on environment
        import tzdata  # type: ignore[import-not-found]

        version = getattr(tzdata, "IANA_VERSION", None) or getattr(tzdata, "__version__", None)
        if version:
            return str(version)
    except ImportError:
        pass

    for candidate in ("/usr/share/zoneinfo/tzdata.zi", "/usr/share/zoneinfo/+VERSION"):
        try:
            first_line = Path(candidate).read_text(encoding="utf-8", errors="replace").splitlines()[0]
        except (OSError, IndexError, UnicodeError):
            continue
        match = re.search(r"(\d{4}[a-z])", first_line)
        if match:
            return match.group(1)
    return "unknown"


# ---------------------------------------------------------------------------
# Time semantics
# ---------------------------------------------------------------------------


def parse_instant(value: Any, label: str) -> datetime:
    """Parse an ISO 8601 timestamp into a timezone-aware UTC instant.

    Naive timestamps are rejected. `Z` is accepted as an alias of `+00:00`,
    matching `progress-event/v0.1`.
    """
    if isinstance(value, datetime):
        return _require_aware(value, label)
    if not isinstance(value, str) or not value.strip():
        raise ReviewPolicyError(
            f"{label}: expected an ISO 8601 timestamp string or datetime",
            "invalid_timestamp",
        )
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ReviewPolicyError(
            f"{label}: invalid ISO 8601 timestamp {value!r}", "invalid_timestamp"
        ) from exc
    return _require_aware(parsed, label)


def _require_aware(value: datetime, label: str) -> datetime:
    if not isinstance(value, datetime):
        raise ReviewPolicyError(f"{label}: expected a datetime", "invalid_timestamp")
    if value.tzinfo is None or value.utcoffset() is None:
        raise ReviewPolicyError(
            f"{label}: timezone-aware timestamp is required", "invalid_timestamp"
        )
    return value.astimezone(timezone.utc)


def resolve_timezone(name: Any) -> ZoneInfo:
    """Resolve an explicit IANA timezone name.

    Machine-local time is never used implicitly: local/system aliases are
    rejected instead of being resolved against the running host.
    """
    if not isinstance(name, str) or not name.strip():
        raise ReviewPolicyError(
            "schedule_timezone: an explicit IANA timezone name is required",
            "invalid_timezone",
        )
    candidate = name.strip()
    if candidate.lower() in RESERVED_TIMEZONE_NAMES:
        raise ReviewPolicyError(
            f"schedule_timezone: {candidate!r} is not an explicit IANA timezone",
            "invalid_timezone",
        )
    try:
        return ZoneInfo(candidate)
    except (ZoneInfoNotFoundError, ValueError, KeyError) as exc:
        raise ReviewPolicyError(
            f"schedule_timezone: unknown IANA timezone {candidate!r}", "invalid_timezone"
        ) from exc


def local_date_of(instant: datetime, tz: ZoneInfo) -> date:
    """Return the local calendar date of an instant in the explicit timezone."""
    return _require_aware(instant, "instant").astimezone(tz).date()


def start_of_local_day(day: date, tz: ZoneInfo) -> datetime:
    """Return the earliest instant whose local date in `tz` is `day` or later.

    The result is the canonical `next_due_at` anchor: a review due on local date
    `D` becomes due at the start of `D` and stays due for the whole local day,
    so the daily "due today" question does not depend on the wall-clock time of
    the review that scheduled it.

    The function is total and deterministic:

    - normal case: the first instant of local date `D`;
    - local midnight does not exist (DST gap at 00:00): the first existing
      instant of local date `D` (for example ``01:00`` local);
    - the whole local date does not exist (a skipped calendar day, such as
      ``Pacific/Apia`` 2011-12-30): the first instant of the next existing
      local date. The *effective* due date is therefore recomputed from the
      returned instant instead of being trusted from the request.

    Only the IANA tzdata of the environment can change the result for a fixed
    `day`/`tz` pair; :func:`tzdata_version` records that dependency.
    """
    if isinstance(day, datetime) or not isinstance(day, date):
        raise ReviewPolicyError("day: expected a datetime.date", "invalid_policy_input")

    reference = datetime(day.year, day.month, day.day, tzinfo=tz, fold=0).astimezone(timezone.utc)
    low = reference - timedelta(hours=26)
    high = reference + timedelta(hours=26)
    while local_date_of(low, tz) >= day:
        low -= timedelta(days=1)
    while local_date_of(high, tz) < day:
        high += timedelta(days=1)
    while high - low > timedelta(seconds=1):
        middle = low + (high - low) / 2
        if local_date_of(middle, tz) < day:
            low = middle
        else:
            high = middle
    snapped = high.replace(microsecond=0)
    return snapped if local_date_of(snapped, tz) >= day else high


def _instant_to_json(instant: datetime | None) -> str | None:
    if instant is None:
        return None
    return instant.astimezone(timezone.utc).isoformat()


def _date_to_json(day: date | None) -> str | None:
    return None if day is None else day.isoformat()


# ---------------------------------------------------------------------------
# Scheduling projection
# ---------------------------------------------------------------------------


def project_review_status(
    *,
    next_due_at: datetime | None,
    next_due_local_date: date | None,
    as_of: datetime,
    tz: ZoneInfo,
) -> tuple[str, str]:
    """Project `(review_status, review_status_reason)` for an item at `as_of`.

    - `not_scheduled`: no evaluated evidence has ever scheduled the item;
    - `due`: `as_of` has reached `next_due_at` (inclusive) on the due local date;
    - `overdue`: the local date of `as_of` is after the due local date;
    - `scheduled`: `as_of` is before `next_due_at`.
    """
    if next_due_at is None:
        return "not_scheduled", "not_scheduled_no_evaluated_evidence"
    if as_of < next_due_at:
        return "scheduled", "scheduled_due_in_future"
    if next_due_local_date is not None and local_date_of(as_of, tz) > next_due_local_date:
        return "overdue", "overdue_since_next_local_date"
    return "due", "due_on_due_local_date"


# ---------------------------------------------------------------------------
# Per-item mastery / scheduling state machine
# ---------------------------------------------------------------------------


def _empty_state(review_item_id: str) -> dict[str, Any]:
    return {
        "review_item_id": review_item_id,
        "mastery_state": "new",
        "mastery_reason": "no_evaluated_evidence",
        "evaluated_evidence_count": 0,
        "successful_review_count": 0,
        "failure_count": 0,
        "insufficient_evidence_count": 0,
        "consecutive_success_count": 0,
        "consecutive_success_day_count": 0,
        "last_success_local_date": None,
        "last_review_at": None,
        "last_evidence_id": None,
        "review_interval_days": None,
        "next_due_at": None,
        "next_due_local_date": None,
        "review_status": "not_scheduled",
        "review_status_reason": "not_scheduled_no_evaluated_evidence",
        "scheduling_reason": "no_evidence_not_scheduled",
    }


def _coerce_evidence(record: Any, index: int) -> PolicyEvidence:
    label = f"evidence[{index}]"
    if isinstance(record, PolicyEvidence):
        evidence_id, occurred_at, outcome = record.evidence_id, record.occurred_at, record.outcome
    elif isinstance(record, Mapping):
        unknown = sorted(set(record) - {"evidence_id", "occurred_at", "outcome"})
        if unknown:
            raise ReviewPolicyError(f"{label}: unknown field(s): {', '.join(unknown)}")
        evidence_id = record.get("evidence_id")
        occurred_at = record.get("occurred_at")
        outcome = record.get("outcome")
    else:
        raise ReviewPolicyError(f"{label}: expected a PolicyEvidence or mapping")
    if not isinstance(evidence_id, str) or not evidence_id.strip():
        raise ReviewPolicyError(f"{label}.evidence_id: expected a non-empty string")
    if outcome not in EVIDENCE_OUTCOMES:
        raise ReviewPolicyError(
            f"{label}.outcome: expected one of {EVIDENCE_OUTCOMES}, got {outcome!r}",
            "invalid_evidence_outcome",
        )
    return PolicyEvidence(
        evidence_id=evidence_id,
        occurred_at=parse_instant(occurred_at, f"{label}.occurred_at"),
        outcome=outcome,
    )


def order_evidence(evidence: Iterable[Any], as_of: datetime, label: str = "evidence") -> list[PolicyEvidence]:
    """Validate, reject future evidence and order evidence deterministically.

    Ordering is `(occurred_at converted to UTC, evidence_id)` ascending, which is
    the same stable rule `progress-replay/v0.1` uses for events. Input order
    never changes the result. Evidence after `as_of` is a hard
    ``future_evidence`` error: replay never silently leaks future facts.
    """
    if isinstance(evidence, (str, bytes, Mapping)):
        raise ReviewPolicyError(f"{label}: expected an iterable of evidence records")
    as_of_instant = _require_aware(as_of, "as_of")
    try:
        materialized = list(evidence)
    except TypeError as exc:
        raise ReviewPolicyError(
            f"{label}: expected an iterable of evidence records"
        ) from exc

    coerced: list[PolicyEvidence] = []
    seen: set[str] = set()
    for index, record in enumerate(materialized):
        item = _coerce_evidence(record, index)
        if item.evidence_id in seen:
            raise ReviewPolicyError(
                f"{label}[{index}]: duplicate evidence_id {item.evidence_id!r}",
                "duplicate_evidence_id",
            )
        seen.add(item.evidence_id)
        if item.occurred_at > as_of_instant:
            raise ReviewPolicyError(
                f"{label}[{index}]: evidence at {item.evidence_id!r} occurs after as_of",
                "future_evidence",
            )
        coerced.append(item)

    return sorted(coerced, key=lambda item: (item.occurred_at, item.evidence_id))


def apply_evidence(
    state: Mapping[str, Any],
    evidence: PolicyEvidence,
    tz: ZoneInfo,
) -> dict[str, Any]:
    """Apply one evaluated evidence record to a mastery/scheduling state.

    The transition function is total: every `(state, outcome)` pair has a frozen
    result, so illegal state transitions cannot occur. `insufficient` evidence is
    a no-op for mastery and scheduling and only bumps its own counter.

    `state` is the internal (non-serialized) representation used by
    :func:`derive_item_state`; it keeps `last_success_local_date` as a
    `datetime.date` so that "same local day" is decided from dates, not from
    wall-clock deltas.
    """
    updated = dict(state)
    updated["last_evidence_id"] = evidence.evidence_id
    local_date = local_date_of(evidence.occurred_at, tz)

    if evidence.outcome == "insufficient":
        updated["insufficient_evidence_count"] = state["insufficient_evidence_count"] + 1
        return updated

    updated["evaluated_evidence_count"] = state["evaluated_evidence_count"] + 1
    updated["last_review_at"] = evidence.occurred_at

    if evidence.outcome == "failure":
        updated["failure_count"] = state["failure_count"] + 1
        updated["consecutive_success_count"] = 0
        updated["consecutive_success_day_count"] = 0
        # A failure breaks the run: the next success always counts as a new day.
        updated["last_success_local_date"] = None
        updated["review_interval_days"] = FAILURE_INTERVAL_DAYS
        due_date = local_date + timedelta(days=FAILURE_INTERVAL_DAYS)
        updated["next_due_at"] = start_of_local_day(due_date, tz)
        updated["next_due_local_date"] = local_date_of(updated["next_due_at"], tz)
        updated["scheduling_reason"] = "failure_schedules_retry_interval"
        prior_mastery = state["mastery_state"]
        updated["mastery_state"] = "learning"
        if prior_mastery == "mastered":
            updated["mastery_reason"] = "mastered_failure_demotes_learning"
        elif prior_mastery == "new":
            updated["mastery_reason"] = "failure_enters_learning"
        else:
            updated["mastery_reason"] = "learning_failure_keeps_learning"
        return updated

    # success
    prior_success_date = state.get("last_success_local_date")
    same_local_date = prior_success_date == local_date
    day_count = state["consecutive_success_day_count"] + (0 if same_local_date else 1)
    updated["successful_review_count"] = state["successful_review_count"] + 1
    updated["consecutive_success_count"] = state["consecutive_success_count"] + 1
    updated["consecutive_success_day_count"] = day_count
    updated["last_success_local_date"] = local_date

    ladder_index = min(day_count - 1, MAX_LADDER_INDEX)
    if ladder_index < 0:  # pragma: no cover - guarded by the run invariant
        raise ReviewPolicyError(
            "internal invariant violated: a success cannot produce a negative ladder index",
            "internal_invariant_violation",
        )
    interval_days = INTERVAL_LADDER_DAYS[ladder_index]
    updated["review_interval_days"] = interval_days
    due_date = local_date + timedelta(days=interval_days)
    updated["next_due_at"] = start_of_local_day(due_date, tz)
    updated["next_due_local_date"] = local_date_of(updated["next_due_at"], tz)
    updated["scheduling_reason"] = (
        "same_day_success_keeps_schedule" if same_local_date else "success_schedules_ladder_interval"
    )

    prior_mastery = state["mastery_state"]
    if prior_mastery == "mastered":
        updated["mastery_state"] = "mastered"
        updated["mastery_reason"] = "mastered_success_maintenance"
    elif day_count >= MASTERY_MIN_DISTINCT_SUCCESS_DAYS:
        updated["mastery_state"] = "mastered"
        updated["mastery_reason"] = "learning_success_reaches_mastery"
    else:
        updated["mastery_state"] = "learning"
        updated["mastery_reason"] = (
            "success_enters_learning" if prior_mastery == "new" else "learning_success_below_mastery"
        )
    return updated


def derive_item_state(
    review_item_id: str,
    evidence: Iterable[Any],
    *,
    as_of: datetime | str,
    schedule_timezone: str | ZoneInfo,
) -> dict[str, Any]:
    """Derive one item's mastery/scheduling projection at an explicit `as_of`."""
    if not isinstance(review_item_id, str) or not review_item_id.strip():
        raise ReviewPolicyError("review_item_id: expected a non-empty string")
    tz = schedule_timezone if isinstance(schedule_timezone, ZoneInfo) else resolve_timezone(schedule_timezone)
    as_of_instant = parse_instant(as_of, "as_of")

    state = _empty_state(review_item_id)
    for record in order_evidence(evidence, as_of_instant):
        state = apply_evidence(state, record, tz)

    status, status_reason = project_review_status(
        next_due_at=state["next_due_at"],
        next_due_local_date=state["next_due_local_date"],
        as_of=as_of_instant,
        tz=tz,
    )
    state["review_status"] = status
    state["review_status_reason"] = status_reason
    return _serialize_item(state)


def _serialize_item(state: Mapping[str, Any]) -> dict[str, Any]:
    serialized = dict(state)
    serialized["last_review_at"] = _instant_to_json(serialized["last_review_at"])
    serialized["next_due_at"] = _instant_to_json(serialized["next_due_at"])
    serialized["next_due_local_date"] = _date_to_json(serialized["next_due_local_date"])
    serialized.pop("last_success_local_date", None)
    return serialized


def derive_projection(
    evidence_by_item: Mapping[str, Iterable[Any]] | None = None,
    *,
    as_of: datetime | str,
    schedule_timezone: str | ZoneInfo,
    item_ids: Iterable[str] | None = None,
) -> dict[str, Any]:
    """Derive the policy projection for a set of review items.

    `item_ids` declares the item universe (a P4.1 concern). Items without any
    evidence project to `new` / `not_scheduled`, so "no evidence" is never
    confused with "no item". `due_count` is derived from the item level
    projection only; it counts items, never events.
    """
    tz = schedule_timezone if isinstance(schedule_timezone, ZoneInfo) else resolve_timezone(schedule_timezone)
    as_of_instant = parse_instant(as_of, "as_of")

    if evidence_by_item is None:
        evidence_by_item = {}
    if not isinstance(evidence_by_item, Mapping):
        raise ReviewPolicyError("evidence_by_item: expected a mapping of item id to evidence")

    declared: list[str] = []

    def _declare(item_id: Any, label: str) -> str:
        if not isinstance(item_id, str) or not item_id.strip():
            raise ReviewPolicyError(f"{label}: expected a non-empty review item id")
        declared.append(item_id)
        return item_id

    for key in evidence_by_item:
        _declare(key, "evidence_by_item key")
    if item_ids is not None:
        if isinstance(item_ids, (str, bytes)):
            raise ReviewPolicyError("item_ids: expected an iterable of item ids")
        for index, item_id in enumerate(item_ids):
            _declare(item_id, f"item_ids[{index}]")

    items: dict[str, Any] = {}
    for item_id in sorted(set(declared)):
        items[item_id] = derive_item_state(
            item_id,
            evidence_by_item.get(item_id, ()),
            as_of=as_of_instant,
            schedule_timezone=tz,
        )

    counts = {status: 0 for status in REVIEW_STATUSES}
    for item in items.values():
        counts[item["review_status"]] += 1

    return {
        "schema_version": PROJECTION_SCHEMA_VERSION,
        "policy": policy_identity(),
        "as_of": _instant_to_json(as_of_instant),
        "schedule_timezone": str(tz.key),
        "tzdata_version": tzdata_version(),
        "items": items,
        "review": {
            "total_items": len(items),
            "not_scheduled_count": counts["not_scheduled"],
            "scheduled_count": counts["scheduled"],
            "due_today_count": counts["due"],
            "overdue_count": counts["overdue"],
            "due_count": counts["due"] + counts["overdue"],
        },
        "mastery": {
            "new_count": sum(1 for item in items.values() if item["mastery_state"] == "new"),
            "learning_count": sum(1 for item in items.values() if item["mastery_state"] == "learning"),
            "mastered_count": sum(1 for item in items.values() if item["mastery_state"] == "mastered"),
        },
    }
