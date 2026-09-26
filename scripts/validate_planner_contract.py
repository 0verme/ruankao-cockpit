#!/usr/bin/env python3
"""Validate Planner input/output contract schemas and static fixtures; do not generate plans."""
from __future__ import annotations

import argparse
import copy
import json
import math
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
import re
import sys
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
TESTS = ROOT / "tests"
if str(TESTS) not in sys.path:
    sys.path.insert(0, str(TESTS))

from engine.rules.review_policy_v01 import ReviewPolicyError, resolve_timezone  # noqa: E402
from planner_contract_fixtures import build_minimal_snapshot  # noqa: E402
from planner_output_fixtures import apply_patch as apply_output_fixture_patch  # noqa: E402
from planner_output_fixtures import build_minimal_output  # noqa: E402

SNAPSHOT_SCHEMA_VERSION = "planner-input/v0.1"
USER_CONFIGURATION_SCHEMA_VERSION = "user-configuration/v0.1"
PLANNER_POLICY_ID = "planner-policy/input-contract"
PLANNER_POLICY_VERSION = "v0.1"
PROGRESS_STATE_SCHEMA_VERSION = "progress-state/v0.1"
PROGRESS_REPLAY_VERSION = "progress-replay/v0.1"
PROGRESS_EVENT_SCHEMA_VERSION = "progress-event/v0.1"
MASTERY_REVIEW_STATE_SCHEMA_VERSION = "mastery-review-state/v0.1"
TAXONOMY_VERSION = "0.1"
CAPABILITY_VERSION = "0.1"
PLANNER_OUTPUT_SCHEMA_VERSION = "planner-output/v0.1"
PLANNER_OUTPUT_HORIZON_DAYS = 7
PLANNER_OUTPUT_HORIZON_UNIT = "local_calendar_days"
SUPPORTED_PLAN_TASK_TYPES = {"review", "new_learning"}
SUPPORTED_DEMAND_TYPES = {"review", "new_learning"}
SUPPORTED_TARGET_KINDS = {"review_item", "topic"}
REVIEW_ITEM_ID_PATTERN = re.compile(
    r"^review/(?:topic/[A-Za-z0-9][A-Za-z0-9._:-]*|"
    r"question/[A-Za-z0-9][A-Za-z0-9._:-]*/[A-Za-z0-9][A-Za-z0-9._:-]*|"
    r"case_capability/[A-Za-z0-9][A-Za-z0-9._:-]*)$"
)
TOPIC_ID_PATTERN = re.compile(r"^[A-Z][A-Z0-9_]*(?:\.[A-Z][A-Z0-9_]*){0,2}$")
REASON_CODE_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")


class PlannerContractError(ValueError):
    """Raised when one complete planner input cannot be accepted safely."""

    def __init__(self, message: str, category: str = "invalid_planner_input") -> None:
        self.category = category
        super().__init__(message)


def _fail(message: str, category: str = "invalid_planner_input") -> None:
    raise PlannerContractError(message, category)


def _require(condition: bool, message: str, category: str = "invalid_planner_input") -> None:
    if not condition:
        _fail(message, category)


