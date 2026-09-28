# Learning Payload v0.1

This directory contains a deliberately small set of static, topic-scoped learning cards for Today tasks. It is not a course catalogue or a content platform.

- `schema.json` defines the serialized contract.
- `<topic_id>.json` is one explicitly versioned payload for one active L3 Knowledge Topic.
- `learning_payload.py` validates the payload against the taxonomy, source catalog/mappings, and (where used) a confirmed Golden Set record before rendering.
- Missing files return an explicit unavailable state. Invalid payload or provenance is rejected; no material is generated at runtime.

Each learning objective, core point, and exam focus item links to one or more `source_references` by `reference_id`. Textbook and exam-outline references reuse taxonomy source-mapping provenance (`source_id`, immutable `source_commit`, repository-relative `source_path`, `source_value`, and confidence). Question references reuse the Golden Set's source fields and must match a confirmed record for the same Topic.

Payload prose is short, self-authored synthesis. Do not copy third-party textbook, question, answer, analysis, OCR, or PDF text into this directory. “Exam focus” wording must reflect its evidence: a syllabus entry proves syllabus coverage; a single indexed question proves only that the indexed sample touches the Topic, not that the Topic is frequent.

To revise content, review its upstream evidence and increment `version`; a contract change requires a new `schema_version` and corresponding validator/tests. Taxonomy Topic IDs and Case Capabilities remain separate dimensions.
