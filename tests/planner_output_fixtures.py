"""Build synthetic Planner Output contract examples without scheduling tasks."""
from __future__ import annotations

import copy
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from engine.rules.review_policy_v01 import resolve_timezone
from planner_contract_fixtures import build_minimal_snapshot


def build_minimal_output(
    root: Path,
    input_snapshot: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Return a valid synthetic input/output pair with seven empty days."""
    input_snapshot = copy.deepcopy(input_snapshot) if input_snapshot is not None else build_minimal_snapshot(root)
    as_of = input_snapshot["as_of"]
    timezone_name = input_snapshot["timezone"]
    config = input_snapshot["inputs"]["user_configuration"]
    local_as_of = datetime.fromisoformat(as_of.replace("Z", "+00:00"))
    first_date = local_as_of.astimezone(resolve_timezone(timezone_name)).date()
    capacity = config["daily_available_minutes"]
    days = []
    for offset in range(7):
        local_date = first_date + timedelta(days=offset)
        days.append({
            "day_offset": offset,
            "local_date": local_date.isoformat(),
            "study_day": local_date.isoweekday() in config["study_days"],
            # Synthetic structure only; P5.3 does not prescribe rest-day capacity.
            "capacity_minutes": capacity,
            "planned_minutes": 0,
            "remaining_minutes": capacity,
            "tasks": [],
            "unmet_demand": [],
        })
    output = {
        "schema_version": "planner-output/v0.1",
        "planner_policy": {
            "policy_id": "planner-policy/contract-fixture",
            "policy_version": "v0.1",
        },
        "input_snapshot_schema_version": input_snapshot["schema_version"],
        "as_of": as_of,
        "timezone": timezone_name,
        "generated_for_local_date": first_date.isoformat(),
        "horizon": {"unit": "local_calendar_days", "day_count": 7},
        "days": days,
        "explain_traces": [],
    }
    return input_snapshot, output


def apply_patch(document: Any, patch: dict[str, Any], label: str) -> None:
    """Apply a small deterministic JSON patch used only by contract fixtures."""
    operation = patch.get("op")
    path = patch.get("path")
    if operation not in {"replace", "remove"} or not isinstance(path, list) or not path or any(not isinstance(part, str) for part in path):
        raise ValueError(f"{label}: malformed patch")
    parent = document
    for part in path[:-1]:
        if isinstance(parent, dict) and part in parent:
            parent = parent[part]
        elif isinstance(parent, list) and part.isdigit() and int(part) < len(parent):
            parent = parent[int(part)]
        else:
            raise ValueError(f"{label}: patch path does not exist")
    final = path[-1]
    if isinstance(parent, dict) and final in parent:
        if operation == "remove":
            del parent[final]
        elif "value" in patch:
            parent[final] = copy.deepcopy(patch["value"])
        else:
            raise ValueError(f"{label}: replace patch needs value")
    elif isinstance(parent, list) and final.isdigit() and int(final) < len(parent):
        if operation == "remove":
            parent.pop(int(final))
        elif "value" in patch:
            parent[int(final)] = copy.deepcopy(patch["value"])
        else:
            raise ValueError(f"{label}: replace patch needs value")
    else:
        raise ValueError(f"{label}: patch target does not exist")
