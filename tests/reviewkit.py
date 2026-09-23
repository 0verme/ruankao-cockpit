"""P4.6 / P4.7 review-domain fixture validation and deterministic test helpers.

本模块不实现 policy；只装载正式 fixture、验证机器契约、比较 replay 结果，
并提供重复性、顺序独立性和时区等价性的性质检查。
"""
from __future__ import annotations

import copy
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import random
import re
from typing import Any, Callable, Iterable, Mapping, Sequence

from engine.progress.model import FORBIDDEN_CONTENT_KEYS

ROOT = Path(__file__).resolve().parents[1]
REVIEW_DIR = ROOT / "data/review"
FIXTURE_DIR = REVIEW_DIR / "fixtures"
PLAN_PATH = REVIEW_DIR / "fixture-plan.json"
DESIGN_DOC_PATH = ROOT / "docs/PHASE4_TEST_MATRIX.md"
BASELINE_PATH = ROOT / "tests/baselines/progress_v01_semantics.json"

FIXTURE_SCHEMA_VERSION = "mastery-review-fixture/v0.1"
PLAN_MANIFEST_VERSION = "review-fixture-plan/v0.2"

FIXTURE_ID_RE = re.compile(r"^(?:id|evidence|mastery|sched|determinism|time|compat|invalid)-[a-z0-9]+(?:-[a-z0-9]+)*$")
MATRIX_REF_RE = re.compile(r"^[A-I]\d+$")
OWNERS = ("P4.1", "P4.2", "P4.3", "P4.4", "P4.5", "P4.6", "P4.7")
INDEPENDENCE = ("contract_independent", "policy_dependent")
IMPLEMENTATIONS = ("fixture", "harness", "static", "regression")
EXPECTED_KINDS = ("state", "error")
STATUSES = ("planned", "ready", "implemented", "not_applicable")
PREFIX_TO_SECTIONS = {
    "id": {"A"},
    "evidence": {"B"},
    "mastery": {"C"},
    "sched": {"D", "H"},
    "determinism": {"E", "F"},
    "time": {"G"},
    "compat": {"I"},
    "invalid": set("ABCDEFGHI"),
}

WALL_CLOCK_PATTERNS = (
    r"\bdatetime\.now\s*\(",
    r"\bdatetime\.utcnow\s*\(",
    r"\bdatetime\.today\s*\(",
    r"\bdate\.today\s*\(",
    r"\btime\.time\s*\(",
    r"\btime\.monotonic\s*\(",
    r"\bdatetime\.fromtimestamp\s*\(",
)


class FixtureContractError(ValueError):
    """fixture / fixture-plan 结构不符合 draft contract。"""


class DeterminismViolation(AssertionError):
    """deterministic replay 性质被违反。"""


