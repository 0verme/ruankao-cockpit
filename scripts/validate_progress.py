#!/usr/bin/env python3
"""Validate Progress Event fixtures and deterministic replay invariants."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import random
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.progress import ProgressValidationError, replay  # noqa: E402

EVENT_SCHEMA_VERSION = "progress-event/v0.1"
STATE_SCHEMA_VERSION = "progress-state/v0.1"
FIXTURE_SCHEMA_VERSION = "progress-fixture/v0.1"
REPLAY_RULE_VERSION = "progress-replay/v0.1"
FORBIDDEN_STATE_KEYS = {
    "mastery",
    "mastered",
    "review_due",
    "review_interval",
    "forgetting_curve",
    "sm2",
    "fsrs",
    "planner",
}


class ValidationError(Exception):
    pass


def load_json(path: Path) -> Any:
    try:
        with path.open(encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise ValidationError(f"cannot read JSON {path}: {exc}") from exc


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def walk_state_keys(value: Any, label: str = "state") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            require(key not in FORBIDDEN_STATE_KEYS, f"{label}: out-of-scope state key {key!r}")
            walk_state_keys(child, f"{label}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            walk_state_keys(child, f"{label}[{index}]")


def validate_contract_schema(root: Path) -> dict[str, Any]:
    schema = load_json(root / "data/progress/schema.json")
    require(schema.get("contract") == "progress-model/v0.1", "schema: wrong contract version")
    require(schema.get("event_schema_version") == EVENT_SCHEMA_VERSION, "schema: wrong event version")
    require(schema.get("state_schema_version") == STATE_SCHEMA_VERSION, "schema: wrong state version")
    require(schema.get("fixture_schema_version") == FIXTURE_SCHEMA_VERSION, "schema: wrong fixture version")
    require(schema.get("replay_rule_version") == REPLAY_RULE_VERSION, "schema: wrong replay version")
    require(schema.get("source_of_truth") == "events", "schema: events must be source of truth")
    event_types = schema.get("event_types")
    require(set(event_types or {}) == {"comprehensive_attempt", "case_attempt", "study_session"}, "schema: event type set changed")
    return schema


def validate_fixture_shape(data: Any, path: Path) -> None:
    label = path.name
    require(isinstance(data, dict), f"{label}: fixture must be an object")
    allowed = {"schema_version", "fixture_id", "description", "events", "expected_state", "expected_error"}
    require(set(data) <= allowed, f"{label}: unknown fixture field")
    require(data.get("schema_version") == FIXTURE_SCHEMA_VERSION, f"{label}: wrong fixture schema")
    require(isinstance(data.get("fixture_id"), str) and data["fixture_id"].strip(), f"{label}: fixture_id required")
    require(isinstance(data.get("events"), list), f"{label}: events must be a list")
    has_error = "expected_error" in data
    has_state = "expected_state" in data
    require(not (has_error and has_state), f"{label}: expected_error and expected_state are mutually exclusive")
    if has_error:
        require(isinstance(data["expected_error"], str) and data["expected_error"].strip(), f"{label}: invalid expected_error")
    if has_state:
        require(isinstance(data["expected_state"], dict), f"{label}: expected_state must be an object")


def validate_fixture(data: dict[str, Any], path: Path, taxonomy: dict[str, Any], capabilities: dict[str, Any]) -> str:
    label = path.name
    events = data["events"]
    expected_error = data.get("expected_error")
    try:
        state = replay(events, taxonomy, capabilities)
    except ProgressValidationError as exc:
        if expected_error is None:
            raise ValidationError(f"{label}: unexpected replay failure [{exc.category}]: {exc}") from exc
        require(exc.category == expected_error, f"{label}: expected {expected_error}, got {exc.category}: {exc}")
        return "expected failure"

    if expected_error is not None:
        raise ValidationError(f"{label}: expected replay failure [{expected_error}] but replay passed")

    repeat_state = replay(events, taxonomy, capabilities)
    require(state == repeat_state, f"{label}: replay repeatability failed")

    shuffled = list(events)
    random.Random(20260921).shuffle(shuffled)
    shuffled_state = replay(shuffled, taxonomy, capabilities)
    require(state == shuffled_state, f"{label}: input order independence failed")

    if "expected_state" in data:
        require(state == data["expected_state"], f"{label}: expected_state does not match replay")

    require(state.get("schema_version") == STATE_SCHEMA_VERSION, f"{label}: wrong state schema")
    require(state.get("replay_rule_version") == REPLAY_RULE_VERSION, f"{label}: wrong replay rule version")
    walk_state_keys(state)
    return "passed"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        validate_contract_schema(root)
        taxonomy = load_json(root / "taxonomy/taxonomy.json")
        capabilities = load_json(root / "taxonomy/capabilities.json")
        fixture_dir = root / "data/progress/fixtures"
        fixture_paths = sorted(fixture_dir.glob("*.json"))
        require(fixture_paths, "fixtures: no JSON fixtures found")
        fixture_ids: set[str] = set()
        passed = 0
        expected_failures = 0
        for path in fixture_paths:
            data = load_json(path)
            validate_fixture_shape(data, path)
            fixture_id = data["fixture_id"]
            require(fixture_id not in fixture_ids, f"fixtures: duplicate fixture_id {fixture_id}")
            fixture_ids.add(fixture_id)
            result = validate_fixture(data, path, taxonomy, capabilities)
            if result == "passed":
                passed += 1
            else:
                expected_failures += 1
        print("PASS progress contract schema validation")
        print(f"  fixtures: {len(fixture_paths)} ({passed} valid replay / {expected_failures} expected rejection)")
        print("PASS deterministic replay repeatability")
        print("PASS deterministic replay input-order independence")
        print("PASS duplicate and reference rejection fixtures")
        print("PASS null semantics and out-of-scope state guard")
        return 0
    except ValidationError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
