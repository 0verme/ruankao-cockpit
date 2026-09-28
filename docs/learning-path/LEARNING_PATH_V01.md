# Learning Path v0.1 Contract

- Contract: `learning-path/v0.1`
- Status: contract frozen for static audit/draft data; the check-in path itself remains `draft` / `MAPPING_REVIEW_REQUIRED`.
- Related: Issue #44; product boundaries #33 and #27.
- Runtime integration: **DEFERRED**. This document does not authorize a Planner, Today, Progress, Review, or browser behavior change.

## 1. Domain boundary

| Layer | Answers | Owns |
|---|---|---|
| Taxonomy | What knowledge exists? | Versioned Knowledge Topic hierarchy and stable active L3 IDs. Knowledge Topic is not Case Capability. |
| Learning Path | In what order does the user prefer to encounter new learning? | Versioned source-item order, provenance, and reviewed mapping to existing L3 Topics. |
| Learning Payload | What static learning content is presented for a Topic? | Separately versioned, source-backed learning material. A path outline is not a payload. |
| Progress / Review | What did the user actually do, and what is due? | Explicit learning/attempt facts and deterministic replay/policy. A path position is not evidence. |
| Planner | What should be scheduled today? | Existing deterministic scheduling from Progress / Review Truth and available capacity. Future new-learning selection may consult an approved Path order. |

A Learning Path neither creates Taxonomy Topics nor embeds a second topic hierarchy. It does not carry learning content, correctness, mastery, completion, review due dates, progress facts, actual duration, study-day constraints, or exam-date obligations.

## 2. Contract shape

The normative machine-readable shape is `data/learning-paths/schema-v0.1.json`; the audited example/draft is `data/learning-paths/system-architect-checkin-v1.json`. The file is ordinary versioned repository data, not a runtime Prompt, schedule, or content payload.

### Path identity

- `schema_version`: exactly `learning-path/v0.1`.
- `path_id`: stable machine identity; this archive uses `system-architect-checkin`.
- `version`: SemVer. Any reordered source, changed source identity, or materially changed mapping requires a new path version and audit; do not silently rewrite an approved version.
- `status`: `draft`, `approved`, or `deprecated`. The check-in dataset remains `draft` until mapping review is accepted.
- `taxonomy_version`: the exact taxonomy version against which `topic_ids` were audited.
- `title`: user-facing path label, not an identity key.

### Item identity and source order

Each `items[]` row has:

- `item_id`: stable ID independent of the editable title; current deterministic archive sequence uses `checkin-001` … `checkin-112`.
- `order`: one-based position across all archive records, including `NON_LEARNING` entries. Filter `NON_LEARNING` to obtain the learning sequence. Missing calendar days do not create synthetic items.
- Order is extracted by ascending ISO source date and then archive-relative `source_file` as deterministic tie-break. It is not based on Taxonomy ID, topic count, or ZIP compression/member order.

These IDs identify items in this path version. If the source archive changes such that an item moves, is inserted, or is replaced, publish a new path version and preserve the old identity/history rather than renumbering an approved path in place.

### Provenance and optional outline

Each item records:

- `source_date`: original date label, for provenance only. It is **not** a future study date or deadline.
- `source_file`: archive-root-relative path using POSIX separators; never a machine/NAS absolute path.
- `source_title`: original filename topic suffix when present; for date-only names, the source Prompt title is used as a fallback.
- `original_topic_title`: source Prompt's concise stated topic title, when present. It can be broad or inconsistent with the filename/content; preserve rather than silently normalize it.
- `knowledge_point_titles`: optional short outline labels extracted from the source item. These are indexing metadata, not copied body text or Learning Payload content.

The source object uses `type: user_provided_checkin_archive` and records the original archive filename, byte size, and SHA-256 fingerprint so the reviewed source can be identified without storing a machine-specific path. The contract does not infer redistribution rights from user provision. Third-party body text, questions, explanations, images, PDFs, and external resource contents remain outside the formal path data unless separately reviewed and licensed. This draft keeps no external URLs or Prompt bodies.

## 3. Mapping contract

`topic_ids` contains zero or more canonical active L3 IDs from the declared `taxonomy_version`. It must never contain parent-only nodes, aliases, Case Capability IDs, or invented IDs.

### Mapping status

The JSON values are lowercase; audit documents display uppercase labels.

