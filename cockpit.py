#!/usr/bin/env python3
"""Minimal local CLI for the deterministic ruankao-cockpit learning loop."""
from __future__ import annotations

import argparse
from datetime import datetime
import json
import os
from pathlib import Path
import sys
import tempfile
from typing import Any, Iterable, Mapping

from engine.execution import record_task_result
from engine.planner import plan_today
from engine.progress import replay as progress_replay
from engine.review.replay import replay as review_replay
from engine.rules.review_policy_v01 import resolve_timezone


PROJECT_ROOT = Path(__file__).resolve().parent
LOCAL_DIR_NAME = ".local"
CONFIG_SCHEMA_VERSION = "user-configuration/v0.1"
TRANSACTION_SCHEMA_VERSION = "cockpit-record-transaction/v0.1"


class CockpitError(ValueError):
    """A user-facing local storage or command error."""


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
        raise CockpitError(f"Invalid JSON in {path}: {exc}") from exc


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise CockpitError(f"Required local facts file is missing: {path}") from None
    events: list[dict[str, Any]] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            raise CockpitError(f"{path}:{line_number}: blank JSONL rows are not allowed")
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise CockpitError(f"{path}:{line_number}: invalid JSON: {exc}") from exc
        if not isinstance(value, dict):
            raise CockpitError(f"{path}:{line_number}: each JSONL row must be an object")
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
        # Keep each serialized event intact and newline-terminated. The local
        # files are append-only; no existing fact row is edited in place.
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


def _local_dir() -> Path:
    return Path.cwd() / LOCAL_DIR_NAME


def _ensure_initialized(local: Path) -> None:
    if not local.is_dir():
        if local.exists():
            raise CockpitError(f"{local} exists but is not a directory")
        raise CockpitError("Not initialized. Run `python3 cockpit.py init` first.")
    for name in ("config.json", "progress-events.jsonl", "review-events.jsonl", "review-items.json"):
        if not (local / name).is_file():
            raise CockpitError(f"Local data is incomplete: missing {local / name}")


def _load_resources() -> tuple[dict[str, Any], dict[str, Any]]:
    taxonomy = _read_json(PROJECT_ROOT / "taxonomy" / "taxonomy.json")
    capabilities = _read_json(PROJECT_ROOT / "taxonomy" / "capabilities.json")
    if not isinstance(taxonomy, dict) or not isinstance(capabilities, dict):
        raise CockpitError("Taxonomy and capabilities documents must be JSON objects")
    return taxonomy, capabilities


def _load_user_data(local: Path) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    _ensure_initialized(local)
    config = _read_json(local / "config.json")
    progress_events = _read_jsonl(local / "progress-events.jsonl")
    review_events = _read_jsonl(local / "review-events.jsonl")
    review_items = _read_json(local / "review-items.json")
    if not isinstance(config, dict):
        raise CockpitError("config.json must contain an object")
    if not isinstance(review_items, list) or any(not isinstance(item, dict) for item in review_items):
        raise CockpitError("review-items.json must contain an array of item objects")
    return config, progress_events, review_events, review_items


def _resolve_as_of(as_of: str | None, timezone_name: str) -> str:
    zone = resolve_timezone(timezone_name)
    if as_of is None:
        # The CLI is the I/O boundary; engine and replay functions receive an
        # explicit timezone-aware instant and never consult the wall clock.
        instant = datetime.now(zone)
    else:
        normalized = as_of[:-1] + "+00:00" if as_of.endswith("Z") else as_of
        try:
            instant = datetime.fromisoformat(normalized)
        except ValueError as exc:
            raise CockpitError(f"--as-of must be an ISO 8601 timestamp: {as_of!r}") from exc
        if instant.tzinfo is None or instant.utcoffset() is None:
            raise CockpitError("--as-of must include a timezone offset")
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


def _topic_names(taxonomy: Mapping[str, Any]) -> dict[str, str]:
    return {
        node["id"]: node["name"]
        for node in taxonomy.get("nodes", [])
        if isinstance(node, Mapping) and isinstance(node.get("id"), str) and isinstance(node.get("name"), str)
    }


def _format_today(
    planner_output: Mapping[str, Any],
    review_state: Mapping[str, Any],
    review_items: list[dict[str, Any]],
    taxonomy: Mapping[str, Any],
) -> str:
    day = planner_output["days"][0]
    review_catalog = {item["review_item_id"]: item for item in review_items}
    names = _topic_names(taxonomy)
    lines = [
        f"Today · {day['local_date']}",
        f"as_of: {planner_output['as_of']}",
        f"timezone: {planner_output['timezone']}",
        f"Available: {day['capacity_minutes']} min",
        f"Planned: {day['planned_minutes']} min",
        f"Remaining: {day['remaining_minutes']} min",
    ]
    tasks = day["tasks"]
    if not tasks:
        lines.append("Today has no scheduled tasks.")
        return "\n".join(lines)

    for index, task in enumerate(tasks, start=1):
        task_type = task["task_type"]
        if task_type == "review":
            label = "REVIEW"
            item = review_catalog.get(task["target_ref"], {})
            topic_id = item.get("canonical_ref", {}).get("topic_id")
            reference = topic_id or task["target_ref"]
            status = review_state["items"].get(task["target_ref"], {}).get("review_status")
            status_text = {"overdue": "overdue", "due": "due today"}.get(status)
        else:
            label = "NEW"
            reference = task["target_ref"]
            status_text = "next unlearned topic"
        display_name = names.get(reference)
        title = f"{reference} · {display_name}" if display_name else reference
        detail = f"{task['planned_minutes']} min"
        if status_text:
            detail += f" · {status_text}"
        lines.extend([
            f"{index}. [{label}] {title}",
            f"   {detail}",
            f"   task: {task['task_id']}",
        ])
    return "\n".join(lines)


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
            raise CockpitError(f"Duplicate {label} event ID: {event_id}")


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
    # Both replay layers are run before persistence. Any schema, provenance,
    # topic mismatch, duplicate or policy validation failure leaves user files
    # untouched.
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
                raise CockpitError(f"Pending transaction conflicts with existing {label} event {event_id!r}")
            continue  # Only resumes this exact, already-staged transaction.
        append.append(event)
        merged.append(event)
        if isinstance(event_id, str):
            indexed[event_id] = event
    return merged, append


