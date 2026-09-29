# Learning Unit v0.1 Contract

- Contract: `learning-unit/v0.1`
- Status: identity, mapping and completion semantics **FROZEN** as a design contract.
- Runtime: **NOT IMPLEMENTED**. This contract does not change Planner, Today, Progress, Review, local storage or UI.
- Related: Issue #46; Learning Path #44; product boundaries #33 and #27; mapping audit PR #45.

## 1. Decision summary

> A schedulable Learning Unit is one learning `Learning Path Item`, not one of its mapped Taxonomy Topics.
>
> A Unit is complete only when an explicit, immutable Learning Unit completion fact names that exact Unit identity. Topic Progress evidence, Review evidence, a study session, a scheduled task, or opening/reading a Payload does not complete it.

The current `system-architect-checkin` path is `draft` / `MAPPING_REVIEW_REQUIRED`. It is not eligible for Planner input. This contract freezes the future domain boundary; it does not approve that path or make it runnable.

## 2. Five identities

| Identity | Canonical form | Meaning |
|---|---|---|
| Taxonomy Topic | Existing stable `topic_id`, e.g. `SOFTWARE.ENGINEERING.PROCESS` | A knowledge concept; not a Path Item or completion identity. |
| Learning Path | `(path_id)` | A named, versioned ordering of source items. |
| Learning Path Item | `(path_id, path.version, item_id)` | One source item within one exact Path version. `item_id` remains the Path contract's item identity. |
| Learning Unit runtime identity | The same tuple: `(path_id, path.version, item_id)`; serialized as `learning_unit/<path_id>/<version>/<item_id>` when a string reference is needed | The schedulable identity of that one Path Item. No additional Unit ID is introduced. |
| Progress / Review evidence | Existing Progress `event_id`; Review Item ID and derived Review Evidence ID | Evidence about an attempt and its Topic / Review Item. It is not evidence that a Learning Unit was completed. |

A completion fact has its own event identity (`event_id`) and points to the exact Learning Unit tuple. The event ID is not another Unit ID. Changing the Path version creates a different Unit runtime identity; completion does not silently carry across versions.

## 3. Unit and Topic relationship

A Learning Unit owns scheduling identity and position. Its `topic_ids` are reviewed associations to existing active L3 Topics, not an instruction to replace the Unit with a Topic task. A Unit may reference zero or multiple Topics in the static Path data, but only an approved, resolved learning item is schedulable.

Learning Payload remains Topic-scoped. A Unit may be associated with one or more existing Topic Payloads; it does not create, merge, copy, or require a Unit-specific Payload. Missing Payload is an availability state, not completion evidence. Reading a Payload does not emit Progress or Review facts and does not complete the Unit.

## 4. Mapping runtime semantics

Mapping labels describe the source-item-to-Topic relationship. They do not change Unit identity or completion rules.

| Mapping | Learning Unit interpretation | Planner eligibility / effect |
|---|---|---|
| `EXACT` | One Path Item is one Unit associated with its one Topic. | May be a candidate in an approved, resolved Path. Topic evidence still does not complete the Unit. |
| `PARTIAL` | One Path Item is one Unit associated with its one partially overlapping Topic. | May be a candidate only after Path/mapping review and approval. The association does not claim that the Unit covers the whole Topic; Topic evidence neither completes nor skips this Unit. |
| `SPLIT` | One Path Item remains **one** Unit associated with all listed Topics. | One future Planner task targets the Unit; do not split it into one task per Topic. Completing the Unit does not complete or master any associated Topic. |
| `MERGE` | Every Path Item remains its own Unit, even when several items point to the same Topic and share a `mapping_group_id`. | Schedule and complete each exact item independently. The group ID is audit metadata; it does not collapse units, transfer completion, or de-duplicate the Path order. |
| `UNMAPPED` | The Path Item identity can be retained for audit, but it has no schedulable Topic association and is unresolved. | Never invent `OTHER` or another Topic. A draft Path is not a Planner input; if an allegedly approved Path contains an unmapped/low-confidence learning item, fail closed for that Path and surface the unresolved item rather than silently skipping it. |
| `NON_LEARNING` | Not a Learning Unit. Keep the source record for provenance/order audit only. | Exclude it from the learning candidate sequence; never create a learning task or completion fact for it. |