- `exact`: one source item aligns closely with one active L3 boundary; exactly one `topic_id`.
- `partial`: one source item covers only part of one active L3 Topic or extends beyond its boundary; exactly one mapped `topic_id` and a note describing the difference.
- `split`: one source item substantively covers multiple active L3 Topics; at least two `topic_ids`. Never force a broad source item into only one of them.
- `merge`: multiple source items jointly deepen/cover the same one active L3 Topic. A `mapping_group_id` links the audit group; each `merge` row has exactly one `topic_id`. It does not state how many Planner tasks should be scheduled.
- `unmapped`: no reasonable active L3 mapping is supported; `topic_ids` is empty. Preserve the reason and, if useful, candidate concepts in `mapping_notes`, not in `topic_ids`.
- `non_learning`: explicit rest day or non-learning record; `topic_ids` and outline are empty and confidence is `null`.

If an item itself maps to multiple Topics while also participating in a repeated-coverage group, `split` takes precedence and `mapping_group_id` expresses the additional group relation. Group IDs are audit metadata only.

### Confidence

- `high`: direct source wording/knowledge points strongly support the chosen Topic boundary.
- `medium`: the broad match is clear but the item spans adjacent boundaries or requires interpretation.
- `low`: only a broad candidate or insufficient evidence exists. Low-confidence mappings are never direct Planner inputs.

Confidence measures certainty of the mapping decision, not completeness. Thus a well-evidenced subset may be `partial` with `high` confidence. An `unmapped` item in this draft is `low`; `non_learning` has no confidence value.

Every mapped or unresolved learning item must include `mapping_notes`; notes are especially required to explain PARTIAL, SPLIT, MERGE, and UNMAPPED decisions. Mapping categories describe source-to-topic relations and are not a quality score.

## 4. Runtime semantics and safety

Learning Path supplies only the ordering of candidate **new learning**. It supplies no state transition and no content.

A future Planner integration must combine:

```text
approved Learning Path order
+ existing deterministic Progress / Review Truth
+ current Planner policy and capacity
→ today's new-learning choice
```

It must not:

- treat `source_date`, `order`, opening/reading a source item, or reaching a path position as study evidence;
- infer mastery, completion, accuracy, streak, review due, or actual time from the path;
- read or execute a source Prompt;
- use Learning Payload content as a substitute for mapping or Progress evidence;
- use a low-confidence mapping as a final candidate;
- schedule `UNMAPPED` items as Topics;
- silently treat a SPLIT item as one Topic or define MERGE de-duplication/completion semantics without a separately reviewed policy.

`PARTIAL`, `SPLIT`, and `MERGE` mappings need an explicit future runtime interpretation before an approved path can drive tasks. This Phase 1 audit does not define that behavior. Reviews continue to be scheduled from Review Truth, regardless of a path's new-learning order.

## 5. Prompt and generated-content boundary

Source items may contain `wh-plain-explainer` or similar authoring instructions. They are eligible only as a future **Learning Payload authoring / offline content generation aid**. They are not runtime domain truth:

- Browser runtime does not depend on Prompts to generate facts.
- Planner does not read Prompts.
- Progress / Review does not read Prompts.
- A Prompt does not automatically become a Learning Payload.
- Any AI output requires content review, factual validation, provenance, and separate versioning before inclusion as a static Learning Payload.

This contract introduces no AI runtime, no generated knowledge facts, and no batch Payload generation.

## 6. Validation and current draft status

Run from repository root:

```sh
python3 scripts/validate_learning_path.py
```

The validator checks deterministic identities/order, safe relative provenance, mapping status/cardinality, confidence semantics, taxonomy-version consistency, active-L3-only topic references, and mapping-group overlap. It validates static data only and has no Planner integration.

For the current check-in draft:

- 112 source records = 110 learning items + 2 explicit rest records.
- 98/110 learning items have at least one mapped Topic; 12 remain `UNMAPPED` / LOW.
- Coverage is 60/110 active L3; uncovered and duplicate-covered ID lists are in `SYSTEM_ARCHITECT_CHECKIN_MAPPING_AUDIT.md`.
- 40 source items map to multiple Topic IDs; merge/partial relations remain reviewable metadata, not runtime decisions.

The audit verdict is `MAPPING_REVIEW_REQUIRED`. The static Draft and contract may be reviewed/versioned without promoting the path to `approved`. Planner integration, Today integration, Learn Directory, and batch Learning Payload authoring remain deferred.