def load_json(path: Path) -> Any:
    try:
        with path.open(encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise PlannerContractError(f"cannot read JSON {path}: {exc}", "invalid_contract_schema") from exc


def _object(value: Any, label: str, category: str = "invalid_planner_input") -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        _fail(f"{label}: expected an object", category)
    return value


def _exact_keys(value: Mapping[str, Any], keys: set[str], label: str, category: str = "invalid_planner_input") -> None:
    missing = sorted(keys - set(value))
    extra = sorted(set(value) - keys)
    if missing or extra:
        pieces = []
        if missing:
            pieces.append("missing " + ", ".join(missing))
        if extra:
            pieces.append("unsupported " + ", ".join(extra))
        _fail(f"{label}: {'; '.join(pieces)}", category)


def _nonempty_string(value: Any, label: str, category: str = "invalid_planner_input") -> str:
    if not isinstance(value, str) or not value.strip() or "\x00" in value:
        _fail(f"{label}: expected a non-empty string", category)
    return value


def _count(value: Any, label: str, category: str = "invalid_domain_state") -> None:
    if type(value) is not int or value < 0:
        _fail(f"{label}: expected a non-negative integer", category)


def _ratio(value: Any, label: str, category: str = "invalid_domain_state") -> None:
    if value is None:
        return
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not 0 <= value <= 1:
        _fail(f"{label}: expected a ratio in [0, 1] or null", category)


def _parse_instant(value: Any, label: str) -> datetime:
    if not isinstance(value, str) or not value.strip():
        _fail(f"{label}: expected an ISO 8601 timestamp", "invalid_timestamp")
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise PlannerContractError(f"{label}: invalid ISO 8601 timestamp {value!r}", "invalid_timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        _fail(f"{label}: timezone-aware timestamp is required", "invalid_timestamp")
    return parsed.astimezone(timezone.utc)


def _canonical_instant(value: str) -> str:
    return _parse_instant(value, "timestamp").isoformat().replace("+00:00", "Z")


def _validate_timezone(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        _fail(f"{label}: an explicit IANA timezone is required", "invalid_timezone")
    try:
        resolve_timezone(value)
    except ReviewPolicyError as exc:
        raise PlannerContractError(f"{label}: {exc}", "invalid_timezone") from exc
    return value


def validate_contract_schemas(root: Path = ROOT) -> None:
    snapshot_schema = load_json(root / "data/planner/planner-input.schema.json")
    config_schema = load_json(root / "data/planner/user-configuration.schema.json")
    progress_schema = load_json(root / "data/progress/schema.json")
    review_schema = load_json(root / "data/review/schema.json")
    review_state_schema = load_json(root / "data/review/mastery-review-state.schema.json")

    _require(snapshot_schema.get("$schema", "").endswith("2020-12/schema"), "Planner input schema must use JSON Schema 2020-12", "invalid_contract_schema")
    _require(snapshot_schema.get("title") == "Planner Input Snapshot v0.1", "Planner input schema title/version mismatch", "invalid_contract_schema")
    _require(snapshot_schema.get("properties", {}).get("schema_version", {}).get("const") == SNAPSHOT_SCHEMA_VERSION, "Planner input schema version mismatch", "invalid_contract_schema")
    _require(snapshot_schema.get("additionalProperties") is False, "Planner input schema must reject additional properties", "invalid_contract_schema")
    _require(set(snapshot_schema.get("required", [])) == {"schema_version", "as_of", "timezone", "planner_policy", "inputs"}, "Planner input schema required fields mismatch", "invalid_contract_schema")
    policy_schema = snapshot_schema.get("$defs", {}).get("plannerPolicy", {}).get("properties", {})
    _require(policy_schema.get("policy_id", {}).get("const") == PLANNER_POLICY_ID and policy_schema.get("policy_version", {}).get("const") == PLANNER_POLICY_VERSION, "Planner input policy identity schema mismatch", "invalid_contract_schema")
    input_schema = snapshot_schema.get("$defs", {}).get("inputs", {})
    _require(set(input_schema.get("required", [])) == {"progress_state", "mastery_review_state", "taxonomy", "capabilities", "user_configuration"}, "Planner input source allowlist mismatch", "invalid_contract_schema")
    input_properties = input_schema.get("properties", {})
    _require(input_properties.get("mastery_review_state", {}).get("$ref") == "../review/mastery-review-state.schema.json", "MasteryReviewState schema reference mismatch", "invalid_contract_schema")
    _require(input_properties.get("user_configuration", {}).get("$ref") == "user-configuration.schema.json", "User Configuration schema reference mismatch", "invalid_contract_schema")
    _require(config_schema.get("$schema", "").endswith("2020-12/schema"), "User Configuration schema must use JSON Schema 2020-12", "invalid_contract_schema")
    _require(config_schema.get("title") == "User Configuration v0.1", "User Configuration schema title/version mismatch", "invalid_contract_schema")
    _require(config_schema.get("properties", {}).get("schema_version", {}).get("const") == USER_CONFIGURATION_SCHEMA_VERSION, "User Configuration schema version mismatch", "invalid_contract_schema")
    _require(config_schema.get("additionalProperties") is False, "User Configuration schema must reject additional properties", "invalid_contract_schema")
    config_properties = config_schema.get("properties", {})
    _require(set(config_schema.get("required", [])) == {"schema_version", "timezone", "daily_available_minutes", "study_days"}, "User Configuration required fields mismatch", "invalid_contract_schema")
    _require(config_properties.get("daily_available_minutes", {}).get("minimum") == 0 and config_properties.get("daily_available_minutes", {}).get("maximum") == 1440, "User Configuration minute bounds mismatch", "invalid_contract_schema")
    study_schema = config_properties.get("study_days", {})
    _require(study_schema.get("uniqueItems") is True and study_schema.get("items", {}).get("minimum") == 1 and study_schema.get("items", {}).get("maximum") == 7, "User Configuration weekday schema mismatch", "invalid_contract_schema")
    _require(progress_schema.get("state_schema_version") == PROGRESS_STATE_SCHEMA_VERSION, "ProgressState source contract version mismatch", "invalid_contract_schema")
    _require(progress_schema.get("replay_rule_version") == PROGRESS_REPLAY_VERSION, "Progress replay source contract version mismatch", "invalid_contract_schema")
    _require(review_schema.get("mastery_review_state_schema") == MASTERY_REVIEW_STATE_SCHEMA_VERSION, "MasteryReviewState source contract version mismatch", "invalid_contract_schema")
    _require(review_state_schema.get("properties", {}).get("schema_version", {}).get("const") == MASTERY_REVIEW_STATE_SCHEMA_VERSION, "MasteryReviewState schema metadata mismatch", "invalid_contract_schema")
    _require((root / "data/review/mastery-review-state.schema.json").is_file(), "MasteryReviewState schema reference is missing", "invalid_contract_schema")
    _constant_object_from_schema(review_state_schema.get("$defs", {}).get("policy", {}), "MasteryReviewState.policy")
    _constant_object_from_schema(review_state_schema.get("$defs", {}).get("outcomeAdapter", {}), "MasteryReviewState.outcome_adapter")

    output_schema = load_json(root / "data/planner/planner-output.schema.json")
    _require(output_schema.get("$schema", "").endswith("2020-12/schema"), "Planner output schema must use JSON Schema 2020-12", "invalid_contract_schema")
    _require(output_schema.get("title") == "Planner Output v0.1", "Planner output schema title/version mismatch", "invalid_contract_schema")
    output_properties = output_schema.get("properties", {})
    _require(output_properties.get("schema_version", {}).get("const") == PLANNER_OUTPUT_SCHEMA_VERSION, "Planner output schema version mismatch", "invalid_contract_schema")
    _require(output_properties.get("input_snapshot_schema_version", {}).get("const") == SNAPSHOT_SCHEMA_VERSION, "Planner output input schema trace mismatch", "invalid_contract_schema")
    _require(output_schema.get("additionalProperties") is False, "Planner output must reject additional root properties", "invalid_contract_schema")
    _require(set(output_schema.get("required", [])) == {
        "schema_version", "planner_policy", "input_snapshot_schema_version", "as_of", "timezone",
        "generated_for_local_date", "horizon", "days", "explain_traces",
    }, "Planner output required fields mismatch", "invalid_contract_schema")
    horizon_schema = output_schema.get("$defs", {}).get("horizon", {}).get("properties", {})
    _require(horizon_schema.get("unit", {}).get("const") == PLANNER_OUTPUT_HORIZON_UNIT, "Planner output horizon unit mismatch", "invalid_contract_schema")
    _require(horizon_schema.get("day_count", {}).get("const") == PLANNER_OUTPUT_HORIZON_DAYS, "Planner output horizon length mismatch", "invalid_contract_schema")
    days_schema = output_properties.get("days", {})
    _require(days_schema.get("minItems") == PLANNER_OUTPUT_HORIZON_DAYS and days_schema.get("maxItems") == PLANNER_OUTPUT_HORIZON_DAYS, "Planner output day count schema mismatch", "invalid_contract_schema")
    for name in ("planDay", "planTask", "unmetDemand", "explainTrace"):
        _require(output_schema.get("$defs", {}).get(name, {}).get("additionalProperties") is False, f"Planner output {name} must reject unsupported fields", "invalid_contract_schema")
    output_defs = output_schema.get("$defs", {})
    plan_task_definition = output_defs.get("planTask", {})
    plan_task_schema = plan_task_definition.get("properties", {})
    _require(set(plan_task_schema.get("task_type", {}).get("enum", [])) == SUPPORTED_PLAN_TASK_TYPES, "Planner output task type scope mismatch", "invalid_contract_schema")
    _require(set(plan_task_schema.get("target_kind", {}).get("enum", [])) == SUPPORTED_TARGET_KINDS, "Planner output target kind scope mismatch", "invalid_contract_schema")
    target_ref_schema = output_defs.get("targetRef", {})
    target_patterns = {
        branch.get("pattern") for branch in target_ref_schema.get("anyOf", [])
        if isinstance(branch, Mapping)
    }
    _require(
        REVIEW_ITEM_ID_PATTERN.pattern in target_patterns and TOPIC_ID_PATTERN.pattern in target_patterns,
        "Planner output target identity patterns mismatch",
        "invalid_contract_schema",
    )
    demand_schema = output_defs.get("unmetDemand", {}).get("properties", {})
    _require(set(demand_schema.get("demand_type", {}).get("enum", [])) == SUPPORTED_DEMAND_TYPES, "Planner output demand type scope mismatch", "invalid_contract_schema")
    _require(set(demand_schema.get("target_kind", {}).get("enum", [])) == SUPPORTED_TARGET_KINDS, "Planner output demand target kind scope mismatch", "invalid_contract_schema")
    _require(set(plan_task_definition.get("required", [])) == {
        "task_id", "task_type", "target_kind", "target_ref", "planned_minutes", "explain_trace_id",
    }, "Planner output PlanTask required fields mismatch", "invalid_contract_schema")
    task_minutes = plan_task_schema.get("planned_minutes", {})
    _require(task_minutes.get("type") == "integer" and task_minutes.get("minimum") == 0 and task_minutes.get("maximum") == 1440, "Planner output PlanTask minute range mismatch", "invalid_contract_schema")
    plan_day_properties = output_defs.get("planDay", {}).get("properties", {})
    for minute_field in ("capacity_minutes", "planned_minutes", "remaining_minutes"):
        minute_schema = plan_day_properties.get(minute_field, {})
        _require(minute_schema.get("type") == "integer" and minute_schema.get("minimum") == 0 and minute_schema.get("maximum") == 1440, f"Planner output PlanDay.{minute_field} range mismatch", "invalid_contract_schema")
    demand_properties = output_defs.get("unmetDemand", {}).get("properties", {})
    requested_minutes = demand_properties.get("requested_minutes", {})
    _require(requested_minutes.get("type") == "integer" and requested_minutes.get("minimum") == 0 and requested_minutes.get("maximum") == 1440, "Planner output UnmetDemand minute range mismatch", "invalid_contract_schema")
    trace_definition = output_defs.get("explainTrace", {})
    trace_properties = trace_definition.get("properties", {})
    _require(set(trace_properties.get("target_kind", {}).get("enum", [])) == SUPPORTED_TARGET_KINDS, "Planner output trace target kind scope mismatch", "invalid_contract_schema")
    _require(trace_properties.get("reason_code", {}).get("pattern") == REASON_CODE_PATTERN.pattern, "Planner output reason_code slot mismatch", "invalid_contract_schema")
    _require(set(trace_definition.get("required", [])) == {
        "trace_id", "subject_kind", "subject_id", "decision_category", "reason_code", "planner_policy",
        "input_references", "target_kind", "target_ref", "structured_inputs",
    }, "Planner output ExplainTrace required fields mismatch", "invalid_contract_schema")


def _constant_object_from_schema(schema: Mapping[str, Any], label: str) -> dict[str, Any]:
    properties = schema.get("properties")
    required = schema.get("required")
    _require(isinstance(properties, Mapping) and isinstance(required, list), f"{label}: schema constants are malformed", "invalid_contract_schema")
    result: dict[str, Any] = {}
    for key in required:
        child = properties.get(key)
        _require(isinstance(child, Mapping), f"{label}.{key}: schema property is missing", "invalid_contract_schema")
        if "const" in child:
            result[key] = child["const"]
        elif "properties" in child:
            result[key] = _constant_object_from_schema(child, f"{label}.{key}")
        else:
            _fail(f"{label}.{key}: expected frozen schema constant", "invalid_contract_schema")
    return result


def _load_supported_catalogs(root: Path) -> tuple[dict[str, Any], set[str], set[str]]:
    taxonomy = load_json(root / "taxonomy/taxonomy.json")
    capabilities = load_json(root / "taxonomy/capabilities.json")
    _require(isinstance(taxonomy, Mapping), "taxonomy catalog must be an object", "invalid_catalog_version")
    _require(isinstance(capabilities, Mapping), "capability catalog must be an object", "invalid_catalog_version")
    _require(taxonomy.get("taxonomy_version") == TAXONOMY_VERSION, "unsupported repository taxonomy version", "invalid_catalog_version")
    _require(capabilities.get("taxonomy_version") == CAPABILITY_VERSION, "unsupported repository capability version", "invalid_catalog_version")
    nodes = taxonomy.get("nodes")
    capability_rows = capabilities.get("capabilities")
    _require(isinstance(nodes, list) and bool(nodes), "repository taxonomy nodes are invalid", "invalid_catalog_version")
    _require(isinstance(capability_rows, list) and bool(capability_rows), "repository capability catalog is invalid", "invalid_catalog_version")
    topic_ids = {_nonempty_string(row.get("id"), "taxonomy node id", "invalid_catalog_version") for row in nodes if isinstance(row, Mapping)}
    capability_ids = {_nonempty_string(row.get("id"), "capability id", "invalid_catalog_version") for row in capability_rows if isinstance(row, Mapping)}
    _require(len(topic_ids) == len(nodes), "repository taxonomy contains malformed or duplicate IDs", "invalid_catalog_version")
    _require(len(capability_ids) == len(capability_rows), "repository capabilities contain malformed or duplicate IDs", "invalid_catalog_version")
    return {"taxonomy": taxonomy, "capabilities": capabilities}, topic_ids, capability_ids


def _validate_catalog_manifest(
    manifest: Any,
    *,
    label: str,
    version_key: str,
    ids_key: str,
    expected_version: str,
    supported_ids: set[str],
) -> set[str]:
    value = _object(manifest, label, "invalid_catalog_version")
    _exact_keys(value, {version_key, ids_key}, label, "invalid_catalog_version")
    if value.get(version_key) != expected_version:
        _fail(f"{label}.{version_key}: unsupported catalog version {value.get(version_key)!r}", "invalid_catalog_version")
    raw_ids = value.get(ids_key)
    if not isinstance(raw_ids, list) or any(not isinstance(item, str) or not item for item in raw_ids):
        _fail(f"{label}.{ids_key}: expected a list of canonical IDs", "invalid_catalog_version")
    if len(raw_ids) != len(set(raw_ids)):
        _fail(f"{label}.{ids_key}: duplicate ID", "invalid_catalog_version")
    ids = set(raw_ids)
    if ids != supported_ids:
        _fail(f"{label}.{ids_key}: IDs do not match the supported catalog version", "invalid_catalog_version")
    return ids


def _validate_progress_state(
    state_value: Any,
    topic_ids: set[str],
    capability_ids: set[str],
    taxonomy_version: str,
    capability_version: str,
) -> Mapping[str, Any]:
    state = _object(state_value, "ProgressState", "invalid_domain_state")
    required = {
        "schema_version", "replay_rule_version", "event_schema_version", "taxonomy_version",
        "capability_version", "replayed_event_count", "global", "case", "topics", "capabilities",
        "errors", "coverage", "study",
    }
    _exact_keys(state, required, "ProgressState", "invalid_domain_state")
    if state.get("schema_version") != PROGRESS_STATE_SCHEMA_VERSION:
        _fail("ProgressState has an unsupported schema_version", "invalid_schema_version")
    if state.get("replay_rule_version") != PROGRESS_REPLAY_VERSION or state.get("event_schema_version") != PROGRESS_EVENT_SCHEMA_VERSION:
        _fail("ProgressState has an unsupported replay/event version", "invalid_schema_version")
    if state.get("taxonomy_version") != taxonomy_version:
        _fail("ProgressState taxonomy_version does not match the catalog", "invalid_catalog_version")
    if state.get("capability_version") != capability_version:
        _fail("ProgressState capability_version does not match the catalog", "invalid_catalog_version")
    _count(state.get("replayed_event_count"), "ProgressState.replayed_event_count")

    metric_shapes = {
        "global": ({"attempt_count", "correct_count", "incorrect_count", "accuracy"}, {"attempt_count", "correct_count", "incorrect_count"}),
        "case": ({"attempt_count", "scored_attempt_count", "score_earned", "score_possible", "score_ratio"}, {"attempt_count", "scored_attempt_count", "score_earned", "score_possible"}),
    }
    for name, (keys, count_keys) in metric_shapes.items():
        metric = _object(state.get(name), f"ProgressState.{name}", "invalid_domain_state")
        _exact_keys(metric, keys, f"ProgressState.{name}", "invalid_domain_state")
        for key in count_keys:
            _count(metric.get(key), f"ProgressState.{name}.{key}")
        _ratio(metric.get("accuracy", metric.get("score_ratio")), f"ProgressState.{name}.ratio")

    for name, expected_ids, metric_keys, count_keys, ratio_key in (
        ("topics", topic_ids, {"attempt_count", "correct_count", "incorrect_count", "accuracy"}, {"attempt_count", "correct_count", "incorrect_count"}, "accuracy"),
        ("capabilities", capability_ids, {"attempt_count", "score_earned", "score_possible", "score_ratio", "evidence_status"}, {"attempt_count", "score_earned", "score_possible"}, "score_ratio"),
    ):
        rows = _object(state.get(name), f"ProgressState.{name}", "invalid_domain_state")
        unknown = set(rows) - expected_ids
        if unknown:
            category = "unknown_topic_id" if name == "topics" else "unknown_capability_id"
            _fail(f"ProgressState.{name}: unknown canonical ID(s): {', '.join(sorted(unknown))}", category)
        if set(rows) != expected_ids:
            _fail(f"ProgressState.{name}: state does not cover the complete catalog ID set", "invalid_domain_state")
        for identity, raw_metric in rows.items():
            metric = _object(raw_metric, f"ProgressState.{name}.{identity}", "invalid_domain_state")
            _exact_keys(metric, metric_keys, f"ProgressState.{name}.{identity}", "invalid_domain_state")
            for key in count_keys:
                _count(metric.get(key), f"ProgressState.{name}.{identity}.{key}")
            _ratio(metric.get(ratio_key), f"ProgressState.{name}.{identity}.{ratio_key}")
            if name == "capabilities" and metric.get("evidence_status") not in {"sufficient", "insufficient_evidence"}:
                _fail(f"ProgressState.capabilities.{identity}: unsupported evidence_status", "invalid_domain_state")

    errors = _object(state.get("errors"), "ProgressState.errors", "invalid_domain_state")
    error_keys = {"error_count", "classified_error_count", "unclassified_error_count", "error_count_by_cause", "error_cause_mix"}
    _exact_keys(errors, error_keys, "ProgressState.errors", "invalid_domain_state")
    for key in ("error_count", "classified_error_count", "unclassified_error_count"):
        _count(errors.get(key), f"ProgressState.errors.{key}")
    causes = {"knowledge_gap", "reading_error", "calculation_error", "scoring_point_expression"}
    for key in ("error_count_by_cause", "error_cause_mix"):
        values = _object(errors.get(key), f"ProgressState.errors.{key}", "invalid_domain_state")
        _exact_keys(values, causes, f"ProgressState.errors.{key}", "invalid_domain_state")
        for cause, value in values.items():
            if key == "error_count_by_cause":
                _count(value, f"ProgressState.errors.{key}.{cause}")
            else:
                _ratio(value, f"ProgressState.errors.{key}.{cause}")

    coverage = _object(state.get("coverage"), "ProgressState.coverage", "invalid_domain_state")
    _exact_keys(coverage, {"l1", "l2", "l3"}, "ProgressState.coverage", "invalid_domain_state")
    for level, value in coverage.items():
        metric = _object(value, f"ProgressState.coverage.{level}", "invalid_domain_state")
        _exact_keys(metric, {"covered", "total", "ratio"}, f"ProgressState.coverage.{level}", "invalid_domain_state")
        _count(metric.get("covered"), f"ProgressState.coverage.{level}.covered")
        _count(metric.get("total"), f"ProgressState.coverage.{level}.total")
        _ratio(metric.get("ratio"), f"ProgressState.coverage.{level}.ratio")

    study = _object(state.get("study"), "ProgressState.study", "invalid_domain_state")
    _exact_keys(study, {"session_count", "study_minutes"}, "ProgressState.study", "invalid_domain_state")
    _count(study.get("session_count"), "ProgressState.study.session_count")
    _count(study.get("study_minutes"), "ProgressState.study.study_minutes")
    return state


def _validate_user_configuration(value: Any) -> Mapping[str, Any]:
    config = _object(value, "UserConfiguration", "invalid_user_configuration")
    _exact_keys(config, {"schema_version", "timezone", "daily_available_minutes", "study_days"}, "UserConfiguration", "invalid_user_configuration")
    if config.get("schema_version") != USER_CONFIGURATION_SCHEMA_VERSION:
        _fail("UserConfiguration has an unsupported schema_version", "invalid_schema_version")
    _validate_timezone(config.get("timezone"), "UserConfiguration.timezone")
    minutes = config.get("daily_available_minutes")
    if type(minutes) is not int or not 0 <= minutes <= 1440:
        _fail("UserConfiguration.daily_available_minutes must be an integer in 0..1440 minutes", "invalid_user_configuration")
    days = config.get("study_days")
    if not isinstance(days, list) or any(type(day) is not int or day < 1 or day > 7 for day in days):
        _fail("UserConfiguration.study_days must be an ISO weekday array with values 1..7", "invalid_user_configuration")
    if len(days) != len(set(days)):
        _fail("UserConfiguration.study_days must not contain duplicates", "invalid_user_configuration")
    return config


def _validate_review_item(
    item_id: Any,
    item_value: Any,
    topic_ids: set[str],
    capability_ids: set[str],
    state_schema: Mapping[str, Any],
) -> None:
    item_key = _nonempty_string(item_id, "MasteryReviewState.items key", "unknown_review_item")
    item = _object(item_value, f"MasteryReviewState.items[{item_key}]", "invalid_domain_state")
    item_schema = _object(state_schema.get("$defs", {}).get("itemState"), "MasteryReviewState item schema", "invalid_contract_schema")
    item_keys = set(item_schema.get("required", []))
    _exact_keys(item, item_keys, f"MasteryReviewState.items[{item_key}]", "invalid_domain_state")
    item_properties = _object(item_schema.get("properties"), "MasteryReviewState item properties", "invalid_contract_schema")
    kind = item.get("item_kind")
    canonical = _object(item.get("canonical_ref"), f"{item_key}.canonical_ref", "invalid_domain_state")
    if kind == "topic":
        _exact_keys(canonical, {"topic_id", "taxonomy_version"}, f"{item_key}.canonical_ref", "invalid_domain_state")
        topic_id = _nonempty_string(canonical.get("topic_id"), f"{item_key}.canonical_ref.topic_id", "unknown_topic_id")
        if topic_id not in topic_ids:
            _fail(f"{item_key}: unknown topic target {topic_id!r}", "unknown_topic_id")
        if canonical.get("taxonomy_version") != TAXONOMY_VERSION:
            _fail(f"{item_key}: topic target taxonomy version mismatch", "invalid_catalog_version")
        expected_id = f"review/topic/{topic_id}"
    elif kind == "case_capability":
        _exact_keys(canonical, {"capability_id", "taxonomy_version"}, f"{item_key}.canonical_ref", "invalid_domain_state")
        capability_id = _nonempty_string(canonical.get("capability_id"), f"{item_key}.canonical_ref.capability_id", "unknown_capability_id")
        if capability_id not in capability_ids:
            _fail(f"{item_key}: unknown capability target {capability_id!r}", "unknown_capability_id")
        if canonical.get("taxonomy_version") != CAPABILITY_VERSION:
            _fail(f"{item_key}: capability target version mismatch", "invalid_catalog_version")
        expected_id = f"review/case_capability/{capability_id}"
    elif kind == "question":
        _exact_keys(canonical, {"source_id", "source_question_id"}, f"{item_key}.canonical_ref", "invalid_domain_state")
        source_id = _nonempty_string(canonical.get("source_id"), f"{item_key}.canonical_ref.source_id", "unknown_review_item")
        question_id = _nonempty_string(canonical.get("source_question_id"), f"{item_key}.canonical_ref.source_question_id", "unknown_review_item")
        expected_id = f"review/question/{source_id}/{question_id}"
    else:
        _fail(f"{item_key}: unsupported item_kind {kind!r}", "unknown_item_kind")
    if item.get("review_item_id") != item_key or item_key != expected_id:
        _fail(f"{item_key}: review target does not match its stable canonical identity", "unknown_review_item")

    source = _object(item.get("source_reference"), f"{item_key}.source_reference", "invalid_domain_state")
    source_keys = {"source_id", "source_commit", "source_path", "source_question_id", "golden_set_record_id", "source_value"}
    _require({"source_id", "source_commit", "source_path"} <= set(source) and set(source) <= source_keys, f"{item_key}: malformed source_reference", "invalid_domain_state")
    _nonempty_string(source.get("source_id"), f"{item_key}.source_reference.source_id", "invalid_domain_state")
    commit = _nonempty_string(source.get("source_commit"), f"{item_key}.source_reference.source_commit", "invalid_domain_state")
    _require(re.fullmatch(r"[0-9a-f]{40}", commit) is not None, f"{item_key}: invalid source commit", "invalid_domain_state")
    source_path = _nonempty_string(source.get("source_path"), f"{item_key}.source_reference.source_path", "invalid_domain_state")
    _require(not source_path.startswith("/") and chr(92) not in source_path and ".." not in source_path.split("/"), f"{item_key}: invalid source path", "invalid_domain_state")
    if "source_question_id" in source:
        _nonempty_string(source["source_question_id"], f"{item_key}.source_reference.source_question_id", "invalid_domain_state")
    if "source_value" in source:
        _nonempty_string(source["source_value"], f"{item_key}.source_reference.source_value", "invalid_domain_state")
    if kind == "question" and (source.get("source_id") != canonical.get("source_id") or source.get("source_question_id") != canonical.get("source_question_id")):
        _fail(f"{item_key}: question target source reference mismatch", "unknown_review_item")

    for key in ("item_kind", "mastery_state", "review_status", "mastery_reason", "review_status_reason", "scheduling_reason"):
        enum_values = item_properties.get(key, {}).get("enum")
        if not isinstance(enum_values, list) or item.get(key) not in enum_values:
            category = "unknown_item_kind" if key == "item_kind" else "invalid_domain_state"
            _fail(f"{item_key}: unsupported {key}", category)
    for key in ("evaluated_evidence_count", "successful_review_count", "failure_count", "insufficient_evidence_count", "consecutive_success_count", "consecutive_success_day_count"):
        _count(item.get(key), f"{item_key}.{key}")
    if item.get("last_review_at") is not None:
        _parse_instant(item["last_review_at"], f"{item_key}.last_review_at")
    if item.get("next_due_at") is not None:
        _parse_instant(item["next_due_at"], f"{item_key}.next_due_at")
    if item.get("next_due_local_date") is not None:
        local_date = item["next_due_local_date"]
        try:
            parsed_date = date.fromisoformat(local_date) if isinstance(local_date, str) else None
        except ValueError as exc:
            raise PlannerContractError(f"{item_key}.next_due_local_date: invalid date", "invalid_domain_state") from exc
        _require(parsed_date is not None and parsed_date.isoformat() == local_date, f"{item_key}.next_due_local_date: expected YYYY-MM-DD", "invalid_domain_state")
    interval = item.get("review_interval_days")
    _require(interval is None or type(interval) is int and interval >= 1, f"{item_key}.review_interval_days: expected positive integer or null", "invalid_domain_state")
    last_evidence_id = item.get("last_evidence_id")
    _require(last_evidence_id is None or isinstance(last_evidence_id, str) and bool(last_evidence_id), f"{item_key}.last_evidence_id: expected non-empty string or null", "invalid_domain_state")
    evidence = item.get("evidence")
    evidence_ids = item.get("evidence_ids")
    if not isinstance(evidence, list) or not isinstance(evidence_ids, list):
        _fail(f"{item_key}: evidence and evidence_ids must be arrays", "invalid_domain_state")
    seen: set[str] = set()
    evidence_schema = _object(state_schema.get("$defs", {}).get("evidenceTrace"), "MasteryReviewState evidence schema", "invalid_contract_schema")
    evidence_keys = set(evidence_schema.get("required", []))
    evidence_properties = _object(evidence_schema.get("properties"), "MasteryReviewState evidence properties", "invalid_contract_schema")
    for index, record_value in enumerate(evidence):
        record = _object(record_value, f"{item_key}.evidence[{index}]", "invalid_domain_state")
        _exact_keys(record, evidence_keys, f"{item_key}.evidence[{index}]", "invalid_domain_state")
        evidence_id = _nonempty_string(record.get("evidence_id"), f"{item_key}.evidence[{index}].evidence_id", "invalid_domain_state")
        _parse_instant(record.get("occurred_at"), f"{item_key}.evidence[{index}].occurred_at")
        _nonempty_string(record.get("source_event_id"), f"{item_key}.evidence[{index}].source_event_id", "invalid_domain_state")
        _nonempty_string(record.get("review_event_id"), f"{item_key}.evidence[{index}].review_event_id", "invalid_domain_state")
        for key in ("attempt_context", "evidence_kind", "evidence_status", "policy_outcome", "policy_outcome_reason"):
            enum_values = evidence_properties.get(key, {}).get("enum")
            if not isinstance(enum_values, list) or record.get(key) not in enum_values:
                _fail(f"{item_key}.evidence[{index}]: unsupported {key}", "invalid_domain_state")
        if evidence_id in seen:
            _fail(f"{item_key}: duplicate evidence id", "invalid_domain_state")
        seen.add(evidence_id)
    if any(not isinstance(value, str) for value in evidence_ids) or set(evidence_ids) != seen or len(evidence_ids) != len(seen):
        _fail(f"{item_key}: evidence_ids do not match evidence records", "invalid_domain_state")


def _validate_mastery_review_state(
    value: Any,
    progress_state: Mapping[str, Any],
    root: Path,
    topic_ids: set[str],
    capability_ids: set[str],
    as_of: datetime,
    timezone_name: str,
) -> Mapping[str, Any]:
    state = _object(value, "MasteryReviewState", "invalid_domain_state")
    review_state_schema = load_json(root / "data/review/mastery-review-state.schema.json")
    required = set(review_state_schema.get("required", []))
    _exact_keys(state, required, "MasteryReviewState", "invalid_domain_state")
    schema_versions = {
        "schema_version": MASTERY_REVIEW_STATE_SCHEMA_VERSION,
        "review_model_version": "review-model/v0.1",
        "review_event_schema_version": "review-event/v0.1",
        "review_evidence_version": "review-evidence/v0.1",
        "progress_event_schema_version": PROGRESS_EVENT_SCHEMA_VERSION,
        "policy_projection_schema_version": "review-policy-projection/v0.1",
    }
    for key, expected in schema_versions.items():
        if state.get(key) != expected:
            _fail(f"MasteryReviewState.{key}: unsupported version", "invalid_schema_version")
    if state.get("progress_replay_version") != progress_state.get("replay_rule_version") or state.get("progress_event_schema_version") != progress_state.get("event_schema_version"):
        _fail("MasteryReviewState and ProgressState replay/event versions disagree", "inconsistent_input")
    if state.get("mastery_policy_version") != "mastery-policy/spaced-consecutive/v0.1" or state.get("review_policy_version") != "review-policy/simple-ladder/v0.1":
        _fail("MasteryReviewState has an unsupported policy identity/version", "invalid_policy_input")
    _count(state.get("progress_replayed_event_count"), "MasteryReviewState.progress_replayed_event_count")
    if state["progress_replayed_event_count"] != progress_state["replayed_event_count"]:
        _fail("MasteryReviewState and ProgressState event counts disagree", "inconsistent_input")
    _nonempty_string(state.get("tzdata_version"), "MasteryReviewState.tzdata_version", "invalid_domain_state")
    state_as_of = _parse_instant(state.get("as_of"), "MasteryReviewState.as_of")
    if state_as_of != as_of:
        _fail("MasteryReviewState.as_of must equal Planner as_of as an instant", "inconsistent_input")
    for key in ("timezone", "schedule_timezone"):
        _validate_timezone(state.get(key), f"MasteryReviewState.{key}")
        if state[key] != timezone_name:
            _fail(f"MasteryReviewState.{key} must equal snapshot timezone", "inconsistent_input")

    policy = _object(state.get("policy"), "MasteryReviewState.policy", "invalid_domain_state")
    expected_policy = _constant_object_from_schema(review_state_schema["$defs"]["policy"], "MasteryReviewState.policy")
    if dict(policy) != expected_policy:
        _fail("MasteryReviewState.policy differs from the frozen Phase 4 schema", "invalid_policy_input")
    adapter = _object(state.get("outcome_adapter"), "MasteryReviewState.outcome_adapter", "invalid_domain_state")
    expected_adapter = _constant_object_from_schema(review_state_schema["$defs"]["outcomeAdapter"], "MasteryReviewState.outcome_adapter")
    if dict(adapter) != expected_adapter:
        _fail("MasteryReviewState outcome adapter differs from the frozen Phase 4 schema", "invalid_policy_input")

    items = _object(state.get("items"), "MasteryReviewState.items", "invalid_domain_state")
    order = state.get("item_order")
    if not isinstance(order, list) or any(not isinstance(item_id, str) or not item_id for item_id in order) or len(order) != len(set(order)):
        _fail("MasteryReviewState.item_order must be a unique list of review targets", "unknown_review_item")
    item_ids = set(items)
    if set(order) != item_ids:
        _fail("MasteryReviewState.item_order targets do not exactly match items", "unknown_review_item")
    for item_id, item in items.items():
        _validate_review_item(item_id, item, topic_ids, capability_ids, review_state_schema)

    # Validate only the upstream aggregate shape, not its derived values.
    # The Planner deliberately does not recalculate mastery, due, overdue, or intervals.
    aggregate_keys = {
        "review": set(review_state_schema.get("$defs", {}).get("reviewAggregate", {}).get("required", [])),
        "mastery": set(review_state_schema.get("$defs", {}).get("masteryAggregate", {}).get("required", [])),
    }
    for aggregate_name, keys in aggregate_keys.items():
        aggregate = _object(state.get(aggregate_name), f"MasteryReviewState.{aggregate_name}", "invalid_domain_state")
        _exact_keys(aggregate, keys, f"MasteryReviewState.{aggregate_name}", "invalid_domain_state")
        for key, count in aggregate.items():
            _count(count, f"MasteryReviewState.{aggregate_name}.{key}")
    return state


def validate_snapshot(snapshot_value: Any, root: Path = ROOT) -> dict[str, Any]:
    """Validate one complete snapshot and return its canonical representation."""
    validate_contract_schemas(root)
    catalogs, supported_topic_ids, supported_capability_ids = _load_supported_catalogs(root)
    snapshot = _object(snapshot_value, "Planner Input Snapshot")
    _exact_keys(snapshot, {"schema_version", "as_of", "timezone", "planner_policy", "inputs"}, "Planner Input Snapshot")
    if snapshot.get("schema_version") != SNAPSHOT_SCHEMA_VERSION:
        _fail("unsupported Planner Input Snapshot schema_version", "invalid_schema_version")
    as_of = _parse_instant(snapshot.get("as_of"), "Planner as_of")
    timezone_name = _validate_timezone(snapshot.get("timezone"), "Planner timezone")

    policy = _object(snapshot.get("planner_policy"), "planner_policy", "invalid_policy_input")
    _exact_keys(policy, {"policy_id", "policy_version"}, "planner_policy", "invalid_policy_input")
    if policy.get("policy_id") != PLANNER_POLICY_ID or policy.get("policy_version") != PLANNER_POLICY_VERSION:
        _fail("unsupported planner policy identity/version", "invalid_policy_input")

    inputs = _object(snapshot.get("inputs"), "inputs")
    input_keys = {"progress_state", "mastery_review_state", "taxonomy", "capabilities", "user_configuration"}
    _exact_keys(inputs, input_keys, "inputs")
    _validate_catalog_manifest(
        inputs.get("taxonomy"), label="inputs.taxonomy", version_key="taxonomy_version", ids_key="topic_ids",
        expected_version=TAXONOMY_VERSION, supported_ids=supported_topic_ids,
    )
    _validate_catalog_manifest(
        inputs.get("capabilities"), label="inputs.capabilities", version_key="taxonomy_version", ids_key="capability_ids",
        expected_version=CAPABILITY_VERSION, supported_ids=supported_capability_ids,
    )
    _require(catalogs["taxonomy"].get("taxonomy_version") == catalogs["capabilities"].get("taxonomy_version"), "repository catalog versions disagree", "invalid_catalog_version")

    config = _validate_user_configuration(inputs.get("user_configuration"))
    if config["timezone"] != timezone_name:
        _fail("snapshot timezone must match UserConfiguration.timezone", "inconsistent_input")
    progress_state = _validate_progress_state(
        inputs.get("progress_state"), supported_topic_ids, supported_capability_ids,
        TAXONOMY_VERSION, CAPABILITY_VERSION,
    )
    _validate_mastery_review_state(
        inputs.get("mastery_review_state"), progress_state, root, supported_topic_ids, supported_capability_ids,
        as_of, timezone_name,
    )

    normalized = copy.deepcopy(dict(snapshot))
    normalized["as_of"] = _canonical_instant(snapshot["as_of"])
    normalized_inputs = normalized["inputs"]
    normalized_inputs["taxonomy"]["topic_ids"] = sorted(normalized_inputs["taxonomy"]["topic_ids"])
    normalized_inputs["capabilities"]["capability_ids"] = sorted(normalized_inputs["capabilities"]["capability_ids"])
    normalized_inputs["user_configuration"]["study_days"] = sorted(normalized_inputs["user_configuration"]["study_days"])

    normalized_review = normalized_inputs["mastery_review_state"]
    normalized_review["as_of"] = _canonical_instant(normalized_review["as_of"])
    normalized_review["item_order"] = sorted(normalized_review["item_order"])
    for item in normalized_review["items"].values():
        for timestamp_key in ("last_review_at", "next_due_at"):
            if item[timestamp_key] is not None:
                item[timestamp_key] = _canonical_instant(item[timestamp_key])
        records = item["evidence"]
        for record in records:
            record["occurred_at"] = _canonical_instant(record["occurred_at"])
        records.sort(key=lambda record: (_parse_instant(record["occurred_at"], "evidence.occurred_at"), record["evidence_id"]))
        item["evidence_ids"] = [record["evidence_id"] for record in records]
    # Mapping insertion order is not semantic; JSON serialization sorts keys.
    return normalized


def canonical_json(snapshot: Any, root: Path = ROOT) -> str:
    canonical = validate_snapshot(snapshot, root)
    return json.dumps(canonical, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _output_date(value: Any, label: str) -> date:
    if not isinstance(value, str):
        _fail(f"{label}: expected an ISO local date", "invalid_plan_day")
    try:
        parsed = date.fromisoformat(value)
    except ValueError as exc:
        raise PlannerContractError(f"{label}: invalid ISO local date", "invalid_plan_day") from exc
    if parsed.isoformat() != value:
        _fail(f"{label}: expected canonical YYYY-MM-DD", "invalid_plan_day")
    return parsed


def _output_minutes(value: Any, label: str) -> int:
    if type(value) is not int or not 0 <= value <= 1440:
        _fail(f"{label}: expected integer minutes in 0..1440", "invalid_minutes")
    return value


def _resolve_input_pointer(document: Any, pointer: Any, label: str) -> Any:
    if not isinstance(pointer, str) or not pointer.startswith("/") or re.search(r"~(?![01])", pointer):
        _fail(f"{label}: expected a valid JSON Pointer into Planner input", "invalid_explain_trace")
    current = document
    for raw_part in pointer[1:].split("/"):
        part = raw_part.replace("~1", "/").replace("~0", "~")
        if isinstance(current, Mapping) and part in current:
            current = current[part]
        elif isinstance(current, list) and part.isdigit() and int(part) < len(current):
            current = current[int(part)]
        else:
            _fail(f"{label}: JSON Pointer does not resolve in Planner input", "invalid_explain_trace")
    return current


def _validate_output_target(
    target_kind: Any,
    target_ref: Any,
    review_item_ids: set[str],
    topic_ids: set[str],
    label: str,
) -> tuple[str, str]:
    if not isinstance(target_kind, str) or target_kind not in SUPPORTED_TARGET_KINDS:
        _fail(f"{label}.target_kind: unsupported target kind {target_kind!r}", "unsupported_target_kind")
    reference = _nonempty_string(target_ref, f"{label}.target_ref", "invalid_target_ref")
    if target_kind == "review_item":
        if REVIEW_ITEM_ID_PATTERN.fullmatch(reference) is None:
            _fail(f"{label}.target_ref: malformed Review Item identity", "invalid_target_ref")
        if reference not in review_item_ids:
            _fail(f"{label}.target_ref: unknown Review Item identity {reference!r}", "unknown_review_item")
    else:
        if TOPIC_ID_PATTERN.fullmatch(reference) is None:
            _fail(f"{label}.target_ref: malformed canonical topic ID", "invalid_target_ref")
        if reference not in topic_ids:
            _fail(f"{label}.target_ref: unknown topic ID {reference!r}", "unknown_topic_id")
    return str(target_kind), reference


def validate_planner_output(
    output_value: Any,
    input_snapshot_value: Any,
    root: Path = ROOT,
) -> dict[str, Any]:
    """Validate one output projection against its explicit, self-contained input."""
    validate_contract_schemas(root)
    input_snapshot = validate_snapshot(input_snapshot_value, root)
    output = _object(output_value, "PlannerOutput", "invalid_planner_output")
    required_output_keys = {
        "schema_version", "planner_policy", "input_snapshot_schema_version", "as_of", "timezone",
        "generated_for_local_date", "horizon", "days", "explain_traces",
    }
    _exact_keys(output, required_output_keys, "PlannerOutput", "invalid_planner_output")
    if output.get("schema_version") != PLANNER_OUTPUT_SCHEMA_VERSION:
        _fail("unsupported PlannerOutput schema_version", "invalid_schema_version")
    if output.get("input_snapshot_schema_version") != input_snapshot["schema_version"]:
        _fail("PlannerOutput input snapshot schema version mismatch", "inconsistent_input")

    policy = _object(output.get("planner_policy"), "PlannerOutput.planner_policy", "invalid_policy_input")
    _exact_keys(policy, {"policy_id", "policy_version"}, "PlannerOutput.planner_policy", "invalid_policy_input")
    _nonempty_string(policy.get("policy_id"), "PlannerOutput.planner_policy.policy_id", "invalid_policy_input")
    _nonempty_string(policy.get("policy_version"), "PlannerOutput.planner_policy.policy_version", "invalid_policy_input")

    as_of = _parse_instant(output.get("as_of"), "PlannerOutput.as_of")
    if output["as_of"] != _canonical_instant(output["as_of"]):
        _fail("PlannerOutput.as_of must use canonical UTC Z form", "invalid_timestamp")
    if as_of != _parse_instant(input_snapshot["as_of"], "PlannerInput.as_of"):
        _fail("PlannerOutput.as_of must match the input snapshot instant", "inconsistent_input")
    timezone_name = _validate_timezone(output.get("timezone"), "PlannerOutput.timezone")
    if timezone_name != input_snapshot["timezone"]:
        _fail("PlannerOutput.timezone must match the input snapshot", "inconsistent_input")
    generated_for_date = _output_date(output.get("generated_for_local_date"), "PlannerOutput.generated_for_local_date")
    expected_local_date = as_of.astimezone(resolve_timezone(timezone_name)).date()
    if generated_for_date != expected_local_date:
        _fail("generated_for_local_date must be the local date of as_of", "invalid_horizon")

    horizon = _object(output.get("horizon"), "PlannerOutput.horizon", "invalid_horizon")
    _exact_keys(horizon, {"unit", "day_count"}, "PlannerOutput.horizon", "invalid_horizon")
    if horizon.get("unit") != PLANNER_OUTPUT_HORIZON_UNIT or horizon.get("day_count") != PLANNER_OUTPUT_HORIZON_DAYS:
        _fail("PlannerOutput horizon must be seven local calendar days", "invalid_horizon")
    days = output.get("days")
    if not isinstance(days, list) or len(days) != PLANNER_OUTPUT_HORIZON_DAYS:
        _fail("PlannerOutput.days must contain exactly seven PlanDay values", "invalid_horizon")

    inputs = input_snapshot["inputs"]
    review_item_ids = set(inputs["mastery_review_state"]["items"])
    topic_ids = set(inputs["taxonomy"]["topic_ids"])
    study_days = set(inputs["user_configuration"]["study_days"])
    task_ids: set[str] = set()
    demand_ids: set[str] = set()
    task_links: list[tuple[str, str, str, str, str]] = []
    demand_links: list[tuple[str, str, str, str, str]] = []

    for offset, day_value in enumerate(days):
        day = _object(day_value, f"PlannerOutput.days[{offset}]", "invalid_plan_day")
        _exact_keys(day, {
            "day_offset", "local_date", "study_day", "capacity_minutes", "planned_minutes",
            "remaining_minutes", "tasks", "unmet_demand",
        }, f"PlannerOutput.days[{offset}]", "invalid_plan_day")
        if type(day.get("day_offset")) is not int or day["day_offset"] != offset:
            _fail(f"PlanDay[{offset}].day_offset must equal its array index", "invalid_horizon")
        local_date = _output_date(day.get("local_date"), f"PlanDay[{offset}].local_date")
        if local_date != generated_for_date + timedelta(days=offset):
            _fail(f"PlanDay[{offset}].local_date is not a consecutive local calendar date", "invalid_horizon")
        if type(day.get("study_day")) is not bool or day["study_day"] != (local_date.isoweekday() in study_days):
            _fail(f"PlanDay[{offset}].study_day does not match UserConfiguration.study_days", "invalid_plan_day")
        capacity = _output_minutes(day.get("capacity_minutes"), f"PlanDay[{offset}].capacity_minutes")
        planned = _output_minutes(day.get("planned_minutes"), f"PlanDay[{offset}].planned_minutes")
        remaining = _output_minutes(day.get("remaining_minutes"), f"PlanDay[{offset}].remaining_minutes")
        tasks = day.get("tasks")
        demands = day.get("unmet_demand")
        if not isinstance(tasks, list):
            _fail(f"PlanDay[{offset}].tasks must be an array", "invalid_plan_day")
        if not isinstance(demands, list):
            _fail(f"PlanDay[{offset}].unmet_demand must be an array", "invalid_plan_day")

        task_minutes = 0
        scheduled_targets: set[tuple[str, str]] = set()
        for task_index, task_value in enumerate(tasks):
            label = f"PlanDay[{offset}].tasks[{task_index}]"
            task = _object(task_value, label, "invalid_plan_task")
            _exact_keys(task, {
                "task_id", "task_type", "target_kind", "target_ref", "planned_minutes", "explain_trace_id",
            }, label, "invalid_plan_task")
            task_id = _nonempty_string(task.get("task_id"), f"{label}.task_id", "invalid_plan_task")
            if task_id in task_ids:
                _fail(f"duplicate task_id {task_id!r}", "duplicate_task_id")
            task_ids.add(task_id)
            if not isinstance(task.get("task_type"), str) or task["task_type"] not in SUPPORTED_PLAN_TASK_TYPES:
                _fail(f"{label}.task_type is unsupported", "unsupported_task_type")
            target_kind, target_ref = _validate_output_target(task.get("target_kind"), task.get("target_ref"), review_item_ids, topic_ids, label)
            expected_target_kind = "review_item" if task["task_type"] == "review" else "topic"
            if target_kind != expected_target_kind:
                _fail(f"{label}: task_type {task['task_type']!r} requires target_kind {expected_target_kind!r}", "unsupported_target_kind")
            target_key = (target_kind, target_ref)
            if target_key in scheduled_targets:
                _fail(f"{label}: duplicate scheduled target in one day", "invalid_plan_task")
            scheduled_targets.add(target_key)
            minutes = _output_minutes(task.get("planned_minutes"), f"{label}.planned_minutes")
            task_minutes += minutes
            explain_id = _nonempty_string(task.get("explain_trace_id"), f"{label}.explain_trace_id", "invalid_explain_trace")
            task_links.append(("plan_task", task_id, explain_id, target_kind, target_ref))

        unmet_targets: set[tuple[str, str]] = set()
        for demand_index, demand_value in enumerate(demands):
            label = f"PlanDay[{offset}].unmet_demand[{demand_index}]"
            demand = _object(demand_value, label, "invalid_unmet_demand")
            _exact_keys(demand, {
                "demand_id", "demand_type", "target_kind", "target_ref", "requested_minutes", "explain_trace_id",
            }, label, "invalid_unmet_demand")
            demand_id = _nonempty_string(demand.get("demand_id"), f"{label}.demand_id", "invalid_unmet_demand")
            if demand_id in demand_ids:
                _fail(f"duplicate demand_id {demand_id!r}", "duplicate_unmet_demand")
            demand_ids.add(demand_id)
            if not isinstance(demand.get("demand_type"), str) or demand["demand_type"] not in SUPPORTED_DEMAND_TYPES:
                _fail(f"{label}.demand_type is unsupported", "unsupported_demand_type")
            target_kind, target_ref = _validate_output_target(demand.get("target_kind"), demand.get("target_ref"), review_item_ids, topic_ids, label)
            expected_target_kind = "review_item" if demand["demand_type"] == "review" else "topic"
            if target_kind != expected_target_kind:
                _fail(f"{label}: demand_type {demand['demand_type']!r} requires target_kind {expected_target_kind!r}", "unsupported_target_kind")
            target_key = (target_kind, target_ref)
            if target_key in unmet_targets or target_key in scheduled_targets:
                _fail(f"{label}: demand cannot be both scheduled and unmet for the same day", "invalid_unmet_demand")
            unmet_targets.add(target_key)
            _output_minutes(demand.get("requested_minutes"), f"{label}.requested_minutes")
            explain_id = _nonempty_string(demand.get("explain_trace_id"), f"{label}.explain_trace_id", "invalid_explain_trace")
            demand_links.append(("unmet_demand", demand_id, explain_id, target_kind, target_ref))

        if planned > capacity or remaining != capacity - planned or task_minutes != planned:
            _fail(f"PlanDay[{offset}] violates capacity or task-minute invariants", "capacity_invariant")
        if capacity == 0 and tasks:
            _fail(f"PlanDay[{offset}] with zero capacity cannot contain tasks", "capacity_invariant")

    traces_value = output.get("explain_traces")
    if not isinstance(traces_value, list):
        _fail("PlannerOutput.explain_traces must be an array", "invalid_explain_trace")
    traces: dict[str, Mapping[str, Any]] = {}
    for index, trace_value in enumerate(traces_value):
        label = f"PlannerOutput.explain_traces[{index}]"
        trace = _object(trace_value, label, "invalid_explain_trace")
        allowed = {
            "trace_id", "subject_kind", "subject_id", "decision_category", "reason_code", "planner_policy",
            "input_references", "target_kind", "target_ref", "structured_inputs", "display_message",
        }
        required = allowed - {"display_message"}
        _require(required <= set(trace), f"{label}: required structured fields are missing", "invalid_explain_trace")
        _exact_keys(trace, allowed if "display_message" in trace else required, label, "invalid_explain_trace")
        trace_id = _nonempty_string(trace.get("trace_id"), f"{label}.trace_id", "invalid_explain_trace")
        if trace_id in traces:
            _fail(f"duplicate Explain trace_id {trace_id!r}", "duplicate_explain_trace")
        subject_kind = trace.get("subject_kind")
        if not isinstance(subject_kind, str) or subject_kind not in {"plan_task", "unmet_demand"}:
            _fail(f"{label}.subject_kind is unsupported", "invalid_explain_trace")
        _nonempty_string(trace.get("subject_id"), f"{label}.subject_id", "invalid_explain_trace")
        if not isinstance(trace.get("decision_category"), str) or trace["decision_category"] not in {"task_scheduled", "demand_unmet"}:
            _fail(f"{label}.decision_category is unsupported", "invalid_explain_trace")
        reason_code = trace.get("reason_code")
        if not isinstance(reason_code, str) or REASON_CODE_PATTERN.fullmatch(reason_code) is None:
            _fail(f"{label}.reason_code must be a machine-readable string", "invalid_explain_trace")
        trace_policy = _object(trace.get("planner_policy"), f"{label}.planner_policy", "invalid_explain_trace")
        _exact_keys(trace_policy, {"policy_id", "policy_version"}, f"{label}.planner_policy", "invalid_explain_trace")
        if dict(trace_policy) != dict(policy):
            _fail(f"{label}.planner_policy does not match PlannerOutput policy", "invalid_explain_trace")
        input_references = trace.get("input_references")
        if not isinstance(input_references, list) or not input_references:
            _fail(f"{label}.input_references must contain JSON Pointers", "invalid_explain_trace")
        for ref_index, pointer in enumerate(input_references):
            _resolve_input_pointer(input_snapshot, pointer, f"{label}.input_references[{ref_index}]")
        target_kind, target_ref = _validate_output_target(trace.get("target_kind"), trace.get("target_ref"), review_item_ids, topic_ids, label)
        if not isinstance(trace.get("structured_inputs"), Mapping):
            _fail(f"{label}.structured_inputs must be an object", "invalid_explain_trace")
        if "display_message" in trace:
            _nonempty_string(trace["display_message"], f"{label}.display_message", "invalid_explain_trace")
        traces[trace_id] = trace

    expected_trace_refs: set[str] = set()
    links = task_links + demand_links
    for subject_kind, subject_id, trace_id, target_kind, target_ref in links:
        if trace_id in expected_trace_refs:
            _fail(f"Explain trace {trace_id!r} is referenced more than once", "invalid_explain_trace")
        expected_trace_refs.add(trace_id)
        trace = traces.get(trace_id)
        if trace is None:
            _fail(f"missing Explain trace {trace_id!r}", "invalid_explain_trace")
        expected_category = "task_scheduled" if subject_kind == "plan_task" else "demand_unmet"
        if (
            trace.get("subject_kind") != subject_kind
            or trace.get("subject_id") != subject_id
            or trace.get("decision_category") != expected_category
            or trace.get("target_kind") != target_kind
            or trace.get("target_ref") != target_ref
        ):
            _fail(f"Explain trace {trace_id!r} does not match its task/demand subject", "invalid_explain_trace")
    if set(traces) != expected_trace_refs:
        _fail("PlannerOutput contains orphan Explain traces", "invalid_explain_trace")
    return copy.deepcopy(dict(output))


def validate_output_fixture_set(root: Path = ROOT) -> dict[str, Any]:
    """Validate synthetic output contract fixtures; never generates a plan."""
    fixture_dir = root / "data/planner/output-fixtures"
    fixture_paths = sorted(fixture_dir.glob("*.json"))
    _require(bool(fixture_paths), "planner output contract fixtures are missing", "invalid_fixture")
    base_input, _ = build_minimal_output(root)
    fixture_ids: set[str] = set()
    accepted = 0
    rejected = 0
    rejection_categories: dict[str, int] = {}
    for path in fixture_paths:
        fixture = load_json(path)
        _require(isinstance(fixture, dict), f"{path.name}: fixture must be an object", "invalid_fixture")
        _exact_keys(fixture, {"fixture_id", "description", "input_patches", "output_patches", "expected_error"}, path.name, "invalid_fixture")
        fixture_id = _nonempty_string(fixture.get("fixture_id"), f"{path.name}.fixture_id", "invalid_fixture")
        _require(fixture_id not in fixture_ids, f"duplicate output fixture_id {fixture_id}", "invalid_fixture")
        fixture_ids.add(fixture_id)
        input_patches = fixture.get("input_patches")
        output_patches = fixture.get("output_patches")
        _require(isinstance(input_patches, list) and isinstance(output_patches, list), f"{path.name}: patches must be arrays", "invalid_fixture")
        expected_error = fixture.get("expected_error")
        _require(expected_error is None or isinstance(expected_error, str) and bool(expected_error), f"{path.name}: expected_error must be null or a category", "invalid_fixture")
        candidate_input = copy.deepcopy(base_input)
        try:
            for index, patch in enumerate(input_patches):
                apply_output_fixture_patch(candidate_input, _object(patch, f"{path.name}.input_patches[{index}]", "invalid_fixture"), f"{path.name}.input_patches[{index}]")
            _, candidate_output = build_minimal_output(root, candidate_input)
            for index, patch in enumerate(output_patches):
                apply_output_fixture_patch(candidate_output, _object(patch, f"{path.name}.output_patches[{index}]", "invalid_fixture"), f"{path.name}.output_patches[{index}]")
            validate_planner_output(candidate_output, candidate_input, root)
        except (PlannerContractError, ValueError) as exc:
            category = exc.category if isinstance(exc, PlannerContractError) else "invalid_fixture"
            if expected_error is None:
                _fail(f"{path.name}: unexpected rejection [{category}]: {exc}", "invalid_fixture")
            _require(category == expected_error, f"{path.name}: expected {expected_error}, got {category}: {exc}", "invalid_fixture")
            rejected += 1
            rejection_categories[category] = rejection_categories.get(category, 0) + 1
        else:
            _require(expected_error is None, f"{path.name}: expected rejection [{expected_error}] but output was accepted", "invalid_fixture")
            accepted += 1
    return {
        "fixtures": len(fixture_paths),
        "accepted": accepted,
        "rejected": rejected,
        "rejection_categories": rejection_categories,
    }


def _apply_patch(snapshot: dict[str, Any], patch: Mapping[str, Any], label: str) -> None:
    operation = patch.get("op")
    path = patch.get("path")
    if operation not in {"replace", "remove"} or not isinstance(path, list) or not path or any(not isinstance(part, str) for part in path):
        _fail(f"{label}: malformed patch", "invalid_fixture")
    parent: Any = snapshot
    for part in path[:-1]:
        if not isinstance(parent, dict) or part not in parent:
            _fail(f"{label}: patch path does not exist", "invalid_fixture")
        parent = parent[part]
    final = path[-1]
    if not isinstance(parent, dict) or final not in parent:
        _fail(f"{label}: patch target does not exist", "invalid_fixture")
    if operation == "remove":
        del parent[final]
    else:
        if "value" not in patch:
            _fail(f"{label}: replace patch needs value", "invalid_fixture")
        parent[final] = copy.deepcopy(patch["value"])


def validate_fixture_set(root: Path = ROOT) -> dict[str, Any]:
    fixture_dir = root / "data/planner/fixtures"
    fixture_paths = sorted(fixture_dir.glob("*.json"))
    _require(bool(fixture_paths), "planner contract fixtures are missing", "invalid_fixture")
    base = build_minimal_snapshot(root)
    fixture_ids: set[str] = set()
    accepted = 0
    rejected = 0
    rejection_categories: dict[str, int] = {}
    for path in fixture_paths:
        fixture = load_json(path)
        _require(isinstance(fixture, dict), f"{path.name}: fixture must be an object", "invalid_fixture")
        _exact_keys(fixture, {"fixture_id", "description", "patches", "expected_error"}, path.name, "invalid_fixture")
        fixture_id = _nonempty_string(fixture.get("fixture_id"), f"{path.name}.fixture_id", "invalid_fixture")
        _require(fixture_id not in fixture_ids, f"duplicate planner fixture_id {fixture_id}", "invalid_fixture")
        fixture_ids.add(fixture_id)
        patches = fixture.get("patches")
        _require(isinstance(patches, list), f"{path.name}: patches must be an array", "invalid_fixture")
        expected_error = fixture.get("expected_error")
        _require(expected_error is None or isinstance(expected_error, str) and bool(expected_error), f"{path.name}: expected_error must be null or a category", "invalid_fixture")
        candidate = copy.deepcopy(base)
        for index, patch in enumerate(patches):
            _apply_patch(candidate, _object(patch, f"{path.name}.patches[{index}]", "invalid_fixture"), f"{path.name}.patches[{index}]")
        try:
            validate_snapshot(candidate, root)
        except PlannerContractError as exc:
            if expected_error is None:
                _fail(f"{path.name}: unexpected rejection [{exc.category}]: {exc}", "invalid_fixture")
            _require(exc.category == expected_error, f"{path.name}: expected {expected_error}, got {exc.category}: {exc}", "invalid_fixture")
            rejected += 1
            rejection_categories[exc.category] = rejection_categories.get(exc.category, 0) + 1
        else:
            _require(expected_error is None, f"{path.name}: expected rejection [{expected_error}] but snapshot was accepted", "invalid_fixture")
            accepted += 1
    return {
        "fixtures": len(fixture_paths),
        "accepted": accepted,
        "rejected": rejected,
        "rejection_categories": rejection_categories,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        validate_contract_schemas(root)
        result = validate_fixture_set(root)
        output_result = validate_output_fixture_set(root)
        print("PASS Planner Input Snapshot v0.1, User Configuration v0.1 and Planner Output v0.1 schema metadata")
        print(f"PASS input contract fixtures: {result['fixtures']} ({result['accepted']} accepted / {result['rejected']} expected rejection)")
        print(f"PASS output contract fixtures: {output_result['fixtures']} ({output_result['accepted']} accepted / {output_result['rejected']} expected rejection)")
        print("PASS input/output version traceability, timezone/date horizon, targets, Explain references and capacity invariants")
        print("PASS canonical input semantics; no Planner output is generated and no scheduling policy is executed")
        for category, count in sorted(result["rejection_categories"].items()):
            print(f"  input {category}: {count}")
        for category, count in sorted(output_result["rejection_categories"].items()):
            print(f"  output {category}: {count}")
        return 0
    except PlannerContractError as exc:
        print(f"FAIL [{exc.category}]: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
