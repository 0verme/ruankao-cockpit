"""Deterministic, read-only Learning Unit Markdown loader.

The Learning Path manifest is the identity/mapping authority. Markdown files
are static authoring artifacts and never produce Progress, Review, or
Completion facts.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re
from typing import Any, Mapping

import yaml
from yaml.constructor import ConstructorError
from yaml.resolver import BaseResolver


PROJECT_ROOT = Path(__file__).resolve().parent
ITEM_ID_RE = re.compile(r"^checkin-[0-9]{3}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
MAPPING_STATUSES = {"exact", "partial", "split", "merge", "unmapped"}
CONFIDENCE_VALUES = {"high", "medium", "low"}
REVIEW_STATUSES = {"source_gap", "unreviewed"}

# Allowlisted static data locations. Request values are only used to look up
# manifest entries; they never become filesystem path components.
PATH_LOCATIONS = {
    "system-architect-checkin": (
        Path("data/learning-paths/system-architect-checkin-v1.json"),
        Path("content/learning-units/system-architect-checkin"),
    ),
}


class LearningUnitExperienceError(ValueError):
    """A requested unit is missing, unavailable, or failed integrity checks."""

    def __init__(self, message: str, category: str = "invalid_learning_unit") -> None:
        self.category = category
        super().__init__(message)


@dataclass(frozen=True)
class LearningUnitTopic:
    topic_id: str
    name: str


@dataclass(frozen=True)
class LearningUnitExperience:
    path_id: str
    path_version: str
    path_title: str
    path_status: str
    item_id: str
    order: int
    title: str
    content_markdown: str
    generation_status: str
    review_status: str
    mapping_status: str
    mapping_confidence: str
    topic_ids: tuple[str, ...]
    topics: tuple[LearningUnitTopic, ...]
    source_date: str
    source_file: str
    source_prompt_sha256: str


class _UniqueKeySafeLoader(yaml.SafeLoader):
    """Safe YAML loader that also rejects duplicate keys instead of clobbering."""


def _construct_unique_mapping(loader: _UniqueKeySafeLoader, node: yaml.MappingNode, deep: bool = False):
    loader.flatten_mapping(node)
    mapping: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        try:
            duplicate = key in mapping
        except TypeError as exc:
            raise ConstructorError("while constructing a mapping", node.start_mark,
                                   "found an unhashable key", key_node.start_mark) from exc
        if duplicate:
            raise ConstructorError("while constructing a mapping", node.start_mark,
                                   f"found duplicate key {key!r}", key_node.start_mark)
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


_UniqueKeySafeLoader.add_constructor(BaseResolver.DEFAULT_MAPPING_TAG, _construct_unique_mapping)


def _fail(message: str, category: str = "invalid_learning_unit") -> None:
    raise LearningUnitExperienceError(message, category)


def _read_json(path: Path, label: str, category: str) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        _fail(f"{label} static data is unavailable or malformed", category)


def _require_string(value: Any, label: str, category: str = "invalid_learning_unit") -> str:
    if not isinstance(value, str) or not value.strip() or "\x00" in value:
        _fail(f"{label} must be a non-empty string", category)
    return value


def _split_frontmatter(text: str, item_id: str) -> tuple[Mapping[str, Any], str]:
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].rstrip("\r\n") != "---":
        _fail(f"Markdown frontmatter is missing for {item_id!r}")
    end = next(
        (index for index, line in enumerate(lines[1:], start=1)
         if line.rstrip("\r\n") == "---"),
        None,
    )
    if end is None:
        _fail(f"Markdown frontmatter is not closed for {item_id!r}")
    raw_frontmatter = "".join(lines[1:end])
    try:
        frontmatter = yaml.load(raw_frontmatter, Loader=_UniqueKeySafeLoader)
    except yaml.YAMLError as exc:
        _fail(f"Markdown frontmatter is malformed for {item_id!r}: {exc}")
    if not isinstance(frontmatter, Mapping):
        _fail(f"Markdown frontmatter must be an object for {item_id!r}")
    body = "".join(lines[end + 1:]).lstrip("\r\n")
    if not body.strip():
        _fail(f"Markdown body is empty for {item_id!r}")
    return frontmatter, body


def _read_topic_names(root: Path, topic_ids: list[str], taxonomy_version: str) -> tuple[LearningUnitTopic, ...]:
    if not topic_ids:
        return ()
    taxonomy = _read_json(root / "taxonomy" / "taxonomy.json", "Taxonomy", "invalid_learning_catalog")
    if not isinstance(taxonomy, Mapping) or taxonomy.get("taxonomy_version") != taxonomy_version:
        _fail("Taxonomy version does not match the Learning Path", "invalid_learning_catalog")
    nodes = taxonomy.get("nodes")
    if not isinstance(nodes, list):
        _fail("Taxonomy nodes are malformed", "invalid_learning_catalog")
    nodes_by_id: dict[str, Mapping[str, Any]] = {}
    for node in nodes:
        if not isinstance(node, Mapping) or not isinstance(node.get("id"), str):
            _fail("Taxonomy nodes are malformed", "invalid_learning_catalog")
        if node["id"] in nodes_by_id:
            _fail("Taxonomy contains duplicate Topic IDs", "invalid_learning_catalog")
        nodes_by_id[node["id"]] = node
    topics: list[LearningUnitTopic] = []
    for topic_id in topic_ids:
        node = nodes_by_id.get(topic_id)
        if (
            not isinstance(node, Mapping)
            or node.get("level") != 3
            or node.get("status") != "active"
            or not isinstance(node.get("name"), str)
            or not node["name"].strip()
        ):
            _fail(f"Learning Path references an unavailable active L3 Topic {topic_id!r}",
                  "invalid_learning_catalog")
        topics.append(LearningUnitTopic(topic_id=topic_id, name=node["name"]))
    return tuple(topics)


def load_learning_unit(
    path_id: str,
    item_id: str,
    *,
    project_root: Path = PROJECT_ROOT,
) -> LearningUnitExperience:
    """Load one allowlisted Path Item and fail closed on identity drift."""
    location = PATH_LOCATIONS.get(path_id) if isinstance(path_id, str) else None
    if location is None:
        _fail("Learning Path was not found", "unknown_learning_path")

    root = Path(project_root).resolve()
    manifest_relative, content_relative = location
    manifest = _read_json(root / manifest_relative, "Learning Path", "invalid_learning_path")
    if not isinstance(manifest, Mapping) or manifest.get("path_id") != path_id:
        _fail("Learning Path identity is malformed", "invalid_learning_path")
    path_version = _require_string(manifest.get("version"), "Learning Path version", "invalid_learning_path")
    path_title = _require_string(manifest.get("title"), "Learning Path title", "invalid_learning_path")
    path_status = _require_string(manifest.get("status"), "Learning Path status", "invalid_learning_path")
    taxonomy_version = _require_string(manifest.get("taxonomy_version"), "Taxonomy version", "invalid_learning_path")
    items = manifest.get("items")
    if not isinstance(items, list):
        _fail("Learning Path items are malformed", "invalid_learning_path")
    if not isinstance(item_id, str):
        _fail("Learning Unit identity is malformed", "unknown_learning_unit")
    matches = [item for item in items if isinstance(item, Mapping) and item.get("item_id") == item_id]
    if not matches:
        _fail("Learning Unit was not found", "unknown_learning_unit")
    if len(matches) != 1:
        _fail("Learning Path contains duplicate item identities", "invalid_learning_path")
    item = matches[0]
    if not isinstance(item_id, str) or not ITEM_ID_RE.fullmatch(item_id):
        _fail("Learning Unit identity is malformed", "invalid_learning_path")

    if item.get("mapping_status") == "non_learning":
        _fail("This Path Item is not a Learning Unit", "not_a_learning_unit")

    order = item.get("order")
    if isinstance(order, bool) or not isinstance(order, int) or order < 1:
        _fail("Learning Path item order is malformed", "invalid_learning_path")
    expected_topic_ids = item.get("topic_ids")
    if (
        not isinstance(expected_topic_ids, list)
        or any(not isinstance(topic_id, str) for topic_id in expected_topic_ids)
        or len(expected_topic_ids) != len(set(expected_topic_ids))
    ):
        _fail("Learning Path item mapping is malformed", "invalid_learning_path")
    mapping_status = item.get("mapping_status")
    mapping_confidence = item.get("mapping_confidence")
    if (
        not isinstance(mapping_status, str)
        or mapping_status not in MAPPING_STATUSES
        or not isinstance(mapping_confidence, str)
        or mapping_confidence not in CONFIDENCE_VALUES
    ):
        _fail("Learning Path item mapping is malformed", "invalid_learning_path")
    if mapping_status == "unmapped" and expected_topic_ids:
        _fail("UNMAPPED Learning Path item must not contain Topic IDs", "invalid_learning_path")
    if mapping_status == "split" and len(expected_topic_ids) < 2:
        _fail("SPLIT Learning Path item must contain multiple Topic IDs", "invalid_learning_path")
    if mapping_status not in {"unmapped", "split"} and len(expected_topic_ids) != 1:
        _fail("This Learning Path mapping must contain exactly one Topic ID", "invalid_learning_path")

    source_date = _require_string(item.get("source_date"), "Learning Path source date", "invalid_learning_path")
    source_file = _require_string(item.get("source_file"), "Learning Path source file", "invalid_learning_path")
    trusted_item_id = item.get("item_id")
    if not isinstance(trusted_item_id, str) or not ITEM_ID_RE.fullmatch(trusted_item_id):
        _fail("Learning Path item identity is malformed", "invalid_learning_path")

    content_root = root / content_relative
    candidate = content_root / f"{trusted_item_id}.md"
    try:
        resolved_content_root = content_root.resolve(strict=True)
        resolved_file = candidate.resolve(strict=True)
    except (OSError, RuntimeError):
        _fail(f"Learning Unit Markdown is unavailable for {item_id!r}")
    if (
        resolved_content_root != content_root
        or resolved_file.parent != resolved_content_root
        or not resolved_file.is_file()
    ):
        _fail(f"Learning Unit Markdown is outside its content directory for {item_id!r}")
    try:
        markdown_text = resolved_file.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        _fail(f"Learning Unit Markdown cannot be read for {item_id!r}")
    frontmatter, body = _split_frontmatter(markdown_text, item_id)

    if frontmatter.get("content_version") != "offline-learning-unit/v0.1":
        _fail(f"Unsupported Learning Unit content version for {item_id!r}")
    identity_checks = {
        "path_id": path_id,
        "path_version": path_version,
        "item_id": item_id,
        "order": order,
    }
    for field, expected in identity_checks.items():
        value = frontmatter.get(field)
        if isinstance(expected, int) and isinstance(value, bool):
            _fail(f"Markdown {field} does not match the Learning Path for {item_id!r}")
        if value != expected:
            _fail(f"Markdown {field} does not match the Learning Path for {item_id!r}")

    title = _require_string(frontmatter.get("title"), "Markdown title")
    mapping = frontmatter.get("mapping")
    if not isinstance(mapping, Mapping):
        _fail(f"Markdown mapping is malformed for {item_id!r}")
    frontmatter_topic_ids = mapping.get("topic_ids")
    if (
        mapping.get("status") != mapping_status
        or mapping.get("confidence") != mapping_confidence
        or frontmatter_topic_ids != expected_topic_ids
        or not isinstance(frontmatter_topic_ids, list)
        or any(not isinstance(topic_id, str) for topic_id in frontmatter_topic_ids)
    ):
        _fail(f"Markdown mapping does not match the Learning Path for {item_id!r}")

    generation = frontmatter.get("generation")
    if not isinstance(generation, Mapping):
        _fail(f"Markdown generation metadata is malformed for {item_id!r}")
    generation_status = _require_string(generation.get("status"), "Markdown generation status")
    review_status = frontmatter.get("review_status")
    if not isinstance(review_status, str) or review_status not in REVIEW_STATUSES:
        _fail(f"Markdown review status is malformed for {item_id!r}")

    source = frontmatter.get("source")
    if not isinstance(source, Mapping):
        _fail(f"Markdown source metadata is malformed for {item_id!r}")
    frontmatter_source_date = source.get("date")
    frontmatter_source_file = source.get("file")
    source_prompt_sha256 = source.get("prompt_sha256")
    if frontmatter_source_date != source_date or frontmatter_source_file != source_file:
        _fail(f"Markdown source identity does not match the Learning Path for {item_id!r}")
    if not isinstance(source_prompt_sha256, str) or not SHA256_RE.fullmatch(source_prompt_sha256):
        _fail(f"Markdown source fingerprint is malformed for {item_id!r}")

    topics = _read_topic_names(root, expected_topic_ids, taxonomy_version)
    return LearningUnitExperience(
        path_id=path_id,
        path_version=path_version,
        path_title=path_title,
        path_status=path_status,
        item_id=item_id,
        order=order,
        title=title,
        content_markdown=body,
        generation_status=generation_status,
        review_status=review_status,
        mapping_status=mapping_status,
        mapping_confidence=mapping_confidence,
        topic_ids=tuple(expected_topic_ids),
        topics=topics,
        source_date=source_date,
        source_file=source_file,
        source_prompt_sha256=source_prompt_sha256,
    )


__all__ = [
    "LearningUnitExperience",
    "LearningUnitExperienceError",
    "LearningUnitTopic",
    "load_learning_unit",
]