Only an approved Path with resolved learning mappings is eligible for future Planner integration. `UNMAPPED` and low-confidence mappings are not final Planner candidates. This is consistent with the existing Learning Path contract; the current draft does not pass this gate.

## 5. Scheduling semantics (future integration)

When integrated, a new-learning task targets `target_kind: "learning_unit"` and the canonical serialized tuple, not `topic`. One Unit produces at most one new-learning task at a time, regardless of its number of Topic associations.

Candidate order is ascending Path `item.order`, after excluding `NON_LEARNING`. Order ties or duplicate Unit identities are invalid Path data, not a runtime tie-break opportunity. Existing Review tasks remain independently derived from Review Truth and retain their current priority rules.

For new-learning completion eligibility, the future Planner must consult explicit completion facts for the exact Unit tuple. Topic attempt counts, Topic Review state, Path order/date, planned minutes, and Payload availability are not substitutes. In particular, existing Topic evidence may coexist with an uncompleted Unit; it must not automatically skip that Unit. A Path version change does not inherit earlier-version completion without an explicit, separately reviewed migration.

The current Planner output contract only permits `topic` and `review_item` targets. Adding `learning_unit` requires a separately versioned Planner contract/implementation and is outside this slice.

## 6. Completion semantics and `COMPLETION_FACT_GAP`

### Audit result

**`COMPLETION_FACT_GAP`** — the repository has no persisted fact meaning “this exact Learning Path Item was completed.”

- `PlannerOutput.task_id` is a deterministic plan identity, not a recorded execution result.
- `record_task_result` checks that a task is in today's plan and that a real comprehensive attempt matches its Topic. It emits the existing Progress attempt, Review Context, and (for first learning) Topic Review Item; it does not persist the task ID or a Path Item reference.
- Progress Event v0.1 has no `path_id`, Path version, `item_id`, or task reference. A comprehensive attempt records objective question/Topic evidence, not completion of all learning represented by a Unit.
- `study_session` measures duration and optional Topic context; it has no task/Path Item target and does not imply completion.
- Review Context identifies an attempt's Review Item and `initial_learning`/`review` context; it is not a task result or Unit completion fact.
- The browser's task-derived attempt ID does not preserve a recoverable task/Path Item relation in the Progress event and is not a completion assertion.

Therefore, **Topic has an attempt ≠ Learning Unit is complete**. No existing execution fact is safe to reuse as Unit completion.

### Options considered

| Dimension | A. Independent Learning Unit completion fact | B. Extend existing execution adapter / task result |
|---|---|---|
| Progress Truth | Separate fact stream; no Progress Event or ProgressState pollution. | Safe only if the adapter emits a separate completion fact. Putting completion/task fields into Progress events changes Progress Truth. |
| Review | No Review event, evidence, mastery, or due-date effect. | Reusing Review Context / Review Item to store completion would misstate Review semantics. |
| Determinism | Deterministic from explicit event identity, exact Unit tuple and explicit timestamp; replay can be pure. | An adapter can deterministically validate the scheduled task, but task validation alone does not prove the user's completion assertion. |
| Unique Path Item location | Exact `(path_id, version, item_id)` is required by the fact. | An attempt's Topic list cannot uniquely distinguish multiple Units mapped to that Topic or represent one SPLIT Unit. |
| Repeated Topic support | Yes: distinct Unit tuples remain independent even with identical Topic IDs. | Topic-targeted task/attempt linkage alone conflates those Units. |
| Schema migration | Adds a small, isolated contract/store; no Progress Event migration. | Changing Progress Event v0.1 would require coordinated schema, validator, replay, fixture and stored-fact migration. Adapter-only output without a separate fact is not durable completion truth. |
| #27 Control Plane boundary | Records an explicit user-confirmed planning/execution fact; no learning content is created or redistributed. | Also compatible only when it captures the independent explicit fact; inferring completion from attempt, elapsed time, or adapter invocation is not. |

**Decision: choose A.** A future execution adapter may be the command/capture path for the fact, but it is not the source of completion semantics. It must receive an explicit user completion assertion and persist a separate Learning Unit completion fact. A Progress attempt may optionally be recorded alongside it, but an attempt is neither required nor sufficient for completion.

### Minimum future fact semantics (no machine schema in this slice)

A future `learning-unit-execution/v0.1` fact is an immutable record with, at minimum:

```text
event_id                 unique completion-event identity
event_type               learning_unit_completed
learning_unit            { path_id, path_version, item_id }
scheduled_task_id        the task whose target was this exact Unit
occurred_at              explicit timezone-aware completion-record instant
```