def _commit_transaction(local: Path, transaction: Mapping[str, Any]) -> None:
    if transaction.get("schema_version") != TRANSACTION_SCHEMA_VERSION:
        raise CockpitError("Unsupported pending record transaction schema")
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
        raise CockpitError("Pending record transaction is malformed")

    merged_progress, append_progress = _merge_recovery_events(progress_events, added_progress, "Progress")
    merged_review, append_review = _merge_recovery_events(review_events, added_review, "Review")
    if current_items == target_items:
        pass
    elif current_items == base_items:
        pass
    else:
        raise CockpitError("Pending transaction conflicts with review-items.json; no local data was changed")

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

    # A small durable staging record allows the next CLI invocation to finish
    # an interrupted multi-file write. This is recovery, not an ACID database.
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
        raise CockpitError(f"Pending transaction is not an object: {pending}")
    _commit_transaction(local, transaction)
    pending.unlink()
    _fsync_directory(pending.parent)


def _init_command() -> int:
    local = _local_dir()
    if local.exists():
        if local.is_dir():
            print(f"Already initialized: {local} (existing data was not changed)")
            return 0
        raise CockpitError(f"{local} exists but is not a directory")

    try:
        local.mkdir()
    except FileExistsError:
        print(f"Already initialized: {local} (existing data was not changed)")
        return 0

    try:
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
    except BaseException:
        # Leave any partial initialization visible rather than recursively
        # deleting user data. The next run explains which expected file is absent.
        raise
    print(f"Initialized local study data: {local}")
    return 0


def _today_command(as_of_arg: str | None) -> int:
    local = _local_dir()
    _ensure_initialized(local)
    _recover_pending(local)
    config, _, _, _ = _load_user_data(local)
    as_of = _resolve_as_of(as_of_arg, config.get("timezone"))
    taxonomy, capabilities = _load_resources()
    planner_output, _, review_state, review_items = _make_plan(local, as_of, taxonomy, capabilities)
    print(_format_today(planner_output, review_state, review_items, taxonomy))
    return 0


def _record_command(args: argparse.Namespace) -> int:
    local = _local_dir()
    _ensure_initialized(local)
    _recover_pending(local)
    config, progress_events, review_events, review_items = _load_user_data(local)
    attempt = _read_json(args.attempt)
    if not isinstance(attempt, dict):
        raise CockpitError("--attempt must point to a JSON object")
    attempt_id = attempt.get("event_id")
    if isinstance(attempt_id, str) and attempt_id in _event_id_index(progress_events):
        raise CockpitError(f"Duplicate progress event ID: {attempt_id}")
    if args.review_context_event_id in _event_id_index(review_events):
        raise CockpitError(f"Duplicate review event ID: {args.review_context_event_id}")

    as_of = _resolve_as_of(args.as_of, config.get("timezone"))
    taxonomy, capabilities = _load_resources()
    planner_output, _, _, _ = _make_plan(local, as_of, taxonomy, capabilities)
    result = record_task_result(
        planner_output,
        args.task_id,
        {
            "progress_event": attempt,
            "review_context_event_id": args.review_context_event_id,
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
        as_of=as_of,
        timezone_name=config.get("timezone"),
    )

    pending_dir = local / "pending"
    pending = pending_dir / "record.json"
    if pending.exists():
        raise CockpitError(f"A pending record transaction already exists: {pending}")
    transaction = {
        "schema_version": TRANSACTION_SCHEMA_VERSION,
        "as_of": as_of,
        "progress_events": added_progress,
        "review_events": added_review,
        "base_review_items": review_items,
        "review_items": target_items,
    }
    _atomic_write_json(pending, transaction)
    _recover_pending(local)

    print("Recorded:")
    print(f"- {len(added_progress)} Progress Event{'s' if len(added_progress) != 1 else ''}")
    print(f"- {len(added_items)} Review Item{'s' if len(added_items) != 1 else ''}")
    print(f"- {len(added_review)} Review Context{'s' if len(added_review) != 1 else ''}")
    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python3 cockpit.py", description="Local deterministic study cockpit")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("init", help="create local user data without overwriting existing data")
    today = commands.add_parser("today", help="replay local facts and show today's plan")
    today.add_argument("--as-of", help="explicit timezone-aware ISO 8601 instant")
    record = commands.add_parser("record", help="record a real comprehensive attempt for a scheduled task")
    record.add_argument("--task-id", required=True, help="task ID from today's plan")
    record.add_argument("--attempt", required=True, type=Path, help="JSON progress-event/v0.1 comprehensive_attempt")
    record.add_argument("--review-context-event-id", required=True, help="explicit stable Review Context event ID")
    record.add_argument("--as-of", help="explicit timezone-aware instant used to validate today's plan and replay")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "init":
            return _init_command()
        if args.command == "today":
            return _today_command(args.as_of)
        if args.command == "record":
            return _record_command(args)
        parser.error(f"unknown command: {args.command}")
    except (CockpitError, OSError, ValueError, KeyError, TypeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