# ---------------------------------------------------------------------------
# JSON helpers
# ---------------------------------------------------------------------------
def canonical_json(value: Any) -> str:
    """稳定序列化：sorted keys、紧凑分隔符、保留非 ASCII。"""
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def state_digest(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def load_json(path: Path) -> Any:
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise FixtureContractError(f"cannot read JSON {path}: {exc}") from exc


def parse_instant(value: Any) -> datetime:
    """解析 timezone-aware instant；naive 值直接失败。"""
    if isinstance(value, datetime):
        parsed = value
    else:
        if not isinstance(value, str) or not value.strip():
            raise FixtureContractError(f"timestamp must be an ISO 8601 string, got {value!r}")
        text = value[:-1] + "+00:00" if value.endswith("Z") else value
        try:
            parsed = datetime.fromisoformat(text)
        except ValueError as exc:
            raise FixtureContractError(f"invalid ISO 8601 timestamp: {value!r}") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise FixtureContractError(f"timezone-aware timestamp required, got {value!r}")
    return parsed.astimezone(timezone.utc)


def _same_instant(left: Any, right: Any) -> bool:
    try:
        return parse_instant(left) == parse_instant(right)
    except FixtureContractError:
        return left == right


# ---------------------------------------------------------------------------
# fixture plan (design manifest)
# ---------------------------------------------------------------------------
def load_fixture_plan(root: Path | None = None) -> dict[str, Any]:
    return load_json(Path(root or ROOT) / "data/review/fixture-plan.json")


def load_fixture_schema(root: Path | None = None) -> dict[str, Any]:
    return load_json(Path(root or ROOT) / "data/review/fixture-schema.v0.1.json")


def declared_fixture_files(plan: Mapping[str, Any]) -> list[str]:
    return [entry["file"] for entry in plan.get("fixtures", []) if entry.get("implementation") == "fixture"]


def validate_fixture_plan(plan: Mapping[str, Any], root: Path | None = None) -> list[str]:
    """返回所有结构问题；空列表代表 plan 与 skeleton 一致。"""
    root = Path(root or ROOT)
    errors: list[str] = []

    if not isinstance(plan, Mapping):
        return ["plan must be an object"]
    if plan.get("manifest_version") != PLAN_MANIFEST_VERSION:
        errors.append(f"plan: manifest_version must be {PLAN_MANIFEST_VERSION!r}")
    if plan.get("status") != "REVIEW_FIXTURE_MATRIX_FROZEN":
        errors.append("plan: status must record the frozen P4.6/P4.7 matrix")
    if plan.get("fixture_schema") != FIXTURE_SCHEMA_VERSION:
        errors.append(f"plan: fixture_schema must name the frozen {FIXTURE_SCHEMA_VERSION} contract")
    p4_6 = plan.get("p4_6")
    if not isinstance(p4_6, Mapping):
        errors.append("plan: p4_6 status block is required")
    else:
        if p4_6.get("status") != "FROZEN":
            errors.append("plan: p4_6 must remain FROZEN")
        if p4_6.get("fixture_schema") != FIXTURE_SCHEMA_VERSION:
            errors.append(f"plan: p4_6.fixture_schema must be {FIXTURE_SCHEMA_VERSION!r}")
    p4_7 = plan.get("p4_7")
    if not isinstance(p4_7, Mapping) or p4_7.get("status") != "COMPLETE":
        errors.append("plan: p4_7 must record the completed edge-case suite")
    for later_phase in ("p4_8", "p4_9"):
        later = plan.get(later_phase)
        if isinstance(later, Mapping) and later.get("status") in {"COMPLETE", "FROZEN", "PASS"}:
            errors.append(f"plan: {later_phase} must not be marked complete by the P4.6/P4.7 fixture window")

    symbols = plan.get("policy_symbols")
    if not isinstance(symbols, Mapping) or not symbols:
        errors.append("plan: policy_symbols must be a non-empty object")
        symbols = {}
    for name, symbol in symbols.items():
        if not isinstance(symbol, Mapping):
            errors.append(f"policy_symbols[{name}]: must be an object")
            continue
        if symbol.get("owner") not in OWNERS:
            errors.append(f"policy_symbols[{name}]: owner must be one of {OWNERS}")
        if not symbol.get("description"):
            errors.append(f"policy_symbols[{name}]: description is required")
        status = symbol.get("status")
        if status == "unfrozen":
            if symbol.get("value") is not None:
                errors.append(f"policy_symbols[{name}]: unfrozen symbol must not carry a value")
        elif status == "frozen":
            if symbol.get("value") is None:
                errors.append(f"policy_symbols[{name}]: frozen symbol needs a value")
            if not symbol.get("frozen_by"):
                errors.append(f"policy_symbols[{name}]: frozen symbol needs frozen_by")
        else:
            errors.append(f"policy_symbols[{name}]: status must be 'unfrozen' or 'frozen'")

    entries = plan.get("fixtures")
    if not isinstance(entries, list) or not entries:
        return errors + ["plan: fixtures must be a non-empty list"]

    fixture_dir = root / "data/review/fixtures"
    seen_ids: set[str] = set()
    seen_files: set[str] = set()
    declared_ready: set[str] = set()
    for index, entry in enumerate(entries):
        label = f"fixtures[{index}]"
        if not isinstance(entry, Mapping):
            errors.append(f"{label}: must be an object")
            continue
        fixture_id = entry.get("fixture_id")
        if not isinstance(fixture_id, str) or FIXTURE_ID_RE.fullmatch(fixture_id) is None:
            errors.append(f"{label}: invalid fixture_id {fixture_id!r}")
            continue
        if fixture_id in seen_ids:
            errors.append(f"{label}: duplicate fixture_id {fixture_id!r}")
        seen_ids.add(fixture_id)

        implementation = entry.get("implementation")
        if implementation not in IMPLEMENTATIONS:
            errors.append(f"{label}: implementation must be one of {IMPLEMENTATIONS}")
        if entry.get("contract_independence") not in INDEPENDENCE:
            errors.append(f"{label}: contract_independence must be one of {INDEPENDENCE}")
        if entry.get("expected_kind") not in EXPECTED_KINDS:
            errors.append(f"{label}: expected_kind must be one of {EXPECTED_KINDS}")
        status = entry.get("status")
        if status not in STATUSES:
            errors.append(f"{label}: status must be one of {STATUSES}")
        if implementation == "fixture" and status not in {"planned", "ready"}:
            errors.append(f"{label}: fixture entries must be planned or ready")
        if implementation != "fixture" and status == "ready":
            errors.append(f"{label}: only implementation=fixture may be ready")
        if status == "not_applicable" and not entry.get("resolution"):
            errors.append(f"{label}: not_applicable entries require a resolution")
        if status == "planned":
            errors.append(f"{label}: P4.6/P4.7 matrix must not retain planned entries")
        if status == "implemented" and not entry.get("skeleton"):
            errors.append(f"{label}: implemented coverage requires a test skeleton")

        blocked = entry.get("blocked_by", [])
        if not isinstance(blocked, list) or any(owner not in OWNERS for owner in blocked):
            errors.append(f"{label}: blocked_by must be a list of owners")
        if blocked:
            errors.append(f"{label}: frozen matrix entries must not remain blocked")
        contract_refs = entry.get("contract_refs")
        if not isinstance(contract_refs, list) or not contract_refs or any(not isinstance(ref, str) for ref in contract_refs):
            errors.append(f"{label}: contract_refs must trace the expected result")
            contract_refs = []
        if implementation == "fixture":
            for required_ref in (
                "data/review/mastery-review-state.schema.json",
                "engine/review/replay.py",
                "docs/review/REVIEW_OUTCOME_ADAPTER_V01.md",
            ):
                if required_ref not in contract_refs:
                    errors.append(f"{label}: contract_refs must include {required_ref!r}")
        if entry.get("contract_independence") == "policy_dependent" and not entry.get("policy_symbols"):
            errors.append(f"{label}: policy_dependent entry must reference at least one policy symbol")
        for symbol_name in entry.get("policy_symbols", []) or []:
            symbol = symbols.get(symbol_name)
            if not isinstance(symbol, Mapping) or symbol.get("status") != "frozen":
                errors.append(f"{label}: policy symbol {symbol_name!r} is not frozen")
                continue
            frozen_source = str(symbol.get("frozen_by", "")).split(" (", 1)[0]
            if frozen_source and frozen_source not in contract_refs:
                errors.append(f"{label}: contract_refs must include frozen symbol source {frozen_source!r}")
            if not frozen_source:
                errors.append(f"{label}: policy symbol {symbol_name!r} has no provenance source")

        refs = entry.get("matrix_refs")
        if not isinstance(refs, list) or not refs:
            errors.append(f"{label}: matrix_refs must be a non-empty list")
            refs = []
        sections: set[str] = set()
        for ref in refs:
            if not isinstance(ref, str) or MATRIX_REF_RE.fullmatch(ref) is None:
                errors.append(f"{label}: invalid matrix_ref {ref!r}")
                continue
            sections.add(ref[0])
        prefix = fixture_id.split("-", 1)[0]
        allowed = PREFIX_TO_SECTIONS.get(prefix)
        if allowed is None:
            errors.append(f"{label}: unknown prefix {prefix!r}")
        elif not sections <= allowed:
            errors.append(
                f"{label}: matrix_refs {sorted(sections)} do not match prefix {prefix!r} (allowed {sorted(allowed)})"
            )

        if implementation == "fixture":
            file_name = entry.get("file")
            if file_name != f"{fixture_id}.json":
                errors.append(f"{label}: file must equal '<fixture_id>.json'")
            if file_name in seen_files:
                errors.append(f"{label}: duplicate fixture file {file_name!r}")
            seen_files.add(file_name)
            if status == "ready":
                declared_ready.add(file_name)
                if not (fixture_dir / file_name).is_file():
                    errors.append(f"{label}: status=ready but {file_name} is missing on disk")
        else:
            if entry.get("file") is not None:
                errors.append(f"{label}: only implementation=fixture may declare a file")
            skeleton = entry.get("skeleton")
            if status != "not_applicable" and not skeleton:
                errors.append(f"{label}: implementation={implementation} needs a skeleton module")
            elif skeleton and not (root / skeleton).is_file():
                errors.append(f"{label}: skeleton {skeleton!r} does not exist")

    if fixture_dir.is_dir():
        for path in sorted(fixture_dir.glob("*.json")):
            if path.name not in seen_files:
                errors.append(f"fixtures/{path.name}: file on disk is not declared in fixture-plan.json")
            elif path.name not in declared_ready:
                errors.append(f"fixtures/{path.name}: file on disk must be declared status=ready")

    if set(plan.get("policy_symbols", {})):
        unfrozen = [name for name, symbol in plan["policy_symbols"].items() if symbol.get("status") != "frozen"]
        if unfrozen:
            errors.append(f"plan: policy symbols remain unfrozen: {', '.join(sorted(unfrozen))}")

    compat = plan.get("backward_compatibility")
    if not isinstance(compat, Mapping):
        errors.append("plan: backward_compatibility section is required")
    else:
        for key in ("baseline", "skeleton"):
            value = compat.get(key)
            if not value or not (root / value).is_file():
                errors.append(f"backward_compatibility.{key}: file {value!r} does not exist")
        for key in ("progress_valid_replay", "progress_expected_rejections"):
            if not isinstance(compat.get(key), list) or not compat[key]:
                errors.append(f"backward_compatibility.{key}: must be a non-empty list")
    return errors


def cross_check_matrix_refs(plan: Mapping[str, Any], doc_text: str) -> list[str]:
    """plan 中声明的 matrix_ref 必须能在设计文档中找到。"""
    missing: list[str] = []
    for entry in plan.get("fixtures", []):
        for ref in entry.get("matrix_refs", []) or []:
            if re.search(rf"(?<![A-Za-z0-9]){re.escape(ref)}(?![0-9])", doc_text) is None:
                missing.append(f"{entry.get('fixture_id')}: matrix_ref {ref} not documented")
    return missing


# ---------------------------------------------------------------------------
# review fixtures
# ---------------------------------------------------------------------------
def _schema_type_matches(value: Any, expected_type: str) -> bool:
    if expected_type == "object":
        return isinstance(value, Mapping)
    if expected_type == "array":
        return isinstance(value, list)
    if expected_type == "string":
        return isinstance(value, str)
    if expected_type == "integer":
        return type(value) is int
    if expected_type == "number":
        return type(value) in {int, float}
    if expected_type == "boolean":
        return type(value) is bool
    if expected_type == "null":
        return value is None
    return False


def _resolve_schema_ref(schema: Mapping[str, Any], root_schema: Mapping[str, Any]) -> Mapping[str, Any]:
    reference = schema.get("$ref")
    if not isinstance(reference, str) or not reference.startswith("#/"):
        raise FixtureContractError(f"unsupported JSON Schema reference {reference!r}")
    resolved: Any = root_schema
    for token in reference[2:].split("/"):
        token = token.replace("~1", "/").replace("~0", "~")
        if not isinstance(resolved, Mapping) or token not in resolved:
            raise FixtureContractError(f"unresolved JSON Schema reference {reference!r}")
        resolved = resolved[token]
    if not isinstance(resolved, Mapping):
        raise FixtureContractError(f"JSON Schema reference {reference!r} is not an object")
    return resolved


def _validate_schema_node(
    value: Any,
    node: Mapping[str, Any],
    root_schema: Mapping[str, Any],
    label: str,
) -> None:
    if "$ref" in node:
        _validate_schema_node(value, _resolve_schema_ref(node, root_schema), root_schema, label)
    if "oneOf" in node:
        matches = 0
        for candidate in node["oneOf"]:
            try:
                _validate_schema_node(value, candidate, root_schema, label)
            except FixtureContractError:
                continue
            matches += 1
        if matches != 1:
            raise FixtureContractError(f"{label}: expected exactly one JSON Schema oneOf branch, got {matches}")
    if "not" in node:
        try:
            _validate_schema_node(value, node["not"], root_schema, label)
        except FixtureContractError:
            pass
        else:
            raise FixtureContractError(f"{label}: JSON Schema not constraint matched")
    expected_type = node.get("type")
    if expected_type is not None:
        types = expected_type if isinstance(expected_type, list) else [expected_type]
        if not any(_schema_type_matches(value, item) for item in types):
            raise FixtureContractError(f"{label}: expected JSON type {expected_type!r}")
    if "const" in node and value != node["const"]:
        raise FixtureContractError(f"{label}: expected constant {node['const']!r}")
    if "enum" in node and value not in node["enum"]:
        raise FixtureContractError(f"{label}: value {value!r} is outside the frozen enum")
    if "minLength" in node and isinstance(value, str) and len(value) < node["minLength"]:
        raise FixtureContractError(f"{label}: string shorter than minLength")
    if "pattern" in node and isinstance(value, str) and re.search(node["pattern"], value) is None:
        raise FixtureContractError(f"{label}: string does not match the required pattern")
    if "minimum" in node and type(value) in {int, float} and value < node["minimum"]:
        raise FixtureContractError(f"{label}: number is below minimum")
    if node.get("format") == "date-time" and isinstance(value, str):
        parse_instant(value)
    elif node.get("format") == "date" and isinstance(value, str):
        try:
            if datetime.fromisoformat(value).date().isoformat() != value:
                raise ValueError(value)
        except ValueError as exc:
            raise FixtureContractError(f"{label}: invalid ISO date {value!r}") from exc
    if isinstance(value, Mapping):
        for required in node.get("required", []):
            if required not in value:
                raise FixtureContractError(f"{label}: missing required field {required!r}")
        properties = node.get("properties", {})
        for key, child in properties.items():
            if key in value:
                _validate_schema_node(value[key], child, root_schema, f"{label}.{key}")
        additional = node.get("additionalProperties", True)
        for key, child_value in value.items():
            if key in properties:
                continue
            if additional is False:
                raise FixtureContractError(f"{label}: unknown field {key!r}")
            if isinstance(additional, Mapping):
                _validate_schema_node(child_value, additional, root_schema, f"{label}.{key}")
    if isinstance(value, list):
        if len(value) < node.get("minItems", 0):
            raise FixtureContractError(f"{label}: array has fewer than minItems")
        if node.get("uniqueItems") and len({canonical_json(item) for item in value}) != len(value):
            raise FixtureContractError(f"{label}: array items must be unique")
        item_schema = node.get("items")
        if isinstance(item_schema, Mapping):
            for index, item in enumerate(value):
                _validate_schema_node(item, item_schema, root_schema, f"{label}[{index}]")


def validate_json_schema(value: Any, schema: Mapping[str, Any], label: str) -> None:
    _validate_schema_node(value, schema, schema, label)


def validate_review_fixture_shape(
    data: Any, label: str, *, require_expectation: bool = True,
    schema: Mapping[str, Any] | None = None,
) -> None:
    if not isinstance(data, Mapping):
        raise FixtureContractError(f"{label}: fixture must be an object")
    if schema is None:
        schema = load_fixture_schema()
    validate_json_schema(data, schema, label)
    if require_expectation and not ("expected" in data or "expected_error" in data):
        raise FixtureContractError(f"{label}: expected or expected_error is required")
    for index, variant in enumerate(data.get("variants", [])):
        if require_expectation and not ("expected" in variant or "expected_error" in variant):
            raise FixtureContractError(f"{label}.variants[{index}]: expected or expected_error is required")
    _reject_forbidden_content(data, label)


def _reject_forbidden_content(value: Any, label: str) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            if key in FORBIDDEN_CONTENT_KEYS:
                raise FixtureContractError(f"{label}: disallowed content field {key!r}")
            _reject_forbidden_content(child, f"{label}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_forbidden_content(child, f"{label}[{index}]")


def load_review_fixture(
    path: Path, *, require_expectation: bool = True,
    schema: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    path = Path(path)
    data = load_json(path)
    validate_review_fixture_shape(
        data, path.name, require_expectation=require_expectation, schema=schema
    )
    if data["fixture_id"] != path.stem:
        raise FixtureContractError(f"{path.name}: fixture_id must equal the file stem")
    return data


def fixture_cases(fixture: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Expand one fixture and its explicit boundary variants into replay calls."""
    base = {
        "case_id": "base",
        "input": fixture["input"],
        "as_of": fixture["as_of"],
        "timezone": fixture["timezone"],
        "expected": fixture.get("expected"),
        "expected_error": fixture.get("expected_error"),
    }
    cases = [base]
    for variant in fixture.get("variants", []):
        cases.append({
            "case_id": variant["variant_id"],
            "input": variant.get("input", fixture["input"]),
            "as_of": variant.get("as_of", fixture["as_of"]),
            "timezone": variant.get("timezone", fixture["timezone"]),
            "expected": variant.get("expected"),
            "expected_error": variant.get("expected_error"),
        })
    return cases


def assert_expected_projection(actual: Any, expected: Any, label: str = "expected") -> None:
    """Compare a recursively partial state projection without ignoring array order."""
    if isinstance(expected, Mapping):
        if not isinstance(actual, Mapping):
            raise FixtureContractError(f"{label}: expected an object projection")
        for key, value in expected.items():
            if key not in actual:
                raise FixtureContractError(f"{label}: output is missing {key!r}")
            assert_expected_projection(actual[key], value, f"{label}.{key}")
        return
    if canonical_json(actual) != canonical_json(expected):
        raise FixtureContractError(f"{label}: expected {expected!r}, got {actual!r}")


def validate_mastery_review_state(
    state: Mapping[str, Any],
    *,
    as_of: Any,
    timezone_name: str,
    state_schema: Mapping[str, Any],
) -> None:
    """Validate the complete P4.5 output schema and item/aggregate invariants."""
    validate_json_schema(state, state_schema, "MasteryReviewState")
    expected_versions = {
        "schema_version": "mastery-review-state/v0.1",
        "review_model_version": "review-model/v0.1",
        "review_event_schema_version": "review-event/v0.1",
        "review_evidence_version": "review-evidence/v0.1",
        "progress_event_schema_version": "progress-event/v0.1",
        "progress_replay_version": "progress-replay/v0.1",
        "mastery_policy_version": "mastery-policy/spaced-consecutive/v0.1",
        "review_policy_version": "review-policy/simple-ladder/v0.1",
        "policy_projection_schema_version": "review-policy-projection/v0.1",
    }
    for field, expected in expected_versions.items():
        if state.get(field) != expected:
            raise FixtureContractError(f"MasteryReviewState.{field}: expected {expected!r}")
    if not _same_instant(state.get("as_of"), as_of):
        raise FixtureContractError("MasteryReviewState.as_of does not match fixture as_of")
    if state.get("timezone") != timezone_name or state.get("schedule_timezone") != timezone_name:
        raise FixtureContractError("MasteryReviewState timezone metadata does not match fixture timezone")
    if not isinstance(state.get("tzdata_version"), str) or not state["tzdata_version"].strip():
        raise FixtureContractError("MasteryReviewState.tzdata_version must be recorded")
    adapter = state.get("outcome_adapter", {})
    if adapter.get("adapter") != "review-outcome/raw-facts/v0.1":
        raise FixtureContractError("MasteryReviewState outcome adapter version is missing or unsupported")

    items = state.get("items", {})
    if state.get("item_order") != sorted(items):
        raise FixtureContractError("MasteryReviewState item_order must be the sorted item registry")
    mastery_counts = {name: 0 for name in ("new", "learning", "mastered")}
    review_counts = {name: 0 for name in ("not_scheduled", "scheduled", "due", "overdue")}
    for item_id, item in items.items():
        if item.get("review_item_id") != item_id:
            raise FixtureContractError(f"items[{item_id}].review_item_id mismatch")
        mastery = item.get("mastery_state")
        status = item.get("review_status")
        if mastery not in mastery_counts or status not in review_counts:
            raise FixtureContractError(f"items[{item_id}] has an unknown mastery or review state")
        mastery_counts[mastery] += 1
        review_counts[status] += 1
        traces = item.get("evidence", [])
        if item.get("evidence_ids") != [trace.get("evidence_id") for trace in traces]:
            raise FixtureContractError(f"items[{item_id}].evidence_ids do not match evidence trace")
        outcomes = [trace.get("policy_outcome") for trace in traces]
        if item.get("successful_review_count") != outcomes.count("success"):
            raise FixtureContractError(f"items[{item_id}] successful_review_count differs from evidence trace")
        if item.get("failure_count") != outcomes.count("failure"):
            raise FixtureContractError(f"items[{item_id}] failure_count differs from evidence trace")
        if item.get("insufficient_evidence_count") != outcomes.count("insufficient"):
            raise FixtureContractError(f"items[{item_id}] insufficient_evidence_count differs from evidence trace")
        if item.get("evaluated_evidence_count") != outcomes.count("success") + outcomes.count("failure"):
            raise FixtureContractError(f"items[{item_id}] evaluated_evidence_count differs from evidence trace")
        for trace in traces:
            kind = trace.get("evidence_kind")
            status_value = trace.get("evidence_status")
            value = trace.get("evidence_value")
            outcome = trace.get("policy_outcome")
            reason = trace.get("policy_outcome_reason")
            if status_value in {"insufficient_evidence", "unsupported"} or kind in {"case_score", "case_capability_score"}:
                expected_outcome = "insufficient"
                expected_reason = "score_outcome_mapping_unfrozen" if status_value == "supported" else (
                    "unsupported_evidence" if status_value == "unsupported" else "insufficient_evidence"
                )
            elif kind == "comprehensive_correctness" and status_value == "supported":
                expected_outcome = "success" if value["correct"] else "failure"
                expected_reason = "comprehensive_correctness_fact"
            else:
                raise FixtureContractError(f"items[{item_id}] evidence trace has an unsupported raw-fact mapping")
            if outcome != expected_outcome or reason != expected_reason:
                raise FixtureContractError(f"items[{item_id}] outcome adapter trace contradicts raw-facts v0.1")
        if mastery == "new" and (item["evaluated_evidence_count"] != 0 or status != "not_scheduled"):
            raise FixtureContractError(f"items[{item_id}] new state must have no evaluated evidence and no schedule")
        if mastery != "new" and item["evaluated_evidence_count"] == 0:
            raise FixtureContractError(f"items[{item_id}] evaluated evidence is required outside new state")

    review = state.get("review", {})
    mastery = state.get("mastery", {})
    if review.get("total_items") != len(items):
        raise FixtureContractError("review.total_items differs from item count")
    for field, status in (
        ("not_scheduled_count", "not_scheduled"),
        ("scheduled_count", "scheduled"),
        ("due_today_count", "due"),
        ("overdue_count", "overdue"),
    ):
        if review.get(field) != review_counts[status]:
            raise FixtureContractError(f"review.{field} differs from item-level projection")
    if review.get("due_count") != review_counts["due"] + review_counts["overdue"]:
        raise FixtureContractError("review.due_count must equal due_today_count + overdue_count")
    if review.get("due_count") != sum(
        item.get("review_status") in {"due", "overdue"} for item in items.values()
    ):
        raise FixtureContractError("review.due_count differs from item-level due projection")
    for field, state_name in (
        ("new_count", "new"), ("learning_count", "learning"), ("mastered_count", "mastered")
    ):
        if mastery.get(field) != mastery_counts[state_name]:
            raise FixtureContractError(f"mastery.{field} differs from item-level mastery states")


def assert_review_replay_properties(
    replay_fn: Callable[..., Any],
    input_data: Mapping[str, Any],
    *,
    as_of: Any,
    timezone_name: str,
    policies: Mapping[str, str],
    taxonomy: Mapping[str, Any],
    capabilities: Mapping[str, Any],
    label: str,
    seeds: Sequence[int] = (0, 7, 20260921),
) -> Any:
    """Exercise P4.5 replay repeatability, ordering and equivalent-instant behavior."""
    frozen = copy.deepcopy(input_data)
    taxonomy_frozen = copy.deepcopy(taxonomy)
    capabilities_frozen = copy.deepcopy(capabilities)

    def call(payload: Mapping[str, Any], run_as_of: Any = as_of, run_timezone: str = timezone_name) -> Any:
        return replay_fn(
            payload["progress_events"],
            payload["review_events"],
            payload["items"],
            taxonomy,
            capabilities,
            as_of=run_as_of,
            timezone=run_timezone,
            mastery_policy=policies["mastery"],
            review_policy=policies["review"],
        )

    baseline = call(input_data)
    if canonical_json(call(input_data)) != canonical_json(baseline):
        raise DeterminismViolation(f"{label}: repeatability violated")
    for seed in seeds:
        shuffled = copy.deepcopy(frozen)
        for key in ("progress_events", "review_events", "items"):
            random.Random(seed).shuffle(shuffled[key])
        if canonical_json(call(shuffled)) != canonical_json(baseline):
            raise DeterminismViolation(f"{label}: input-order independence violated (seed={seed})")

    for offset in ("+08:00", "+09:00"):
        rewritten = copy.deepcopy(frozen)
        rewritten["progress_events"] = rewrite_event_offsets(rewritten["progress_events"], offset)
        rewritten["review_events"] = rewrite_event_offsets(rewritten["review_events"], offset)
        if canonical_json(call(rewritten)) != canonical_json(baseline):
            raise DeterminismViolation(f"{label}: UTC equivalent evidence instant changed output ({offset})")
    as_of_instant = parse_instant(as_of)
    for offset in ("+08:00", "+09:00"):
        equivalent_as_of = as_of_instant.astimezone(_tz_from_offset(offset)).isoformat()
        if canonical_json(call(frozen, run_as_of=equivalent_as_of)) != canonical_json(baseline):
            raise DeterminismViolation(f"{label}: UTC equivalent as_of changed output ({offset})")

    if input_data != frozen or taxonomy != taxonomy_frozen or capabilities != capabilities_frozen:
        raise DeterminismViolation(f"{label}: replay mutated a caller-owned input")

    evidence_instants = [
        parse_instant(event["occurred_at"])
        for event in frozen["review_events"]
    ]
    if evidence_instants:
        before_all = min(evidence_instants) - timedelta(seconds=1)
        try:
            call(frozen, run_as_of=before_all.isoformat())
        except Exception as exc:  # noqa: BLE001
            if getattr(exc, "category", None) != "future_evidence":
                raise DeterminismViolation(f"{label}: future evidence rejection category drifted") from exc
        else:
            raise DeterminismViolation(f"{label}: future evidence was not rejected")
    return baseline


# ---------------------------------------------------------------------------
# deterministic replay property harness
# ---------------------------------------------------------------------------
def event_instant(event: Mapping[str, Any], time_key: str = "occurred_at") -> datetime:
    if time_key not in event:
        raise FixtureContractError(f"event missing timestamp field {time_key!r}: {event.get('event_id')!r}")
    return parse_instant(event[time_key])


def _tz_from_offset(offset: str) -> timezone:
    return parse_instant("2000-01-01T00:00:00" + offset).tzinfo  # type: ignore[return-value]


def rewrite_event_offsets(
    events: Iterable[Mapping[str, Any]],
    offset: str,
    *,
    time_keys: Sequence[str] = ("occurred_at",),
) -> list[dict[str, Any]]:
    """保持 instant 不变，只改变 timezone 表示，用于 UTC 等价性测试。"""
    tzinfo = _tz_from_offset(offset)
    rewritten: list[dict[str, Any]] = []
    for event in events:
        clone = copy.deepcopy(dict(event))
        for key in time_keys:
            if isinstance(clone.get(key), str):
                clone[key] = parse_instant(clone[key]).astimezone(tzinfo).isoformat()
        rewritten.append(clone)
    return rewritten


def assert_replay_properties(
    replay_fn: Callable[..., Any],
    events: Sequence[Mapping[str, Any]],
    *,
    as_of: Any,
    timezone_name: str = "UTC",
    label: str = "review replay",
    future_evidence_mode: str = "reject",
    event_time_key: str = "occurred_at",
    as_of_key: str = "as_of",
    time_keys: Sequence[str] = ("occurred_at",),
    seeds: Sequence[int] = (0, 7, 20260921),
    rewrite_to_offsets: Sequence[str] = ("+08:00", "+09:00"),
    expected_rejection: tuple[type[BaseException], ...] = (Exception,),
) -> Any:
    """验证 deterministic replay 的契约无关性质，返回 baseline 结果。

    覆盖：输入不被修改、repeatability、输入顺序独立性、as_of 显式回显、
    future evidence 语义、UTC 等价性。所有问题一次性汇总后抛出。
    """
    if future_evidence_mode not in {"reject", "exclude"}:
        raise ValueError("future_evidence_mode must be 'reject' or 'exclude'")

    events = list(events)
    frozen = copy.deepcopy(events)
    problems: list[str] = []

    def call(payload: Sequence[Mapping[str, Any]], *, run_as_of: Any = as_of, tz: str = timezone_name) -> Any:
        # 故意不预先 copy：replay 必须自己保证不修改输入。
        return replay_fn(payload, as_of=run_as_of, timezone=tz)

    try:
        baseline = call(events)
    except Exception as exc:  # noqa: BLE001 - harness must surface any failure
        raise DeterminismViolation(f"{label}: baseline replay failed: {exc!r}") from exc

    if events != frozen:
        problems.append("replay mutated its input events")
        events = copy.deepcopy(frozen)

    repeat = call(events)
    if canonical_json(repeat) != canonical_json(baseline):
        problems.append("repeatability violated: replay(x) != replay(x)")

    for seed in seeds:
        shuffled = copy.deepcopy(frozen)
        random.Random(seed).shuffle(shuffled)
        if canonical_json(call(shuffled)) != canonical_json(baseline):
            problems.append(f"input-order independence violated (seed={seed})")

    if isinstance(baseline, Mapping) and as_of_key in baseline:
        if not _same_instant(baseline[as_of_key], as_of):
            problems.append(f"as_of echo mismatch: result[{as_of_key!r}] does not match the requested as_of")
    else:
        problems.append(f"as_of echo missing: result must record {as_of_key!r}")

    instants = [event_instant(event, event_time_key) for event in frozen]
    if instants:
        before_all = min(instants) - timedelta(seconds=1)
        if future_evidence_mode == "reject":
            try:
                call(copy.deepcopy(frozen), run_as_of=before_all.isoformat())
            except expected_rejection:
                pass
            else:
                problems.append("future evidence was not rejected when as_of precedes all events")
        else:
            visible = [event for event, instant in zip(frozen, instants) if instant <= before_all]
            try:
                excluded = call(copy.deepcopy(visible), run_as_of=before_all.isoformat())
                expected = call(copy.deepcopy(frozen), run_as_of=before_all.isoformat())
            except Exception as exc:  # noqa: BLE001
                problems.append(f"exclude-mode future evidence check could not run: {exc!r}")
            else:
                if canonical_json(excluded) != canonical_json(expected):
                    problems.append("exclude-mode future evidence leaked into the result")

    for offset in rewrite_to_offsets:
        rewritten = rewrite_event_offsets(frozen, offset, time_keys=time_keys)
        if canonical_json(call(rewritten)) != canonical_json(baseline):
            problems.append(f"UTC equivalence violated for offset {offset}")

    if problems:
        raise DeterminismViolation(f"{label}:\n- " + "\n- ".join(problems))
    return baseline


# ---------------------------------------------------------------------------
# static guard: no wall-clock dependency in replay / policy paths
# ---------------------------------------------------------------------------
def replay_path_python_files(root: Path | None = None) -> list[Path]:
    """需要禁用的 wall-clock 的源码：engine 下 progress / review / replay / policy。"""
    root = Path(root or ROOT)
    engine = root / "engine"
    if not engine.is_dir():
        return []
    files: list[Path] = []
    for path in sorted(engine.rglob("*.py")):
        relative = path.relative_to(root)
        in_domain_dir = any(part in {"progress", "review"} for part in relative.parts)
        name = path.name
        policy_like = name.startswith(("replay", "policy", "scheduler", "mastery", "review"))
        if in_domain_dir or policy_like:
            files.append(path)
    return files


def scan_for_wall_clock(paths: Iterable[Path]) -> list[tuple[Path, int, str]]:
    patterns = [re.compile(pattern) for pattern in WALL_CLOCK_PATTERNS]
    violations: list[tuple[Path, int, str]] = []
    for path in paths:
        try:
            text = Path(path).read_text(encoding="utf-8")
        except OSError:
            continue
        for lineno, line in enumerate(text.splitlines(), start=1):
            if any(pattern.search(line) for pattern in patterns):
                violations.append((Path(path), lineno, line.strip()))
    return violations
