#!/usr/bin/env python3
"""Validate static check-in Learning Units against the draft Learning Path.

This is an offline content-artifact validator. It does not load or alter runtime
contracts, Planner, Progress, Review, or Taxonomy behavior.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data/learning-paths/system-architect-checkin-v1.json"
UNITS = ROOT / "content/learning-units/system-architect-checkin"
HEX64 = re.compile(r"^[a-f0-9]{64}$")


def fail(message: str) -> None:
    raise ValueError(message)


def parse_frontmatter(text: str, filename: str) -> tuple[dict[str, str], dict[str, str], dict[str, str], list[str]]:
    if not text.startswith("---\n"):
        fail(f"{filename}: missing YAML frontmatter opener")
    end = text.find("\n---\n", 4)
    if end < 0:
        fail(f"{filename}: missing YAML frontmatter closer")
    block = text[4:end]
    top: dict[str, str] = {}
    source: dict[str, str] = {}
    mapping: dict[str, str] = {}
    topics: list[str] = []
    section = "top"
    topic_list = False
    for line in block.splitlines():
        if not line.strip():
            continue
        if line == "source:":
            section, topic_list = "source", False
            continue
        if line == "mapping:":
            section, topic_list = "mapping", False
            continue
        if line.startswith("  "):
            keyval = line.strip()
            if keyval == "topic_ids:":
                topic_list = True
                continue
            if line.startswith("    - ") and section == "mapping" and topic_list:
                topics.append(line[6:].strip())
                continue
            topic_list = False
            match = re.fullmatch(r"([a-z0-9_]+):\s*(.*)", keyval)
            if not match:
                fail(f"{filename}: invalid nested frontmatter line: {line!r}")
            if section == "source":
                source[match.group(1)] = match.group(2)
            elif section == "mapping":
                mapping[match.group(1)] = match.group(2)
            else:
                top[f"generation.{match.group(1)}"] = match.group(2)
            continue
        match = re.fullmatch(r"([a-z0-9_]+):\s*(.*)", line)
        if not match:
            fail(f"{filename}: invalid frontmatter line: {line!r}")
        section, topic_list = "top", False
        top[match.group(1)] = match.group(2)
    return top, source, mapping, topics


def scalar(value: str) -> str:
    value = value.strip()
    if value.startswith('"'):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid quoted scalar {value!r}: {exc}") from exc
        if not isinstance(parsed, str):
            fail(f"expected string scalar, got {value!r}")
        return parsed
    return value


def expected_prompt_digest(archive: zipfile.ZipFile, source_file: str) -> str:
    names = [n for n in archive.namelist() if n.endswith("/" + source_file)]
    if len(names) != 1:
        fail(f"archive: expected exactly one member for {source_file!r}, found {len(names)}")
    raw = archive.read(names[0])
    tail = raw[raw.find("## 提示词".encode("utf-8")):]
    if not tail:
        fail(f"archive: missing prompt heading in {source_file}")
    opening = re.search(rb"(?m)^````markdown[^\r\n]*\r?\n", tail)
    if not opening:
        fail(f"archive: missing outer prompt fence in {source_file}")
    closing = re.search(rb"(?m)^````\s*$", tail[opening.end():])
    if not closing:
        fail(f"archive: missing outer prompt closing fence in {source_file}")
    end = opening.end() + closing.end()
    return hashlib.sha256(tail[opening.start():end]).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, help="optional source ZIP for full prompt-hash verification")
    args = parser.parse_args()
    path = json.loads(MANIFEST.read_text(encoding="utf-8"))
    items = path["items"]
    learning = [item for item in items if item["mapping_status"] != "non_learning"]
    non_learning = [item for item in items if item["mapping_status"] == "non_learning"]
    expected_names = {f"{item['item_id']}.md" for item in learning}
    actual_names = {p.name for p in UNITS.glob("checkin-*.md")}
    if actual_names != expected_names:
        fail(f"unit file set mismatch: missing={sorted(expected_names-actual_names)}, extra={sorted(actual_names-expected_names)}")
    if len(learning) != 110 or len(non_learning) != 2:
        fail(f"expected 110 learning records and 2 non-learning records; got {len(learning)} and {len(non_learning)}")
    if {x["item_id"] for x in non_learning} != {"checkin-020", "checkin-026"}:
        fail("unexpected NON_LEARNING identity set")

    archive = zipfile.ZipFile(args.archive) if args.archive else None
    if archive:
        archive_sha = hashlib.sha256(args.archive.read_bytes()).hexdigest()
        if archive_sha != path["source"]["archive_sha256"]:
            fail("source archive SHA-256 does not match Learning Path manifest")
        if args.archive.stat().st_size != path["source"]["archive_size_bytes"]:
            fail("source archive size does not match Learning Path manifest")
        bad_member = archive.testzip()
        if bad_member:
            fail(f"source archive CRC failure: {bad_member}")
    gaps = unreviewed = 0
    seen_orders: set[int] = set()
    for item in learning:
        item_id = item["item_id"]
        filename = f"{item_id}.md"
        text = (UNITS / filename).read_text(encoding="utf-8")
        top, source, mapping, topic_ids = parse_frontmatter(text, filename)
        required_top = {"content_version", "path_id", "path_version", "item_id", "order", "title", "generation", "review_status"}
        if not required_top.issubset(top):
            fail(f"{filename}: missing frontmatter fields {sorted(required_top-set(top))}")
        if scalar(top["content_version"]) != "offline-learning-unit/v0.1":
            fail(f"{filename}: wrong content_version")
        if scalar(top["path_id"]) != path["path_id"] or scalar(top["path_version"]) != path["version"]:
            fail(f"{filename}: path identity does not match manifest")
        if scalar(top["item_id"]) != item_id or scalar(top["order"]) != str(item["order"]):
            fail(f"{filename}: item identity/order does not match manifest")
        if item["order"] in seen_orders:
            fail(f"duplicate learning order {item['order']}")
        seen_orders.add(item["order"])
        title = scalar(top["title"])
        if not re.search(r"(?m)^# " + re.escape(title) + r"$", text):
            fail(f"{filename}: H1 does not match frontmatter title")
        for field in ("date", "file"):
            if field not in source:
                fail(f"{filename}: missing source.{field}")
        if scalar(source["date"]) != item["source_date"] or scalar(source["file"]) != item["source_file"]:
            fail(f"{filename}: source date/file does not match Path item")
        digest = source.get("prompt_sha256", "")
        if not HEX64.fullmatch(digest):
            fail(f"{filename}: invalid prompt_sha256")
        if archive and digest != expected_prompt_digest(archive, item["source_file"]):
            fail(f"{filename}: prompt_sha256 does not match archive source")
        if mapping.get("status") != item["mapping_status"] or mapping.get("confidence") != str(item["mapping_confidence"]).lower():
            fail(f"{filename}: mapping status/confidence does not match Path item")
        if topic_ids != item["topic_ids"]:
            fail(f"{filename}: topic_ids do not match Path item (expected {item['topic_ids']!r}, got {topic_ids!r})")
        review = scalar(top["review_status"])
        if review not in {"unreviewed", "source_gap"}:
            fail(f"{filename}: unsupported review_status {review!r}")
        if review == "source_gap":
            gaps += 1
            if "SOURCE_GAP" not in text:
                fail(f"{filename}: review_status=source_gap but no visible SOURCE_GAP marker")
        else:
            unreviewed += 1
        if "wh-plain-explainer" in text or re.search(r"使用\s+wh-[\w-]+\s+技能", text):
            fail(f"{filename}: authoring instruction leaked into learning unit")
        for section in ("今天学会什么", "先建立直觉", "核心知识", "一张脑图式结构", "架构师视角", "软考关注", "记忆锚点", "来源与证据"):
            if f"## {section}" not in text:
                fail(f"{filename}: missing section {section!r}")
    if sorted(seen_orders) != [item["order"] for item in learning]:
        fail("learning item order sequence differs from manifest order")
    if archive:
        archive.close()
    print(f"PASS: {len(learning)} static units; {len(non_learning)} NON_LEARNING records omitted; {gaps} SOURCE_GAP; {unreviewed} no-known-gap drafts")
    if args.archive:
        print(f"PASS: prompt SHA-256 verified against {args.archive}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, KeyError, ValueError, json.JSONDecodeError, zipfile.BadZipFile) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
