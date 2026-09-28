"""Load and validate small, source-backed Today learning payloads.

Payload files are static repository data. This module performs no network or
LLM calls; every evidence reference must resolve to the checked-in taxonomy
source mapping or a confirmed Golden Set record for the same Topic.
"""
from __future__ import annotations

import json
import re
from pathlib import Path, PurePosixPath
from typing import Any, Mapping
from urllib.parse import quote


PROJECT_ROOT = Path(__file__).resolve().parent
SCHEMA_VERSION = "learning-payload/v0.1"
TOPIC_ID_RE = re.compile(r"^[A-Z0-9_]+(?:\.[A-Z0-9_]+){2}$")
REFERENCE_ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
CONFIDENCE = {"high", "medium", "low"}
REFERENCE_KINDS = {"textbook_section", "exam_outline", "golden_set_question"}


class LearningPayloadError(ValueError):
    """A payload is malformed or its provenance cannot be verified."""

    def __init__(self, message: str, category: str = "invalid_learning_payload") -> None:
        self.category = category
        super().__init__(message)


def _fail(message: str, category: str = "invalid_learning_payload") -> None:
    raise LearningPayloadError(message, category)


def _read_json(path: Path, label: str) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        _fail(f"Required {label} file is missing: {path}", "invalid_learning_catalog")
    except (OSError, json.JSONDecodeError) as exc:
        _fail(f"Cannot read {label} JSON {path}: {exc}", "invalid_learning_catalog")


def _require_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip() or "\x00" in value:
        _fail(f"{label} must be a non-empty string")
    return value


def _exact_keys(value: Mapping[str, Any], required: set[str], allowed: set[str], label: str) -> None:
    missing = sorted(required - set(value))
    extra = sorted(set(value) - allowed)
    if missing or extra:
        details = []
        if missing:
            details.append(f"missing {', '.join(missing)}")
        if extra:
            details.append(f"unsupported {', '.join(extra)}")
        _fail(f"{label}: {'; '.join(details)}")


def _safe_source_path(value: Any, label: str) -> str:
    path = _require_string(value, label)
    parsed = PurePosixPath(path)
    if (
        path.startswith("/")
        or "\\" in path
        or ".." in parsed.parts
        or any(part in path for part in ("/vol5/", "/root/", "ruankao-cockpit_base/research"))
    ):
        _fail(f"{label} must be a safe repository-relative path", "invalid_source_provenance")
    return path


def _topic_ancestors(topic_id: str, nodes_by_id: Mapping[str, Mapping[str, Any]]) -> set[str]:
    ancestors: set[str] = set()
    current: str | None = topic_id
    while current is not None:
        if current in ancestors or current not in nodes_by_id:
            _fail(f"Taxonomy has an invalid parent chain for {topic_id!r}", "invalid_learning_catalog")
        ancestors.add(current)
        parent = nodes_by_id[current].get("parent_id")
        current = parent if isinstance(parent, str) else None
    return ancestors


def _validate_evidence_list(value: Any, known_reference_ids: set[str], label: str) -> list[str]:
    if not isinstance(value, list) or not value:
        _fail(f"{label} must reference at least one source")
    if any(not isinstance(item, str) or item not in known_reference_ids for item in value):
        _fail(f"{label} contains an unknown source reference", "invalid_source_provenance")
    if len(value) != len(set(value)):
        _fail(f"{label} contains duplicate source references")
    return value


def _validate_content_items(
    value: Any,
    *,
    label: str,
    min_count: int,
    max_count: int,
    text_max: int,
    known_reference_ids: set[str],
    with_heading: bool = False,
) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not min_count <= len(value) <= max_count:
        _fail(f"{label} must contain {min_count}–{max_count} items")
    normalized: list[dict[str, Any]] = []
    for index, item in enumerate(value):
        item_label = f"{label}[{index}]"
        if not isinstance(item, Mapping):
            _fail(f"{item_label} must be an object")
        required = {"text", "evidence_refs"} | ({"heading"} if with_heading else set())
        _exact_keys(item, required, required, item_label)
        text = _require_string(item.get("text"), f"{item_label}.text")
        if len(text) > text_max:
            _fail(f"{item_label}.text exceeds {text_max} characters")
        refs = _validate_evidence_list(item.get("evidence_refs"), known_reference_ids, f"{item_label}.evidence_refs")
        normalized_item: dict[str, Any] = {"text": text, "evidence_refs": list(refs)}
        if with_heading:
            heading = _require_string(item.get("heading"), f"{item_label}.heading")
            if len(heading) > 80:
                _fail(f"{item_label}.heading exceeds 80 characters")
            normalized_item = {"heading": heading, **normalized_item}
        normalized.append(normalized_item)
    return normalized


