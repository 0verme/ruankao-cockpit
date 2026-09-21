#!/usr/bin/env python3
"""Validate Review Model / Evidence v0.1 contract fixtures."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.review import (  # noqa: E402
    EVIDENCE_SCHEMA_VERSION,
    ITEM_SCHEMA_VERSION,
    REVIEW_EVENT_SCHEMA_VERSION,
    REVIEW_FIXTURE_SCHEMA_VERSION,
    ReviewValidationError,
    project_review_evidence,
)


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


def validate_schema(root: Path) -> dict[str, Any]:
    schema = load_json(root / "data/review/schema.json")
    require(schema.get("contract") == "review-model/v0.1", "schema: wrong contract")
    require(schema.get("item_schema_version") == ITEM_SCHEMA_VERSION, "schema: wrong item version")
    require(schema.get("event_schema_version") == REVIEW_EVENT_SCHEMA_VERSION, "schema: wrong event version")
    require(schema.get("evidence_schema_version") == EVIDENCE_SCHEMA_VERSION, "schema: wrong evidence version")
    require(schema.get("fixture_schema_version") == REVIEW_FIXTURE_SCHEMA_VERSION, "schema: wrong fixture version")
    require(
        set(schema.get("item_kinds", {})) == {"topic", "question", "case_capability"},
        "schema: item kind set changed",
    )
    require(
        schema.get("identity", {}).get("namespace") == "review",
        "schema: identity namespace changed",
    )
    return schema


def validate_fixture_shape(data: Any, path: Path) -> None:
    label = path.name
    require(isinstance(data, dict), f"{label}: fixture must be an object")
    allowed = {
        "schema_version",
        "fixture_id",
        "description",
        "items",
        "progress_events",
        "review_events",
        "expected_evidence",
    }
    require(set(data) <= allowed, f"{label}: unknown fixture field")
    require(data.get("schema_version") == REVIEW_FIXTURE_SCHEMA_VERSION, f"{label}: wrong fixture schema")
    require(isinstance(data.get("fixture_id"), str) and data["fixture_id"].strip(), f"{label}: fixture_id required")
    for key in ("items", "progress_events", "review_events", "expected_evidence"):
        require(isinstance(data.get(key), list), f"{label}: {key} must be a list")


def validate_fixture(data: dict[str, Any], path: Path, taxonomy: dict[str, Any], capabilities: dict[str, Any]) -> None:
    label = path.name
    try:
        actual = project_review_evidence(
            data["progress_events"],
            data["review_events"],
            data["items"],
            taxonomy,
            capabilities,
        )
    except ReviewValidationError as exc:
        raise ValidationError(f"{label}: [{exc.category}] {exc}") from exc
    require(actual == data["expected_evidence"], f"{label}: expected_evidence does not match projection")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        validate_schema(root)
        taxonomy = load_json(root / "taxonomy/taxonomy.json")
        capabilities = load_json(root / "taxonomy/capabilities.json")
        fixture_paths = sorted((root / "data/review/contract-fixtures").glob("*.json"))
        require(fixture_paths, "contract fixtures: no JSON fixtures found")
        fixture_ids: set[str] = set()
        for path in fixture_paths:
            data = load_json(path)
            validate_fixture_shape(data, path)
            fixture_id = data["fixture_id"]
            require(fixture_id not in fixture_ids, f"contract fixtures: duplicate fixture_id {fixture_id}")
            fixture_ids.add(fixture_id)
            validate_fixture(data, path, taxonomy, capabilities)
        print("PASS Review Model / Evidence v0.1 schema validation")
        print(f"PASS deterministic evidence projection ({len(fixture_paths)} fixture(s))")
        print("PASS explicit initial_learning/review context boundary")
        print("PASS policy-neutral evidence and source-reference validation")
        return 0
    except ValidationError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
