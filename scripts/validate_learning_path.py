#!/usr/bin/env python3
"""Validate static Learning Path v0.1 data against the recorded Taxonomy.

The validator is an offline contract check only. It does not feed Planner,
create learning facts, load Prompts, or call an LLM.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path, PurePosixPath
from typing import Any, Mapping

SCHEMA_VERSION = "learning-path/v0.1"
STATUSES = {"exact", "partial", "split", "merge", "unmapped", "non_learning"}
CONFIDENCE = {"high", "medium", "low"}
TOPIC_ID_RE = re.compile(r"^[A-Z0-9_]+(?:\.[A-Z0-9_]+){2}$")
ITEM_ID_RE = re.compile(r"^checkin-(\d{3})$")
FORBIDDEN_PATH_PARTS = ("/vol5/", "/root/", "ruankao-cockpit_base/research")
TOP_LEVEL_KEYS = {
    "schema_version", "path_id", "version", "status", "title", "taxonomy_version",
    "source", "ordering", "items",
}
SOURCE_KEYS = {"type", "archive_name", "archive_size_bytes", "archive_sha256", "description"}
ARCHIVE_NAME = "系统架构设计师打卡.zip"
ARCHIVE_SIZE_BYTES = 175511
ARCHIVE_SHA256 = "d7e8f68374f250dab72f2a08c543cbe9cbd44533fdc8e1e32c1a0d0e67fce17a"
ORDERING_KEYS = {"basis", "date_semantics", "order_semantics"}
ITEM_REQUIRED_KEYS = {
    "item_id", "order", "source_date", "source_file", "source_title", "topic_ids",
    "mapping_status", "mapping_confidence", "mapping_notes", "knowledge_point_titles",
}
ITEM_OPTIONAL_KEYS = {"original_topic_title", "mapping_group_id"}


class LearningPathValidationError(ValueError):
    """Raised when a static Learning Path document violates its contract."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise LearningPathValidationError(message)


def _safe_relative_source_file(value: Any, label: str) -> None:
    require(isinstance(value, str) and bool(value.strip()), f"{label}: source_file must be a non-empty string")
    parsed = PurePosixPath(value)
    require(not value.startswith("/"), f"{label}: absolute source_file is forbidden")
    require("\\" not in value, f"{label}: source_file must use POSIX separators")
    require(".." not in parsed.parts and "." not in parsed.parts, f"{label}: unsafe source_file path")
    require(not any(part in value for part in FORBIDDEN_PATH_PARTS), f"{label}: local/NAS path leaked")


