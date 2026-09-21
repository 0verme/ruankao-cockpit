"""P4.6 / P4.7 review-domain test kit (design stage).

本模块**不包含任何 production policy**。它只提供：

* fixture / fixture-plan 装载与结构校验；
* canonical JSON 编码与 digest；
* deterministic replay 的性质测试 harness；
* 禁止 wall-clock 依赖的静态源码扫描。

contract freeze 之后，fixture 只需要填充 `expected` / `expected_error`，
性质测试 harness 可以直接指向 `engine.review` 的 replay 入口，无需重写测试结构。
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
SCHEMA_DRAFT_PATH = REVIEW_DIR / "fixture-schema.draft.json"
DESIGN_DOC_PATH = ROOT / "docs/PHASE4_TEST_MATRIX.md"
BASELINE_PATH = ROOT / "tests/baselines/progress_v01_semantics.json"

FIXTURE_SCHEMA_VERSION = "review-fixture/v0.1-draft"
PLAN_MANIFEST_VERSION = "review-fixture-plan/v0.1"

FIXTURE_ID_RE = re.compile(r"^(?:id|evidence|mastery|sched|determinism|time|compat|invalid)-[a-z0-9]+(?:-[a-z0-9]+)*$")
MATRIX_REF_RE = re.compile(r"^[A-I]\d+$")
OWNERS = ("P4.1", "P4.2", "P4.3", "P4.4", "P4.5", "P4.6", "P4.7")
INDEPENDENCE = ("contract_independent", "policy_dependent")
IMPLEMENTATIONS = ("fixture", "harness", "static", "regression")
EXPECTED_KINDS = ("state", "error")
STATUSES = ("planned", "ready", "implemented")
PREFIX_TO_SECTIONS = {
    "id": {"A"},
    "evidence": {"B"},
    "mastery": {"C"},
    "sched": {"D", "H"},
    "determinism": {"E", "F"},
    "time": {"G"},
    "compat": {"I"},
    "invalid": {"A", "B", "C", "D", "E", "F", "H"},
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


def load_fixture_schema_draft(root: Path | None = None) -> dict[str, Any]:
    return load_json(Path(root or ROOT) / "data/review/fixture-schema.draft.json")


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
    if plan.get("status") != "TEST_DESIGN_READY_WAITING_FOR_CONTRACT_FREEZE":
        errors.append("plan: status must record waiting for contract freeze")

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
        if implementation == "fixture" and status == "implemented":
            errors.append(f"{label}: a fixture entry is either planned or ready, never implemented")
        if implementation != "fixture" and status == "ready":
            errors.append(f"{label}: only implementation=fixture may be ready")

        blocked = entry.get("blocked_by")
        if not isinstance(blocked, list) or any(owner not in OWNERS for owner in blocked):
            errors.append(f"{label}: blocked_by must be a list of owners")
        if entry.get("contract_independence") == "policy_dependent" and not entry.get("policy_symbols"):
            errors.append(f"{label}: policy_dependent entry must reference at least one policy symbol")
        for symbol_name in entry.get("policy_symbols", []) or []:
            if symbol_name not in symbols:
                errors.append(f"{label}: unknown policy symbol {symbol_name!r}")

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
            if not skeleton:
                errors.append(f"{label}: implementation={implementation} needs a skeleton module")
            elif not (root / skeleton).is_file():
                errors.append(f"{label}: skeleton {skeleton!r} does not exist")

    if fixture_dir.is_dir():
        for path in sorted(fixture_dir.glob("*.json")):
            if path.name not in seen_files:
                errors.append(f"fixtures/{path.name}: file on disk is not declared in fixture-plan.json")
            elif path.name not in declared_ready:
                errors.append(f"fixtures/{path.name}: file on disk must be declared status=ready")

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
def validate_review_fixture_shape(
    data: Any, label: str, *, require_expectation: bool = True
) -> None:
    if not isinstance(data, Mapping):
        raise FixtureContractError(f"{label}: fixture must be an object")
    if data.get("schema_version") != FIXTURE_SCHEMA_VERSION:
        raise FixtureContractError(f"{label}: wrong fixture schema version {data.get('schema_version')!r}")
    fixture_id = data.get("fixture_id")
    if not isinstance(fixture_id, str) or not fixture_id.strip():
        raise FixtureContractError(f"{label}: fixture_id is required")
    if not data.get("description"):
        raise FixtureContractError(f"{label}: description is required")
    if "as_of" not in data:
        raise FixtureContractError(f"{label}: as_of is required")
    parse_instant(data["as_of"])
    if not isinstance(data.get("timezone"), str) or not data["timezone"].strip():
        raise FixtureContractError(f"{label}: timezone is required")

    has_events = isinstance(data.get("events"), list) and data["events"]
    has_event_cases = isinstance(data.get("events_by_case"), Mapping) and data["events_by_case"]
    if not (has_events or has_event_cases):
        raise FixtureContractError(f"{label}: events or events_by_case is required")

    has_expected = "expected" in data
    has_error = "expected_error" in data
    if has_expected and has_error:
        raise FixtureContractError(f"{label}: expected and expected_error are mutually exclusive")
    if require_expectation and not (has_expected or has_error):
        raise FixtureContractError(f"{label}: expected or expected_error is required for a shipped fixture")

    for variant_index, variant in enumerate(data.get("variants", []) or []):
        variant_label = f"{label}.variants[{variant_index}]"
        if not isinstance(variant, Mapping):
            raise FixtureContractError(f"{variant_label}: must be an object")
        if not variant.get("variant_id"):
            raise FixtureContractError(f"{variant_label}: variant_id is required")
        if "as_of" in variant:
            parse_instant(variant["as_of"])
        variant_expected = "expected" in variant
        variant_error = "expected_error" in variant
        if variant_expected and variant_error:
            raise FixtureContractError(f"{variant_label}: expected and expected_error are mutually exclusive")
        if require_expectation and not (variant_expected or variant_error):
            raise FixtureContractError(f"{variant_label}: expected or expected_error is required")

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


def load_review_fixture(path: Path, *, require_expectation: bool = True) -> dict[str, Any]:
    path = Path(path)
    data = load_json(path)
    validate_review_fixture_shape(data, path.name, require_expectation=require_expectation)
    if data["fixture_id"] != path.stem:
        raise FixtureContractError(f"{path.name}: fixture_id must equal the file stem")
    return data


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