def _load_learning_catalogs(root: Path) -> tuple[
    dict[str, dict[str, Any]], list[dict[str, Any]], dict[str, dict[str, Any]], dict[str, Any]
]:
    taxonomy = _read_json(root / "taxonomy" / "taxonomy.json", "taxonomy")
    mapping_doc = _read_json(root / "taxonomy" / "source-mappings.json", "source mapping")
    if not isinstance(taxonomy, Mapping) or taxonomy.get("taxonomy_version") != "0.1":
        _fail("Unsupported or malformed taxonomy document", "invalid_learning_catalog")
    if not isinstance(mapping_doc, Mapping) or mapping_doc.get("taxonomy_version") != "0.1":
        _fail("Unsupported or malformed source mapping document", "invalid_learning_catalog")
    nodes = taxonomy.get("nodes")
    sources = mapping_doc.get("sources")
    mappings = mapping_doc.get("mappings")
    if not isinstance(nodes, list) or not isinstance(sources, list) or not isinstance(mappings, list):
        _fail("Taxonomy source catalogs are malformed", "invalid_learning_catalog")
    if any(not isinstance(node, Mapping) or not isinstance(node.get("id"), str) for node in nodes):
        _fail("Taxonomy nodes are malformed", "invalid_learning_catalog")
    if any(not isinstance(source, Mapping) or not isinstance(source.get("source_id"), str) for source in sources):
        _fail("Source catalog entries are malformed", "invalid_learning_catalog")
    if any(
        not isinstance(item, Mapping) or not isinstance(item.get("canonical_topic_ids"), list)
        for item in mappings
    ):
        _fail("Source mapping entries are malformed", "invalid_learning_catalog")
    nodes_by_id = {node["id"]: node for node in nodes}
    sources_by_id = {source["source_id"]: dict(source) for source in sources}
    if len(nodes_by_id) != len(nodes) or len(sources_by_id) != len(sources):
        _fail("Taxonomy or source catalog contains duplicate IDs", "invalid_learning_catalog")
    return nodes_by_id, [dict(item) for item in mappings], sources_by_id, taxonomy


