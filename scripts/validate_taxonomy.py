#!/usr/bin/env python3
"""Validate the v0.1 taxonomy, provenance mappings, capabilities, and samples.

This deliberately uses only the Python standard library because the repository
stores its machine-readable contracts as JSON.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

CONFIDENCE = {"high", "medium", "low"}
STATUS = {"candidate", "reviewed", "confirmed", "rejected"}
ID_RE = re.compile(r"^[A-Z][A-Z0-9_]*(?:\.[A-Z0-9_]+)*$")
CAPABILITY_ID_RE = re.compile(r"^CASE(?:\.[A-Z0-9_]+)+$")
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
FORBIDDEN_CANONICAL_SEGMENTS = {"OTHER", "UNKNOWN", "MISC", "UNCLASSIFIED"}
FORBIDDEN_CONTENT_KEYS = {
    "stem",
    "prompt",
    "options",
    "answer",
    "analysis",
    "reference_answer",
    "ocr_text",
    "full_text",
}
FORBIDDEN_PATH_PARTS = ("/vol5/", "/root/pi-cwd", "ruankao-cockpit_base/research")


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


def check_relative_path(value: Any, label: str) -> None:
    require(isinstance(value, str) and value, f"{label}: source_path must be a non-empty string")
    require(not value.startswith("/"), f"{label}: absolute source_path is forbidden: {value}")
    require(".." not in Path(value).parts, f"{label}: parent traversal is forbidden: {value}")
    require(not any(part in value for part in FORBIDDEN_PATH_PARTS), f"{label}: local/NAS path leaked: {value}")


def check_provenance(obj: dict[str, Any], known_sources: dict[str, dict[str, Any]], label: str) -> None:
    source_id = obj.get("source_id")
    commit = obj.get("source_commit")
    require(source_id in known_sources, f"{label}: unknown source_id {source_id!r}")
    require(isinstance(commit, str) and COMMIT_RE.fullmatch(commit), f"{label}: invalid source_commit")
    require(commit == known_sources[source_id]["source_commit"], f"{label}: source_commit does not match source catalog")
    check_relative_path(obj.get("source_path"), label)


def walk_strings(value: Any, label: str) -> None:
    if isinstance(value, str):
        require(not any(part in value for part in FORBIDDEN_PATH_PARTS), f"{label}: local path leaked in string")
    elif isinstance(value, dict):
        for key, child in value.items():
            walk_strings(child, f"{label}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            walk_strings(child, f"{label}[{index}]")


def validate_taxonomy(root: Path) -> tuple[set[str], dict[str, int]]:
    data = load_json(root / "taxonomy/taxonomy.json")
    require(data.get("taxonomy_version") == "0.1", "taxonomy: taxonomy_version must be 0.1")
    nodes = data.get("nodes")
    require(isinstance(nodes, list) and nodes, "taxonomy: nodes must be a non-empty list")
    ids: set[str] = set()
    by_id: dict[str, dict[str, Any]] = {}
    for index, node in enumerate(nodes):
        label = f"taxonomy.nodes[{index}]"
        require(isinstance(node, dict), f"{label}: node must be an object")
        node_id = node.get("id")
        require(isinstance(node_id, str) and ID_RE.fullmatch(node_id), f"{label}: invalid id {node_id!r}")
        require(node_id not in ids, f"{label}: duplicate id {node_id}")
        ids.add(node_id)
        by_id[node_id] = node
        level = node.get("level")
        require(level in {1, 2, 3}, f"{label}: level must be 1, 2 or 3")
        require(len(node_id.split(".")) == level, f"{label}: id segments do not match level")
        require(isinstance(node.get("name"), str) and node["name"], f"{label}: name is required")
        require(node.get("status") in {"active", "deprecated", "proposed"}, f"{label}: invalid status")
        parent = node.get("parent_id")
        if level == 1:
            require(parent is None, f"{label}: L1 parent_id must be null")
        else:
            require(isinstance(parent, str) and parent in by_id or parent in ids, f"{label}: missing parent {parent!r}")
    for node_id, node in by_id.items():
        if node["level"] > 1:
            parent = by_id[node["parent_id"]]
            require(parent["level"] == node["level"] - 1, f"taxonomy: invalid parent level for {node_id}")
    for node_id in ids:
        seen: set[str] = set()
        current = node_id
        while current is not None:
            require(current not in seen, f"taxonomy: cycle detected at {node_id}")
            seen.add(current)
            current = by_id[current].get("parent_id")
    require(
        not any(segment in FORBIDDEN_CANONICAL_SEGMENTS for node_id in ids for segment in node_id.split(".")),
        "taxonomy: canonical IDs must not use OTHER, UNKNOWN, MISC, or UNCLASSIFIED",
    )
    counts = {f"L{level}": sum(1 for node in nodes if node["level"] == level) for level in (1, 2, 3)}
    return ids, counts


def validate_sources_and_mappings(root: Path, topic_ids: set[str]) -> tuple[dict[str, dict[str, Any]], int, int]:
    mapping_data = load_json(root / "taxonomy/source-mappings.json")
    require(mapping_data.get("taxonomy_version") == "0.1", "source mappings: taxonomy_version must be 0.1")
    sources = mapping_data.get("sources")
    mappings = mapping_data.get("mappings")
    require(isinstance(sources, list) and sources, "source mappings: sources must be non-empty")
    require(isinstance(mappings, list) and mappings, "source mappings: mappings must be non-empty")
    known: dict[str, dict[str, Any]] = {}
    for index, source in enumerate(sources):
        label = f"source-mappings.sources[{index}]"
        require(isinstance(source, dict), f"{label}: source must be an object")
        source_id = source.get("source_id")
        require(isinstance(source_id, str) and source_id not in known, f"{label}: duplicate/invalid source_id")
        commit = source.get("source_commit")
        require(isinstance(commit, str) and COMMIT_RE.fullmatch(commit), f"{label}: invalid source_commit")
        require(source.get("repository"), f"{label}: repository is required")
        known[source_id] = source
    for index, mapping in enumerate(mappings):
        label = f"source-mappings.mappings[{index}]"
        require(isinstance(mapping, dict), f"{label}: mapping must be an object")
        check_provenance(mapping, known, label)
        topic_list = mapping.get("canonical_topic_ids")
        require(isinstance(topic_list, list) and topic_list, f"{label}: canonical_topic_ids must be non-empty")
        require(len(topic_list) == len(set(topic_list)), f"{label}: duplicate canonical topic")
        require(all(topic in topic_ids for topic in topic_list), f"{label}: unknown canonical topic")
        require(mapping.get("confidence") in CONFIDENCE, f"{label}: invalid confidence")
        require(mapping.get("source_value"), f"{label}: source_value is required")
    unresolved = load_json(root / "taxonomy/unresolved-mappings.json")
    require(unresolved.get("taxonomy_version") == "0.1", "unresolved mappings: taxonomy_version must be 0.1")
    unresolved_items = unresolved.get("unresolved")
    require(isinstance(unresolved_items, list) and unresolved_items, "unresolved mappings: list must be non-empty")
    for index, item in enumerate(unresolved_items):
        label = f"unresolved[{index}]"
        require(isinstance(item, dict), f"{label}: item must be an object")
        check_provenance(item, known, label)
        require(item.get("source_value"), f"{label}: source_value is required")
        require(item.get("reason"), f"{label}: reason is required")
        candidates = item.get("candidate_topics")
        require(isinstance(candidates, list), f"{label}: candidate_topics must be a list")
        require(all(topic in topic_ids for topic in candidates), f"{label}: unknown candidate topic")
        require(isinstance(item.get("evidence"), list) and item["evidence"], f"{label}: evidence is required")
    return known, len(mappings), len(unresolved_items)


def validate_aliases(root: Path, topic_ids: set[str], known_sources: dict[str, dict[str, Any]]) -> int:
    data = load_json(root / "taxonomy/aliases.json")
    require(data.get("taxonomy_version") == "0.1", "aliases: taxonomy_version must be 0.1")
    aliases = data.get("aliases")
    groups = data.get("collision_groups")
    require(isinstance(aliases, list) and aliases, "aliases: aliases must be non-empty")
    require(isinstance(groups, list), "aliases: collision_groups must be a list")
    keys: set[tuple[str, str, str, str]] = set()
    group_map: dict[str, set[str]] = {}
    for index, group in enumerate(groups):
        label = f"aliases.collision_groups[{index}]"
        group_id = group.get("id")
        require(isinstance(group_id, str) and group_id not in group_map, f"{label}: invalid/duplicate id")
        topics = group.get("topic_ids")
        require(isinstance(topics, list) and topics and all(topic in topic_ids for topic in topics), f"{label}: invalid topic_ids")
        group_map[group_id] = set(topics)
    for index, alias in enumerate(aliases):
        label = f"aliases[{index}]"
        require(isinstance(alias, dict), f"{label}: alias must be an object")
        check_provenance(alias, known_sources, label)
        topic = alias.get("canonical_topic_id")
        require(topic in topic_ids, f"{label}: unknown canonical topic {topic}")
        require(isinstance(alias.get("alias"), str) and alias["alias"].strip(), f"{label}: alias is required")
        require(alias.get("confidence") in CONFIDENCE, f"{label}: invalid confidence")
        key = (alias["alias"], topic, alias["source_id"], alias["source_value"])
        require(key not in keys, f"{label}: duplicate alias record")
        keys.add(key)
        group_id = alias.get("collision_group_id")
        if group_id is not None:
            require(group_id in group_map, f"{label}: unknown collision group")
            require(topic in group_map[group_id], f"{label}: topic not in collision group")
    for group_id, topics in group_map.items():
        actual = {alias["canonical_topic_id"] for alias in aliases if alias.get("collision_group_id") == group_id}
        require(actual == topics, f"aliases: collision group {group_id} does not match alias records")
    return len(aliases)


def validate_capabilities(root: Path, known_sources: dict[str, dict[str, Any]]) -> set[str]:
    data = load_json(root / "taxonomy/capabilities.json")
    require(data.get("taxonomy_version") == "0.1", "capabilities: taxonomy_version must be 0.1")
    capabilities = data.get("capabilities")
    require(isinstance(capabilities, list) and capabilities, "capabilities: list must be non-empty")
    ids: set[str] = set()
    for index, capability in enumerate(capabilities):
        label = f"capabilities[{index}]"
        capability_id = capability.get("id")
        require(isinstance(capability_id, str) and CAPABILITY_ID_RE.fullmatch(capability_id), f"{label}: invalid id")
        require(capability_id not in ids, f"{label}: duplicate id")
        ids.add(capability_id)
        require(isinstance(capability.get("name"), str) and capability["name"], f"{label}: name is required")
        require(isinstance(capability.get("description"), str) and capability["description"], f"{label}: description is required")
        for evidence_index, evidence in enumerate(capability.get("evidence", [])):
            check_provenance(evidence, known_sources, f"{label}.evidence[{evidence_index}]")
            require(evidence.get("source_value"), f"{label}.evidence[{evidence_index}]: source_value required")
    return ids


def validate_sample(root: Path, path: Path, expected_type: str, topic_ids: set[str], capability_ids: set[str], known_sources: dict[str, dict[str, Any]], seen_record_ids: set[str]) -> tuple[int, int]:
    data = load_json(path)
    label = path.relative_to(root).as_posix()
    require(data.get("schema_version") == "golden-set/v0.1", f"{label}: wrong schema_version")
    require(data.get("taxonomy_version") == "0.1", f"{label}: wrong taxonomy_version")
    require(data.get("question_type") == expected_type, f"{label}: wrong question_type")
    records = data.get("records")
    require(isinstance(records, list) and records, f"{label}: records must be a non-empty list")
    multi_topic = 0
    for index, record in enumerate(records):
        record_label = f"{label}.records[{index}]"
        require(isinstance(record, dict), f"{record_label}: record must be an object")
        record_id = record.get("id")
        require(isinstance(record_id, str) and record_id.strip() and record_id not in seen_record_ids, f"{record_label}: duplicate/invalid id")
        seen_record_ids.add(record_id)
        require(record.get("question_type") == expected_type, f"{record_label}: wrong record question_type")
        source = record.get("source")
        require(isinstance(source, dict), f"{record_label}: source is required")
        check_provenance(source, known_sources, record_label + ".source")
        require(isinstance(source.get("source_question_id"), str) and source["source_question_id"].strip(), f"{record_label}: source_question_id is required")
        if expected_type == "case":
            require(source.get("case_id") and source.get("sub_question_id"), f"{record_label}: case source needs case_id/sub_question_id")
        identification = record.get("identification", {})
        if identification:
            summary = identification.get("summary")
            if summary is not None:
                require(isinstance(summary, str) and len(summary) <= 80, f"{record_label}: summary is too long")
        topics = record.get("topics")
        caps = record.get("capabilities")
        require(isinstance(topics, list) and topics, f"{record_label}: at least one topic is required")
        require(isinstance(caps, list), f"{record_label}: topics/capabilities must be lists")
        if expected_type == "case":
            require(caps, f"{record_label}: case records require at least one capability")
        if len(topics) > 1:
            multi_topic += 1
        topic_seen: set[str] = set()
        for ref_index, ref in enumerate(topics):
            ref_label = f"{record_label}.topics[{ref_index}]"
            topic = ref.get("topic_id") if isinstance(ref, dict) else None
            require(topic in topic_ids, f"{ref_label}: unknown topic {topic}")
            require(topic not in topic_seen, f"{ref_label}: duplicate topic")
            topic_seen.add(topic)
            require(ref.get("confidence") in CONFIDENCE, f"{ref_label}: invalid confidence")
        cap_seen: set[str] = set()
        for ref_index, ref in enumerate(caps):
            ref_label = f"{record_label}.capabilities[{ref_index}]"
            capability = ref.get("capability_id") if isinstance(ref, dict) else None
            require(capability in capability_ids, f"{ref_label}: unknown capability {capability}")
            require(capability not in cap_seen, f"{ref_label}: duplicate capability")
            cap_seen.add(capability)
            require(ref.get("confidence") in CONFIDENCE, f"{ref_label}: invalid confidence")
        if expected_type == "comprehensive":
            require(not caps, f"{record_label}: comprehensive capabilities must be empty in v0.1")
        annotation = record.get("annotation")
        require(isinstance(annotation, dict), f"{record_label}: annotation is required")
        require(annotation.get("status") in STATUS, f"{record_label}: invalid review status")
        require(annotation.get("note"), f"{record_label}: annotation note is required")
        if annotation.get("status") == "confirmed":
            require(annotation.get("annotator") == "human", f"{record_label}: confirmed records require human annotator")
        walk_strings(record, record_label)
        # Explicitly reject full-text-like keys even if a future nested object is added.
        def reject_keys(value: Any, where: str) -> None:
            if isinstance(value, dict):
                for key, child in value.items():
                    require(key not in FORBIDDEN_CONTENT_KEYS, f"{where}: disallowed full-content key {key}")
                    reject_keys(child, f"{where}.{key}")
            elif isinstance(value, list):
                for child_index, child in enumerate(value):
                    reject_keys(child, f"{where}[{child_index}]")
        reject_keys(record, record_label)
    return len(records), multi_topic


def collect_golden_statistics(root: Path, taxonomy_nodes: list[dict[str, Any]]) -> dict[str, Any]:
    """Collect diagnostic coverage without turning coverage into a validation gate."""
    records: list[dict[str, Any]] = []
    source_counts: Counter[str] = Counter()
    status_counts: Counter[str] = Counter()
    confidence_counts: Counter[str] = Counter()
    multi_topic_count = 0
    multi_capability_count = 0
    capability_ids: set[str] = set()
    nodes = {node["id"]: node for node in taxonomy_nodes}
    covered_by_level: dict[int, set[str]] = {1: set(), 2: set(), 3: set()}

    def mark_topic(topic_id: str) -> None:
        current: str | None = topic_id
        while current is not None:
            node = nodes[current]
            covered_by_level[node["level"]].add(current)
            current = node.get("parent_id")

    for filename in ("comprehensive.sample.json", "case.sample.json"):
        data = load_json(root / "data/golden-set" / filename)
        records.extend(data["records"])

    for record in records:
        source_counts[record["source"]["source_id"]] += 1
        status_counts[record["annotation"]["status"]] += 1
        if len(record["topics"]) > 1:
            multi_topic_count += 1
        if len(record["capabilities"]) > 1:
            multi_capability_count += 1
        for reference in record["topics"]:
            mark_topic(reference["topic_id"])
            confidence_counts[reference["confidence"]] += 1
        for reference in record["capabilities"]:
            capability_ids.add(reference["capability_id"])
            confidence_counts[reference["confidence"]] += 1

    return {
        "total": len(records),
        "comprehensive": sum(record["question_type"] == "comprehensive" for record in records),
        "case": sum(record["question_type"] == "case" for record in records),
        "coverage": {f"L{level}": len(covered_by_level[level]) for level in (1, 2, 3)},
        "taxonomy_totals": {f"L{level}": sum(node["level"] == level for node in taxonomy_nodes) for level in (1, 2, 3)},
        "capability_coverage": len(capability_ids),
        "status": dict(sorted(status_counts.items())),
        "confidence": dict(sorted(confidence_counts.items())),
        "sources": dict(sorted(source_counts.items())),
        "multi_topic": multi_topic_count,
        "multi_capability": multi_capability_count,
        "unresolved": len(load_json(root / "taxonomy/unresolved-mappings.json")["unresolved"]),
    }


def format_counter(values: dict[str, int]) -> str:
    return ", ".join(f"{key}={value}" for key, value in values.items()) or "none"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        topic_ids, counts = validate_taxonomy(root)
        taxonomy_data = load_json(root / "taxonomy/taxonomy.json")
        known_sources, mapping_count, unresolved_count = validate_sources_and_mappings(root, topic_ids)
        alias_count = validate_aliases(root, topic_ids, known_sources)
        capability_ids = validate_capabilities(root, known_sources)
        record_ids: set[str] = set()
        comprehensive_count, comprehensive_multi = validate_sample(root, root / "data/golden-set/comprehensive.sample.json", "comprehensive", topic_ids, capability_ids, known_sources, record_ids)
        case_count, case_multi = validate_sample(root, root / "data/golden-set/case.sample.json", "case", topic_ids, capability_ids, known_sources, record_ids)
        statistics = collect_golden_statistics(root, taxonomy_data["nodes"])
        walk_strings(load_json(root / "taxonomy/taxonomy.json"), "taxonomy")
        print("PASS taxonomy schema validation")
        print(f"  topics: {len(topic_ids)} ({counts['L1']} L1 / {counts['L2']} L2 / {counts['L3']} L3)")
        print(f"  aliases: {alias_count}")
        print(f"  source mappings: {mapping_count}; unresolved: {unresolved_count}")
        print(f"  capabilities: {len(capability_ids)}")
        print(f"  comprehensive sample: {comprehensive_count}; multi-topic: {comprehensive_multi}")
        print(f"  case sample: {case_count}; multi-topic: {case_multi}")
        print("PASS mapping reference validation")
        print("Golden Set coverage diagnostics (not a hard gate)")
        print(f"  total: {statistics['total']}; comprehensive: {statistics['comprehensive']}; case: {statistics['case']}")
        for level in ("L1", "L2", "L3"):
            print(f"  {level} coverage: {statistics['coverage'][level]}/{statistics['taxonomy_totals'][level]}")
        print(f"  capability coverage: {statistics['capability_coverage']}/{len(capability_ids)}")
        print(f"  review status: {format_counter(statistics['status'])}")
        print(f"  confidence: {format_counter(statistics['confidence'])}")
        print(f"  sources: {format_counter(statistics['sources'])}")
        print(f"  multi-topic records: {statistics['multi_topic']}; multi-capability case records: {statistics['multi_capability']}")
        print(f"  unresolved mappings: {statistics['unresolved']}")
        print("PASS golden-set sample validation")
        print("PASS duplicate ID validation")
        print("PASS parent relationship validation")
        return 0
    except ValidationError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
