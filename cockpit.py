#!/usr/bin/env python3
"""Minimal CLI adapter for the shared local Cockpit application service."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping

from cockpit_service import (
    CockpitError,
    TodaySnapshot,
    get_today,
    initialize_cockpit,
    record_result,
)


def _topic_names(taxonomy: Mapping[str, Any]) -> dict[str, str]:
    return {
        node["id"]: node["name"]
        for node in taxonomy.get("nodes", [])
        if isinstance(node, Mapping) and isinstance(node.get("id"), str) and isinstance(node.get("name"), str)
    }


def _format_today(snapshot: TodaySnapshot) -> str:
    planner_output = snapshot.planner_output
    day = planner_output["days"][0]
    review_catalog = {item["review_item_id"]: item for item in snapshot.review_items}
    names = _topic_names(snapshot.taxonomy)
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
        if task["task_type"] == "review":
            label = "REVIEW"
            item = review_catalog.get(task["target_ref"], {})
            topic_id = item.get("canonical_ref", {}).get("topic_id")
            reference = topic_id or task["target_ref"]
            status = snapshot.review_state["items"].get(task["target_ref"], {}).get("review_status")
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


def _read_attempt(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise CockpitError(f"Attempt file does not exist: {path}", "invalid_attempt") from None
    except json.JSONDecodeError as exc:
        raise CockpitError(f"Invalid attempt JSON in {path}: {exc}", "invalid_attempt") from exc
    if not isinstance(value, dict):
        raise CockpitError("--attempt must point to a JSON object", "invalid_attempt")
    return value


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
            if initialize_cockpit():
                print(f"Initialized local study data: {Path.cwd() / '.local'}")
            else:
                print(f"Already initialized: {Path.cwd() / '.local'} (existing data was not changed)")
            return 0
        if args.command == "today":
            print(_format_today(get_today(args.as_of)))
            return 0
        if args.command == "record":
            result = record_result(
                args.task_id,
                _read_attempt(args.attempt),
                args.review_context_event_id,
                as_of=args.as_of,
            )
            print("Recorded:")
            print(f"- {result.progress_event_count} Progress Event{'s' if result.progress_event_count != 1 else ''}")
            print(f"- {result.review_item_count} Review Item{'s' if result.review_item_count != 1 else ''}")
            print(f"- {result.review_context_count} Review Context{'s' if result.review_context_count != 1 else ''}")
            return 0
        parser.error(f"unknown command: {args.command}")
    except (CockpitError, OSError, ValueError, KeyError, TypeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