def _validate_reference(
    reference: Any,
    *,
    topic_id: str,
    nodes_by_id: Mapping[str, Mapping[str, Any]],
    mappings: list[dict[str, Any]],
    sources_by_id: Mapping[str, Mapping[str, Any]],
    golden_records: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    if not isinstance(reference, Mapping):
        _fail("Each source reference must be an object")
    kind = reference.get("kind")
    if not isinstance(kind, str) or kind not in REFERENCE_KINDS:
        _fail(f"Unsupported source reference kind {kind!r}", "invalid_source_provenance")
    common = {
        "reference_id", "kind", "display_title", "source_id", "source_commit",
        "source_path", "confidence",
    }
    if kind in {"textbook_section", "exam_outline"}:
        required = common | {"source_value", "source_anchor"}
        allowed = required
    else:
        required = common | {"source_question_id", "golden_set_record_id"}
        allowed = required
    _exact_keys(reference, required, allowed, f"source_references[{reference.get('reference_id', '?')}]")

    reference_id = _require_string(reference.get("reference_id"), "source reference id")
    if REFERENCE_ID_RE.fullmatch(reference_id) is None:
        _fail(f"Invalid source reference id {reference_id!r}")
    display_title = _require_string(reference.get("display_title"), f"{reference_id}.display_title")
    source_id = _require_string(reference.get("source_id"), f"{reference_id}.source_id")
    source_commit = _require_string(reference.get("source_commit"), f"{reference_id}.source_commit")
    if COMMIT_RE.fullmatch(source_commit) is None:
        _fail(f"{reference_id}: source_commit must be an immutable 40-character lowercase SHA", "invalid_source_provenance")
    source_path = _safe_source_path(reference.get("source_path"), f"{reference_id}.source_path")
    confidence = reference.get("confidence")
    if not isinstance(confidence, str) or confidence not in CONFIDENCE:
        _fail(f"{reference_id}: invalid provenance confidence", "invalid_source_provenance")
    source_catalog = sources_by_id.get(source_id)
    if source_catalog is None or source_catalog.get("source_commit") != source_commit:
        _fail(f"{reference_id}: source id/commit is not registered in source catalog", "invalid_source_provenance")

    if kind in {"textbook_section", "exam_outline"}:
        source_value = _require_string(reference.get("source_value"), f"{reference_id}.source_value")
        source_anchor = _require_string(reference.get("source_anchor"), f"{reference_id}.source_anchor")
        ancestors = _topic_ancestors(topic_id, nodes_by_id)
        matching_mappings = [
            item for item in mappings
            if item.get("source_id") == source_id
            and item.get("source_commit") == source_commit
            and item.get("source_path") == source_path
            and item.get("source_value") == source_value
            and any(mapped_topic in ancestors for mapped_topic in item.get("canonical_topic_ids", []))
        ]
        if not matching_mappings:
            _fail(f"{reference_id}: no source mapping supports Topic {topic_id}", "invalid_source_provenance")
        if not any(confidence == item.get("confidence") for item in matching_mappings):
            _fail(f"{reference_id}: confidence does not match source mapping", "invalid_source_provenance")
        return {
            "reference_id": reference_id,
            "kind": kind,
            "display_title": display_title,
            "source_id": source_id,
            "source_commit": source_commit,
            "source_path": source_path,
            "source_value": source_value,
            "source_anchor": source_anchor,
            "confidence": confidence,
        }

    source_question_id = _require_string(reference.get("source_question_id"), f"{reference_id}.source_question_id")
    record_id = _require_string(reference.get("golden_set_record_id"), f"{reference_id}.golden_set_record_id")
    record = golden_records.get(record_id)
    if record is None or record.get("question_type") != "comprehensive":
        _fail(f"{reference_id}: Golden Set question reference is not indexed", "invalid_source_provenance")
    source = record.get("source")
    if not isinstance(source, Mapping) or any(source.get(key) != value for key, value in {
        "source_id": source_id,
        "source_commit": source_commit,
        "source_path": source_path,
        "source_question_id": source_question_id,
    }.items()):
        _fail(f"{reference_id}: question provenance does not match Golden Set record", "invalid_source_provenance")
    topic_refs = record.get("topics")
    matching_topic_refs = [
        item for item in topic_refs or []
        if isinstance(item, Mapping) and item.get("topic_id") == topic_id
    ]
    annotation = record.get("annotation")
    if (
        not matching_topic_refs
        or not isinstance(annotation, Mapping)
        or annotation.get("status") != "confirmed"
    ):
        _fail(f"{reference_id}: question evidence is not confirmed for Topic {topic_id}", "invalid_source_provenance")
    if matching_topic_refs[0].get("confidence") != confidence:
        _fail(f"{reference_id}: confidence does not match Golden Set annotation", "invalid_source_provenance")
    return {
        "reference_id": reference_id,
        "kind": kind,
        "display_title": display_title,
        "source_id": source_id,
        "source_commit": source_commit,
        "source_path": source_path,
        "source_question_id": source_question_id,
        "golden_set_record_id": record_id,
        "confidence": confidence,
    }


def load_learning_payload(topic_id: str, *, root: str | Path | None = None) -> dict[str, Any] | None:
    """Return a validated payload for an active L3 Topic, or ``None`` if absent.

    Missing payloads are an explicit supported state. Malformed content or
    unverifiable provenance raises ``LearningPayloadError`` and is never
    converted into generated or guessed material.
    """
    if not isinstance(topic_id, str) or TOPIC_ID_RE.fullmatch(topic_id) is None:
        _fail("Learning payload resolution requires a canonical L3 topic id")
    project_root = Path(root) if root is not None else PROJECT_ROOT
    path = project_root / "data" / "learning-payloads" / f"{topic_id}.json"
    if not path.is_file():
        return None
    payload = _read_json(path, "learning payload")
    if not isinstance(payload, Mapping):
        _fail("Learning payload must be a JSON object")
    required = {
        "schema_version", "version", "topic_id", "objectives", "core_points",
        "exam_focus", "source_references",
    }
    _exact_keys(payload, required, required, "learning payload")
    if payload.get("schema_version") != SCHEMA_VERSION:
        _fail(f"Unsupported Learning Payload schema version {payload.get('schema_version')!r}")
    version = _require_string(payload.get("version"), "learning payload version")
    if re.fullmatch(r"\d+\.\d+\.\d+", version) is None:
        _fail("Learning payload version must use MAJOR.MINOR.PATCH")
    if payload.get("topic_id") != topic_id:
        _fail("Learning payload topic_id does not match the requested Topic")

    nodes_by_id, mappings, sources_by_id, taxonomy = _load_learning_catalogs(project_root)
    node = nodes_by_id.get(topic_id)
    if not isinstance(node, Mapping) or node.get("level") != 3 or node.get("status") != "active":
        _fail(f"Learning payload target {topic_id!r} is not an active L3 Topic", "invalid_learning_catalog")

    references = payload.get("source_references")
    if not isinstance(references, list) or not references:
        _fail("Learning payload must contain at least one source reference")
    golden_doc = _read_json(project_root / "data" / "golden-set" / "comprehensive.sample.json", "comprehensive Golden Set")
    records = golden_doc.get("records") if isinstance(golden_doc, Mapping) else None
    if not isinstance(records, list):
        _fail("Comprehensive Golden Set records are malformed", "invalid_learning_catalog")
    golden_records = {
        record["id"]: record
        for record in records
        if isinstance(record, Mapping) and isinstance(record.get("id"), str)
    }
    validated_references: list[dict[str, Any]] = []
    seen_reference_ids: set[str] = set()
    for reference in references:
        validated = _validate_reference(
            reference,
            topic_id=topic_id,
            nodes_by_id=nodes_by_id,
            mappings=mappings,
            sources_by_id=sources_by_id,
            golden_records=golden_records,
        )
        reference_id = validated["reference_id"]
        if reference_id in seen_reference_ids:
            _fail(f"Duplicate source reference id {reference_id!r}")
        seen_reference_ids.add(reference_id)
        validated_references.append(validated)

    objectives = _validate_content_items(
        payload.get("objectives"),
        label="objectives",
        min_count=2,
        max_count=4,
        text_max=240,
        known_reference_ids=seen_reference_ids,
    )
    core_points = _validate_content_items(
        payload.get("core_points"),
        label="core_points",
        min_count=1,
        max_count=5,
        text_max=1000,
        known_reference_ids=seen_reference_ids,
        with_heading=True,
    )
    if sum(len(item["text"]) for item in core_points) > 3000:
        _fail("Core knowledge is too long for a short Today learning card")
    exam_focus = _validate_content_items(
        payload.get("exam_focus"),
        label="exam_focus",
        min_count=1,
        max_count=4,
        text_max=320,
        known_reference_ids=seen_reference_ids,
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "version": version,
        "topic_id": topic_id,
        "objectives": objectives,
        "core_points": core_points,
        "exam_focus": exam_focus,
        "source_references": validated_references,
        "taxonomy_version": taxonomy["taxonomy_version"],
    }


def learning_source_url(reference: Mapping[str, Any], *, root: str | Path | None = None) -> str:
    """Build a stable upstream GitHub blob URL from validated provenance."""
    project_root = Path(root) if root is not None else PROJECT_ROOT
    mapping_doc = _read_json(project_root / "taxonomy" / "source-mappings.json", "source mapping")
    sources = mapping_doc.get("sources", []) if isinstance(mapping_doc, Mapping) else []
    source = next(
        (item for item in sources if isinstance(item, Mapping) and item.get("source_id") == reference.get("source_id")),
        None,
    )
    repository = source.get("repository") if isinstance(source, Mapping) else None
    commit = _require_string(reference.get("source_commit"), "source_commit")
    if (
        not isinstance(repository, str)
        or re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository) is None
        or source.get("source_commit") != commit
    ):
        _fail("Cannot build a source URL from unregistered provenance", "invalid_source_provenance")
    path = _safe_source_path(reference.get("source_path"), "source_path")
    if COMMIT_RE.fullmatch(commit) is None:
        _fail("Cannot build a source URL from a non-immutable commit", "invalid_source_provenance")
    return f"https://github.com/{repository}/blob/{commit}/{quote(path, safe='/')}"


__all__ = [
    "LearningPayloadError",
    "SCHEMA_VERSION",
    "learning_source_url",
    "load_learning_payload",
]