The capture adapter must validate that `scheduled_task_id` resolves to the exact Unit tuple in the plan being executed. The task ID is linkage/provenance, not the completion fact by itself. The user action is an explicit “mark this Unit complete” assertion; task display, opening/reading, planned or measured minutes, and any attempt's correctness do not produce this fact automatically.

A Unit is complete in deterministic replay iff a valid explicit completion fact exists for that exact tuple. The first such fact is sufficient; it has no mastery threshold and does not imply completion of other Units or Topics. Facts are append-only and identified explicitly. No automatic backfill from historical Topic attempts is allowed. A correction/reopen lifecycle would require a future explicit contract; v0.1 does not mutate or revoke facts.

This minimal contract deliberately does not add fields to `progress-event/v0.1`, `review-event/v0.1`, Review Evidence, or Learning Payload, and does not yet prescribe a JSON Schema, local file layout, database, or API.

## 7. Progress, Review and content boundaries

### Progress

Progress remains the deterministic replay of existing immutable Progress Events. Learning Unit completion is not a Progress Event and does not change score, accuracy, Topic attempt counts, coverage, streak, weak modules, or mastery. Conversely, Progress evidence for a Topic does not complete, skip, or backfill any Path Item.

### Review

Review remains based on explicit Progress attempt facts, Review Context, Review Items and versioned Review policy. A Unit completion fact does not create Review Evidence, register a Topic Review Item, mark a Review Item mastered, or schedule/clear a review. An associated Topic may receive Review evidence only through the existing explicit attempt/context contract.

### Learning Payload

Payload remains static, versioned and Topic-scoped with provenance. A Unit-to-Topic association may help a future view locate available Payloads, but a Unit is not a content bundle, Payload availability is not completion, and no source Prompt or third-party body becomes runtime content.

## 8. Deterministic ordering and unresolved handling

- Runtime identity is the exact Path ID + Path version + Path Item ID tuple.
- Candidate order uses the validated one-based `item.order`; `source_date` remains provenance only.
- `NON_LEARNING` records are filtered from learning candidates without renumbering or rewriting source order.
- A Path must be approved and resolved before use. Draft paths, `UNMAPPED` items and low-confidence mappings are not silently filtered into an apparently complete schedule.
- If an invalid/inconsistent approved Path reaches a future Planner, the Planner integration must fail closed for that Path and report the unresolved item(s); it must not invent a Topic, treat the item as completed, or silently continue as if the requested order were satisfied.
- All completion lookup is exact-version identity; no Topic-level or mapping-group-level completion inheritance.

## 9. Required regression cases

**Case A — repeated Topic / MERGE**

`checkin-001 → SOFTWARE.ENGINEERING.PROCESS` and `checkin-002 → SOFTWARE.ENGINEERING.PROCESS` are different Units. Completing `checkin-001` creates no completion for `checkin-002`; Topic attempt evidence on the shared Topic creates completion for neither.

**Case B — SPLIT**

`checkin-005 → PROCESS + TESTING` is one Unit and one future task target. It must not be expanded into two “Today” learning tasks. Its completion is the explicit fact for `(..., checkin-005)`, not the presence of evidence for either or both Topics.

**Case C — UNMAPPED**

An item such as `checkin-032` has an empty `topic_ids` list. It remains unresolved and blocks use of an inconsistent Path; it is not assigned a synthetic Topic or converted into a completed/skipped Unit.

## 10. Out of scope and next gate

This contract does not implement Planner new-learning selection, Planner target schema changes, Today UI, local execution storage/adapter changes, Learning Payload bundles, taxonomy edits, bulk content, or Topic/Unit mastery. Planner behavior remains unchanged.

Before Planner Learning Path integration, a separate implementation gate must provide:

1. an approved, mapping-reviewed Path with no unresolved/low-confidence candidates;
2. the isolated completion-fact contract and deterministic validator/replay (with explicit task-to-Unit validation);
3. a versioned Planner target/output/input integration that schedules one Unit per Path Item and reads only exact Unit completion facts;
4. regression tests for the repeated-Topic, SPLIT and UNMAPPED cases, plus proof existing Progress / Review behavior is unchanged.

Until those gates pass, the safe state is: **Learning Unit semantics frozen; Planner integration not yet safe to start.**
