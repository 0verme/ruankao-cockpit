"""Shared local application orchestration for CLI and Streamlit.

This module owns only local Cockpit I/O orchestration. Planner, Progress,
Review and execution semantics remain in their existing domain modules.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import tempfile
from typing import Any, Iterable, Mapping

from engine.execution import record_task_result as execute_task_result
from engine.planner import plan_today
from engine.progress import replay as progress_replay
from engine.review.replay import replay as review_replay
from engine.rules.review_policy_v01 import resolve_timezone


PROJECT_ROOT = Path(__file__).resolve().parent
LOCAL_DIR_NAME = ".local"
CONFIG_SCHEMA_VERSION = "user-configuration/v0.1"
TRANSACTION_SCHEMA_VERSION = "cockpit-record-transaction/v0.1"
PROGRESS_EVENT_SCHEMA_VERSION = "progress-event/v0.1"


class CockpitError(ValueError):
    """A user-facing local storage or command error."""

    def __init__(self, message: str, category: str = "cockpit_error") -> None:
        self.category = category
        super().__init__(message)


@dataclass(frozen=True)
class TodaySnapshot:
    """Rebuildable read model returned by the existing replay/planner path."""

    planner_output: dict[str, Any]
    progress_state: dict[str, Any]
    review_state: dict[str, Any]
    review_items: list[dict[str, Any]]
    taxonomy: dict[str, Any]


@dataclass(frozen=True)
class RecordResult:
    """Facts persisted and the resulting replayed Today view."""

    progress_event_count: int
    review_item_count: int
    review_context_count: int
    today: TodaySnapshot


def _json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def _fsync_directory(path: Path) -> None:
    try:
        descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
    except OSError:  # pragma: no cover - platform/filesystem dependent
        return
    try:
        os.fsync(descriptor)
    except OSError:  # pragma: no cover - platform/filesystem dependent
        pass
    finally:
        os.close(descriptor)


def _atomic_write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(_json_bytes(value))
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        _fsync_directory(path.parent)
    except BaseException:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass
        raise


def _read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise CockpitError(f"Invalid JSON in {path}: {exc}", "invalid_local_data") from exc


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise CockpitError(f"Required local facts file is missing: {path}", "incomplete_local_data") from None
    events: list[dict[str, Any]] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            raise CockpitError(f"{path}:{line_number}: blank JSONL rows are not allowed", "invalid_local_data")
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise CockpitError(f"{path}:{line_number}: invalid JSON: {exc}", "invalid_local_data") from exc
        if not isinstance(value, dict):
            raise CockpitError(f"{path}:{line_number}: each JSONL row must be an object", "invalid_local_data")
        events.append(value)
    return events


def _append_jsonl(path: Path, events: Iterable[Mapping[str, Any]]) -> None:
    rows = list(events)
    if not rows:
        return
    payload = b"".join(
        (json.dumps(dict(event), ensure_ascii=False, separators=(",", ":"), sort_keys=True) + "\n").encode("utf-8")
        for event in rows
    )
    needs_separator = False
    if path.stat().st_size:
        with path.open("rb") as current:
            current.seek(-1, os.SEEK_END)
            needs_separator = current.read(1) != b"\n"
    descriptor = os.open(path, os.O_WRONLY | os.O_APPEND)
    try:
        if needs_separator:
            os.write(descriptor, b"\n")
        view = memoryview(payload)
        while view:
            written = os.write(descriptor, view)
            if written <= 0:
                raise OSError("short write while appending JSONL facts")
            view = view[written:]
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _resolve_local_dir(local_dir: str | Path | None) -> Path:
    return Path(local_dir) if local_dir is not None else Path.cwd() / LOCAL_DIR_NAME


def _ensure_initialized(local: Path) -> None:
    if not local.is_dir():
        if local.exists():
            raise CockpitError(f"{local} exists but is not a directory", "invalid_local_data")
        raise CockpitError("Cockpit 尚未初始化。请先初始化本地数据。", "not_initialized")
    for name in ("config.json", "progress-events.jsonl", "review-events.jsonl", "review-items.json"):
        if not (local / name).is_file():
            raise CockpitError(f"Local data is incomplete: missing {local / name}", "incomplete_local_data")


def _load_resources() -> tuple[dict[str, Any], dict[str, Any]]:
    taxonomy = _read_json(PROJECT_ROOT / "taxonomy" / "taxonomy.json")
    capabilities = _read_json(PROJECT_ROOT / "taxonomy" / "capabilities.json")
    if not isinstance(taxonomy, dict) or not isinstance(capabilities, dict):
        raise CockpitError("Taxonomy and capabilities documents must be JSON objects", "invalid_catalog")
    return taxonomy, capabilities


def _load_user_data(
    local: Path,
) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    _ensure_initialized(local)
    config = _read_json(local / "config.json")
    progress_events = _read_jsonl(local / "progress-events.jsonl")
    review_events = _read_jsonl(local / "review-events.jsonl")
    review_items = _read_json(local / "review-items.json")
    if not isinstance(config, dict):
        raise CockpitError("config.json must contain an object", "invalid_local_data")
    if not isinstance(review_items, list) or any(not isinstance(item, dict) for item in review_items):
        raise CockpitError("review-items.json must contain an array of item objects", "invalid_local_data")
    return config, progress_events, review_events, review_items


def _resolve_as_of(as_of: str | None, timezone_name: str) -> str:
    zone = resolve_timezone(timezone_name)
    if as_of is None:
        instant = datetime.now(zone)
    else:
        normalized = as_of[:-1] + "+00:00" if as_of.endswith("Z") else as_of
        try:
            instant = datetime.fromisoformat(normalized)
        except ValueError as exc:
            raise CockpitError(f"--as-of must be an ISO 8601 timestamp: {as_of!r}", "invalid_timestamp") from exc
        if instant.tzinfo is None or instant.utcoffset() is None:
            raise CockpitError("--as-of must include a timezone offset", "invalid_timestamp")
    return instant.isoformat()


def _make_plan(
    local: Path,
    as_of: str,
    taxonomy: dict[str, Any],
    capabilities: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
    config, progress_events, review_events, review_items = _load_user_data(local)
    progress_state = progress_replay(progress_events, taxonomy, capabilities)
    review_state = review_replay(
        progress_events,
        review_events,
        review_items,
        taxonomy,
        capabilities,
        as_of=as_of,
        timezone=config.get("timezone"),
    )
    planner_input = {
        "schema_version": "planner-input/v0.1",
        "as_of": as_of,
        "timezone": config.get("timezone"),
        "planner_policy": {"policy_id": "planner-policy/input-contract", "policy_version": "v0.1"},
        "inputs": {
            "progress_state": progress_state,
            "mastery_review_state": review_state,
            "taxonomy": {
                "taxonomy_version": taxonomy["taxonomy_version"],
                "topic_ids": sorted(node["id"] for node in taxonomy["nodes"]),
            },
            "capabilities": {
                "taxonomy_version": capabilities["taxonomy_version"],
                "capability_ids": sorted(item["id"] for item in capabilities["capabilities"]),
            },
            "user_configuration": config,
        },
    }
    planner_output = plan_today(planner_input, as_of, root=PROJECT_ROOT)
    return planner_output, progress_state, review_state, review_items


def get_comprehensive_source_references(topic_id: str) -> list[dict[str, Any]]:
    """Return indexed provenance references tagged with a topic, without content."""
    if not isinstance(topic_id, str) or not topic_id:
        return []
    catalog = _read_json(PROJECT_ROOT / "data" / "golden-set" / "comprehensive.sample.json")
    records = catalog.get("records") if isinstance(catalog, Mapping) else None
    if not isinstance(records, list):
        raise CockpitError("Golden Set source index is malformed", "invalid_source_catalog")
    results: list[dict[str, Any]] = []
    for record in records:
        if not isinstance(record, Mapping):
            continue
        topics = record.get("topics")
        source = record.get("source")
        if (
            isinstance(topics, list)
            and any(isinstance(item, Mapping) and item.get("topic_id") == topic_id for item in topics)
            and isinstance(source, Mapping)
        ):
            results.append({
                "record_id": record.get("id"),
                "source_reference": {
                    key: source[key]
                    for key in ("source_id", "source_commit", "source_path", "source_question_id")
                    if key in source
                },
            })
    return results


def _event_id_index(events: Iterable[Mapping[str, Any]]) -> dict[str, Mapping[str, Any]]:
    indexed: dict[str, Mapping[str, Any]] = {}
    for event in events:
        event_id = event.get("event_id")
        if isinstance(event_id, str):
            indexed[event_id] = event
    return indexed


def _check_duplicate_ids(
    existing: list[dict[str, Any]],
    additions: list[Mapping[str, Any]],
    label: str,
) -> None:
    existing_ids = _event_id_index(existing)
    for event in additions:
        event_id = event.get("event_id")
        if isinstance(event_id, str) and event_id in existing_ids:
            raise CockpitError(f"Duplicate {label} event ID: {event_id}", "duplicate_event")


def _validate_facts(
    progress_events: list[dict[str, Any]],
    review_events: list[dict[str, Any]],
    review_items: list[dict[str, Any]],
    taxonomy: dict[str, Any],
    capabilities: dict[str, Any],
    *,
    as_of: str,
    timezone_name: str,
) -> None:
    progress_replay(progress_events, taxonomy, capabilities)
    review_replay(
        progress_events,
        review_events,
        review_items,
        taxonomy,
        capabilities,
        as_of=as_of,
        timezone=timezone_name,
    )


def _merge_recovery_events(
    existing: list[dict[str, Any]],
    additions: list[dict[str, Any]],
    label: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    indexed = _event_id_index(existing)
    append: list[dict[str, Any]] = []
    merged = list(existing)
    for event in additions:
        event_id = event.get("event_id")
        previous = indexed.get(event_id) if isinstance(event_id, str) else None
        if previous is not None:
            if previous != event:
                raise CockpitError(
                    f"Pending transaction conflicts with existing {label} event {event_id!r}",
                    "conflicting_transaction",
                )
            continue
        append.append(event)
        merged.append(event)
        if isinstance(event_id, str):
            indexed[event_id] = event
    return merged, append


def _commit_transaction(local: Path, transaction: Mapping[str, Any]) -> None:
    if transaction.get("schema_version") != TRANSACTION_SCHEMA_VERSION:
        raise CockpitError("Unsupported pending record transaction schema", "invalid_transaction")
    config, progress_events, review_events, current_items = _load_user_data(local)
    added_progress = transaction.get("progress_events")
    added_review = transaction.get("review_events")
    base_items = transaction.get("base_review_items")
    target_items = transaction.get("review_items")
    as_of = transaction.get("as_of")
    if (
        not isinstance(added_progress, list)
        or not isinstance(added_review, list)
        or not isinstance(base_items, list)
        or not isinstance(target_items, list)
        or not isinstance(as_of, str)
    ):
        raise CockpitError("Pending record transaction is malformed", "invalid_transaction")

    merged_progress, append_progress = _merge_recovery_events(progress_events, added_progress, "Progress")
    merged_review, append_review = _merge_recovery_events(review_events, added_review, "Review")
    if current_items == target_items:
        pass
    elif current_items != base_items:
        raise CockpitError(
            "Pending transaction conflicts with review-items.json; no local data was changed",
            "conflicting_transaction",
        )

    taxonomy, capabilities = _load_resources()
    _validate_facts(
        merged_progress,
        merged_review,
        target_items,
        taxonomy,
        capabilities,
        as_of=as_of,
        timezone_name=config.get("timezone"),
    )

    if current_items != target_items:
        _atomic_write_json(local / "review-items.json", target_items)
    _append_jsonl(local / "progress-events.jsonl", append_progress)
    _append_jsonl(local / "review-events.jsonl", append_review)


def _recover_pending(local: Path) -> None:
    pending = local / "pending" / "record.json"
    if not pending.exists():
        return
    transaction = _read_json(pending)
    if not isinstance(transaction, dict):
        raise CockpitError(f"Pending transaction is not an object: {pending}", "invalid_transaction")
    _commit_transaction(local, transaction)
    pending.unlink()
    _fsync_directory(pending.parent)


def initialize_cockpit(local_dir: str | Path | None = None) -> bool:
    """Initialize local files without replacing existing data; return True if created."""
    local = _resolve_local_dir(local_dir)
    if local.exists():
        if local.is_dir():
            return False
        raise CockpitError(f"{local} exists but is not a directory", "invalid_local_data")

    try:
        local.mkdir(parents=True)
    except FileExistsError:
        return False

    _atomic_write_json(local / "config.json", {
        "schema_version": CONFIG_SCHEMA_VERSION,
        "timezone": "Asia/Shanghai",
        "daily_available_minutes": 60,
        "study_days": [1, 2, 3, 4, 5, 6, 7],
    })
    (local / "progress-events.jsonl").touch(exist_ok=False)
    (local / "review-events.jsonl").touch(exist_ok=False)
    _atomic_write_json(local / "review-items.json", [])
    (local / "pending").mkdir()
    # Partial creation remains visible rather than deleting files recursively;
    # subsequent reads fail closed with the exact missing path.
    return True


def get_today(as_of: str | None = None, *, local_dir: str | Path | None = None) -> TodaySnapshot:
    """Replay local facts and return the existing deterministic Today Plan."""
    local = _resolve_local_dir(local_dir)
    _ensure_initialized(local)
    _recover_pending(local)
    config, _, _, _ = _load_user_data(local)
    resolved_as_of = _resolve_as_of(as_of, config.get("timezone"))
    taxonomy, capabilities = _load_resources()
    planner_output, progress_state, review_state, review_items = _make_plan(
        local, resolved_as_of, taxonomy, capabilities
    )
    return TodaySnapshot(planner_output, progress_state, review_state, review_items, taxonomy)


def record_result(
    task_id: str,
    attempt: Mapping[str, Any],
    review_context_event_id: str,
    *,
    as_of: str | None = None,
    local_dir: str | Path | None = None,
) -> RecordResult:
    """Validate, persist, and replay an explicit attempt via the shared execution path."""
    local = _resolve_local_dir(local_dir)
    _ensure_initialized(local)
    _recover_pending(local)
    config, progress_events, review_events, review_items = _load_user_data(local)
    if not isinstance(attempt, Mapping):
        raise CockpitError("attempt must be a JSON object", "invalid_attempt")
    attempt = dict(attempt)
    attempt_id = attempt.get("event_id")
    if isinstance(attempt_id, str) and attempt_id in _event_id_index(progress_events):
        raise CockpitError(f"Duplicate progress event ID: {attempt_id}", "duplicate_event")
    if review_context_event_id in _event_id_index(review_events):
        raise CockpitError(f"Duplicate review event ID: {review_context_event_id}", "duplicate_event")

    resolved_as_of = _resolve_as_of(as_of, config.get("timezone"))
    taxonomy, capabilities = _load_resources()
    planner_output, _, _, _ = _make_plan(local, resolved_as_of, taxonomy, capabilities)
    result = execute_task_result(
        planner_output,
        task_id,
        {
            "progress_event": attempt,
            "review_context_event_id": review_context_event_id,
        },
        taxonomy=taxonomy,
        capabilities=capabilities,
        existing_review_items=review_items,
    )
    added_progress = [dict(event) for event in result["progress_events"]]
    added_review = [dict(event) for event in result["review_events"]]
    added_items = [dict(item) for item in result["review_items"]]

    _check_duplicate_ids(progress_events, added_progress, "Progress")
    _check_duplicate_ids(review_events, added_review, "Review")
    target_items = [*review_items, *added_items]
    _validate_facts(
        [*progress_events, *added_progress],
        [*review_events, *added_review],
        target_items,
        taxonomy,
        capabilities,
        as_of=resolved_as_of,
        timezone_name=config.get("timezone"),
    )

    pending_dir = local / "pending"
    pending = pending_dir / "record.json"
    if pending.exists():
        raise CockpitError(f"A pending record transaction already exists: {pending}", "pending_transaction")
    transaction = {
        "schema_version": TRANSACTION_SCHEMA_VERSION,
        "as_of": resolved_as_of,
        "progress_events": added_progress,
        "review_events": added_review,
        "base_review_items": review_items,
        "review_items": target_items,
    }
    _atomic_write_json(pending, transaction)
    _recover_pending(local)

    updated_today = get_today(resolved_as_of, local_dir=local)
    return RecordResult(len(added_progress), len(added_items), len(added_review), updated_today)


def record_browser_attempt(
    task_id: str,
    *,
    occurred_at: str,
    question: Mapping[str, Any],
    correct: bool,
    error_cause: str | None = None,
    as_of: str | None = None,
    local_dir: str | Path | None = None,
) -> RecordResult:
    """Build technical identities for a browser form, then use ``record_result``.

    The event identity is a deterministic SHA-256 of the scheduled task and
    explicit attempt facts. Re-submitting the same facts therefore reuses the
    same ID and is rejected as a duplicate; Review Context identity is derived
    deterministically from that attempt ID. No random or hidden identity is
    introduced, and the CLI continues to require its explicit IDs.
    """
    local = _resolve_local_dir(local_dir)
    current = get_today(as_of, local_dir=local)
    planner_output = current.planner_output
    resolved_as_of = planner_output["as_of"]
    today_tasks = planner_output["days"][0]["tasks"]
    matches = [task for task in today_tasks if task.get("task_id") == task_id]
    if len(matches) != 1:
        raise CockpitError("该任务已不属于当前 Today 计划，请刷新后重试。", "task_not_scheduled")
    task = matches[0]
    review_catalog = {item["review_item_id"]: item for item in current.review_items}
    if task.get("task_type") == "new_learning" and task.get("target_kind") == "topic":
        topic_id = task["target_ref"]
    elif task.get("task_type") == "review" and task.get("target_kind") == "review_item":
        item = review_catalog.get(task["target_ref"])
        canonical_ref = item.get("canonical_ref") if isinstance(item, Mapping) else None
        topic_id = canonical_ref.get("topic_id") if isinstance(canonical_ref, Mapping) else None
        if not isinstance(topic_id, str):
            raise CockpitError("当前复习目标无法映射到知识点，已停止记录。", "invalid_review_target")
    else:
        raise CockpitError("当前任务类型不支持综合题记录。", "unsupported_execution_target")

    fact_identity: dict[str, Any] = {
        "task_id": task_id,
        "occurred_at": occurred_at,
        "question": dict(question),
        "topics": [topic_id],
        "correct": correct,
    }
    if error_cause is not None and correct is False:
        fact_identity["error_cause"] = error_cause
    serialized_identity = json.dumps(
        fact_identity, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )
    identity = hashlib.sha256(serialized_identity.encode("utf-8")).hexdigest()
    attempt = {
        "event_id": f"browser-attempt-{identity}",
        "schema_version": PROGRESS_EVENT_SCHEMA_VERSION,
        "event_type": "comprehensive_attempt",
        "occurred_at": occurred_at,
        "question": dict(question),
        "topics": [topic_id],
        "correct": correct,
    }
    if error_cause is not None and correct is False:
        attempt["error_cause"] = error_cause
    review_context_event_id = f"browser-context-{identity}"
    return record_result(
        task_id,
        attempt,
        review_context_event_id,
        as_of=resolved_as_of,
        local_dir=local,
    )


__all__ = [
    "CockpitError",
    "PROJECT_ROOT",
    "RecordResult",
    "TodaySnapshot",
    "get_comprehensive_source_references",
    "get_today",
    "initialize_cockpit",
    "record_browser_attempt",
    "record_result",
]