def _check_strings(value: Any, label: str) -> None:
    if isinstance(value, str):
        require(not any(part in value for part in FORBIDDEN_PATH_PARTS), f"{label}: local path leaked")
    elif isinstance(value, Mapping):
        for key, child in value.items():
            _check_strings(child, f"{label}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _check_strings(child, f"{label}[{index}]")


def validate_document(document: Any, taxonomy: Mapping[str, Any]) -> dict[str, Any]:
    require(isinstance(document, Mapping), "Learning Path must be an object")
    require(set(document) == TOP_LEVEL_KEYS, "Learning Path has missing or unsupported top-level fields")
    require(document.get("schema_version") == SCHEMA_VERSION, "unsupported Learning Path schema_version")
    require(isinstance(document.get("path_id"), str) and re.fullmatch(r"[a-z0-9][a-z0-9-]*", document["path_id"]), "invalid path_id")
    require(isinstance(document.get("version"), str) and re.fullmatch(r"\d+\.\d+\.\d+", document["version"]), "invalid path version")
    require(document.get("status") in {"draft", "approved", "deprecated"}, "invalid path status")
    require(isinstance(document.get("title"), str) and bool(document["title"].strip()), "title is required")
    require(isinstance(taxonomy, Mapping), "Taxonomy must be an object")
    require(document.get("taxonomy_version") == taxonomy.get("taxonomy_version"), "Learning Path taxonomy_version does not match Taxonomy")

    source = document.get("source")
    require(isinstance(source, Mapping) and set(source) == SOURCE_KEYS, "source has missing or unsupported fields")
    require(source.get("type") == "user_provided_checkin_archive", "unsupported Learning Path source type")
    require(source.get("archive_name") == ARCHIVE_NAME, "source archive_name does not match audited archive")
    require(source.get("archive_size_bytes") == ARCHIVE_SIZE_BYTES, "source archive_size_bytes does not match audited archive")
    require(source.get("archive_sha256") == ARCHIVE_SHA256, "source archive_sha256 does not match audited archive")
    require(isinstance(source.get("description"), str) and bool(source["description"].strip()), "source description is required")

    ordering = document.get("ordering")
    require(isinstance(ordering, Mapping) and set(ordering) == ORDERING_KEYS, "ordering has missing or unsupported fields")
    for field in ORDERING_KEYS:
        require(isinstance(ordering.get(field), str) and bool(ordering[field].strip()), f"ordering.{field} is required")
    require("provenance_only" in ordering["date_semantics"], "source_date must be explicitly provenance-only")
    require("NON_LEARNING" in ordering["order_semantics"], "order semantics must define NON_LEARNING records")

    nodes = taxonomy.get("nodes")
    require(isinstance(nodes, list), "Taxonomy nodes must be a list")
    active_l3 = {
        node["id"] for node in nodes
        if isinstance(node, Mapping) and node.get("level") == 3 and node.get("status") == "active"
    }
    require(bool(active_l3), "Taxonomy has no active L3 Topics")

    items = document.get("items")
    require(isinstance(items, list) and bool(items), "items must be a non-empty list")
    item_ids: set[str] = set()
    orders: set[int] = set()
    source_files: set[str] = set()
    previous_key: tuple[str, str] | None = None
    topic_source_counts: Counter[str] = Counter()
    confidence_counts: Counter[str] = Counter()
    status_counts: Counter[str] = Counter()
    multi_topic_count = 0
    groups: dict[str, list[Mapping[str, Any]]] = defaultdict(list)

    for index, item in enumerate(items):
        label = f"items[{index}]"
        require(isinstance(item, Mapping), f"{label}: item must be an object")
        keys = set(item)
        require(ITEM_REQUIRED_KEYS <= keys and keys <= ITEM_REQUIRED_KEYS | ITEM_OPTIONAL_KEYS, f"{label}: missing or unsupported fields")
        item_id = item.get("item_id")
        order = item.get("order")
        match = ITEM_ID_RE.fullmatch(item_id) if isinstance(item_id, str) else None
        require(match is not None, f"{label}: invalid item_id")
        require(isinstance(order, int) and not isinstance(order, bool) and order >= 1, f"{label}: order must be a positive integer")
        require(int(match.group(1)) == order, f"{label}: item_id must deterministically match order")
        require(item_id not in item_ids and order not in orders, f"{label}: duplicate item_id or order")
        item_ids.add(item_id)
        orders.add(order)

        source_date = item.get("source_date")
        require(isinstance(source_date, str), f"{label}: source_date must be an ISO date")
        try:
            parsed_date = date.fromisoformat(source_date)
        except ValueError:
            raise LearningPathValidationError(f"{label}: invalid source_date") from None
        require(parsed_date.isoformat() == source_date, f"{label}: source_date must use YYYY-MM-DD")
        source_file = item.get("source_file")
        _safe_relative_source_file(source_file, label)
        require(source_file not in source_files, f"{label}: duplicate source_file")
        source_files.add(source_file)
        ordering_key = (source_date, source_file)
        require(previous_key is None or previous_key <= ordering_key, f"{label}: items are not in deterministic date/file order")
        previous_key = ordering_key
        require(isinstance(item.get("source_title"), str) and bool(item["source_title"].strip()), f"{label}: source_title is required")
        if "original_topic_title" in item:
            require(isinstance(item["original_topic_title"], str) and bool(item["original_topic_title"].strip()), f"{label}: invalid original_topic_title")
        outline = item.get("knowledge_point_titles")
        require(isinstance(outline, list), f"{label}: knowledge_point_titles must be a list")
        require(all(isinstance(title, str) and bool(title.strip()) and len(title) <= 120 for title in outline), f"{label}: invalid knowledge point title")
        notes = item.get("mapping_notes")
        require(isinstance(notes, str) and bool(notes.strip()), f"{label}: mapping_notes is required")

        status = item.get("mapping_status")
        confidence = item.get("mapping_confidence")
        topic_ids = item.get("topic_ids")
        require(isinstance(status, str) and status in STATUSES, f"{label}: unsupported mapping_status")
        require(isinstance(topic_ids, list) and all(isinstance(topic_id, str) for topic_id in topic_ids), f"{label}: topic_ids must be a string list")
        require(len(topic_ids) == len(set(topic_ids)), f"{label}: topic_ids must be unique")
        for topic_id in topic_ids:
            require(isinstance(topic_id, str) and TOPIC_ID_RE.fullmatch(topic_id), f"{label}: invalid canonical L3 Topic ID {topic_id!r}")
            require(topic_id in active_l3, f"{label}: Topic is not active L3 in recorded Taxonomy: {topic_id}")
            topic_source_counts[topic_id] += 1
        if len(topic_ids) > 1:
            multi_topic_count += 1

        if status == "non_learning":
            require(confidence is None and not topic_ids and not outline, f"{label}: NON_LEARNING must have null confidence, no topics, and no outline")
        else:
            require(confidence in CONFIDENCE, f"{label}: mapping confidence is required")
            confidence_counts[confidence] += 1
            if status == "unmapped":
                require(not topic_ids and confidence == "low", f"{label}: UNMAPPED requires no topics and low confidence")
            elif status == "split":
                require(len(topic_ids) >= 2, f"{label}: SPLIT requires at least two Topic IDs")
            elif status in {"exact", "partial", "merge"}:
                require(len(topic_ids) == 1, f"{label}: {status.upper()} requires exactly one Topic ID")
            if status == "merge":
                require(isinstance(item.get("mapping_group_id"), str), f"{label}: MERGE requires mapping_group_id")
        group_id = item.get("mapping_group_id")
        if group_id is not None:
            require(isinstance(group_id, str) and re.fullmatch(r"[a-z0-9][a-z0-9-]*", group_id), f"{label}: invalid mapping_group_id")
            groups[group_id].append(item)
        status_counts[status] += 1
        _check_strings(item, label)

    require(orders == set(range(1, len(items) + 1)), "orders must be contiguous and start at 1")
    for group_id, group_items in groups.items():
        require(len(group_items) >= 2, f"mapping group {group_id!r} must contain at least two items")
        common_topics = set(group_items[0]["topic_ids"])
        for grouped_item in group_items[1:]:
            common_topics.intersection_update(grouped_item["topic_ids"])
        require(bool(common_topics), f"mapping group {group_id!r} must share at least one Topic ID")

    _check_strings(document, "Learning Path")
    covered = set(topic_source_counts)
    return {
        "source_items": len(items),
        "learning_items": sum(count for status, count in status_counts.items() if status != "non_learning"),
        "non_learning_items": status_counts["non_learning"],
        "mapping_status": dict(sorted(status_counts.items())),
        "confidence": dict(sorted(confidence_counts.items())),
        "mapped_unique_l3_topics": len(covered),
        "active_l3_topics": len(active_l3),
        "uncovered_topic_ids": sorted(active_l3 - covered),
        "duplicate_covered_topic_ids": sorted(topic for topic, count in topic_source_counts.items() if count > 1),
        "source_items_with_multiple_topic_mappings": multi_topic_count,
    }


def validate_learning_path(root: Path) -> dict[str, Any]:
    try:
        document = json.loads((root / "data/learning-paths/system-architect-checkin-v1.json").read_text(encoding="utf-8"))
        schema = json.loads((root / "data/learning-paths/schema-v0.1.json").read_text(encoding="utf-8"))
        taxonomy = json.loads((root / "taxonomy/taxonomy.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise LearningPathValidationError(f"cannot read Learning Path, schema, or Taxonomy JSON: {exc}") from exc
    require(schema.get("$schema") == "https://json-schema.org/draft/2020-12/schema", "unsupported JSON Schema dialect")
    require(schema.get("properties", {}).get("schema_version", {}).get("const") == SCHEMA_VERSION, "schema file does not describe Learning Path v0.1")
    return validate_document(document, taxonomy)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    try:
        summary = validate_learning_path(args.root.resolve())
        print("PASS Learning Path v0.1 validation (offline static data; no Planner integration)")
        print(f"  source items: {summary['source_items']}; learning: {summary['learning_items']}; non-learning: {summary['non_learning_items']}")
        print("  mapping status: " + ", ".join(f"{key}={value}" for key, value in summary["mapping_status"].items()))
        print("  confidence: " + ", ".join(f"{key}={value}" for key, value in summary["confidence"].items()))
        print(f"  Taxonomy coverage: {summary['mapped_unique_l3_topics']}/{summary['active_l3_topics']} L3 topics")
        print(f"  uncovered: {len(summary['uncovered_topic_ids'])}; duplicate covered: {len(summary['duplicate_covered_topic_ids'])}")
        print(f"  source items with multiple topic mappings: {summary['source_items_with_multiple_topic_mappings']}")
        return 0
    except LearningPathValidationError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
