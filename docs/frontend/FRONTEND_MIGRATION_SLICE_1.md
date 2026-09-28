# Frontend Migration Slice 1 — Astro + React Topic Shell

**Status: `BACKEND_INTEGRATION_PENDING`**

This slice owns Browser Presentation only. Astro emits static routes and shell; React islands fetch the API. Python remains the only domain/application truth source.

```text
Browser
  → Astro static routes + React islands
  → same-origin HTTP /api/*
  → FastAPI transport adapter (parallel implementation)
  → cockpit_service
  → Planner / Progress replay / Review replay / validated Learning Payload / Taxonomy
```

## Routes and scope

- `/` — Today API read, explicit initialization action when API reports `not_initialized`, server-provided tasks/capacity, entry to the supported Topic.
- `/topics/ARCH.CLOUD_NATIVE.CONTAINERS_SERVERLESS` — static Astro route with a React island that fetches `TopicExperience`.
- The Topic page renders the existing read model: header and Taxonomy breadcrumb, payload state/version, objectives, core knowledge, exam context, source/provenance metadata, light Progress/Review read state, and an optional Verification form.
- Missing payload is rendered as **材料尚未整理**. Invalid payload/provenance is a distinct fail-closed API error. No runtime content generation is attempted.
- Verification is available only when entered from a Today task (`task_id` query parameter). The browser submits actual answer time, indexed/manual source reference, correct/incorrect and optional error cause, then rereads Topic and Today from the API.

No browser-owned planner, taxonomy mapping, provenance validator, Progress/Review policy, localStorage learning truth, `event_id`, `review_context_id`, mastery, due date or progress percentage is introduced.

## API contract assumptions (to reconcile with backend)

The API paths are fixed by Issue #34. Until the FastAPI contract merges, the following minimal JSON shapes are **consumer assumptions**, not a claim of an integrated contract:

| Endpoint | Assumption consumed by this browser |
|---|---|
| `POST /api/init` | Explicit initialization; returns `{ "initialized": boolean }`. GET requests never initialize local facts. |
| `GET /api/today` | `{ as_of, timezone, day: { local_date, capacity_minutes, planned_minutes, remaining_minutes, tasks[] } }`. Each task includes `task_id`, `task_type`, backend-resolved `topic_id`/`topic_name`, `planned_minutes`, and `display_reason`. In particular, review task → Topic mapping belongs to Python/service, not TypeScript. |
| `GET /api/topics/{topic_id}` | JSON projection of `TopicExperience` from PR #36 (snake_case); `learning_payload: null` means valid Topic with no payload. A malformed/unverified payload/provenance must fail closed with a typed API error, not return guessed content. |
| `POST /api/attempts` | Request: `task_id`, timezone-aware `occurred_at`, `source_reference`, `correct`, optional `error_cause`. Response `{ "accepted": true }`; it contains no client-generated or client-controlled domain IDs/policies. Client then rereads Today and Topic. |

Expected error body: `{ "error": { "code": string, "message": string } }`. Important codes include `not_initialized`, `payload_unavailable`, `unknown_topic`, `invalid_payload_provenance`, `invalid_input`, `task_not_scheduled`, and `duplicate_attempt`. HTTP status is not the only semantic signal; the stable error code drives user-facing copy.

The API may return optional server-computed `source_url` on validated provenance references. The browser only renders `http(s)` links supplied by the API; absent links are shown as provenance metadata, not synthesized from source IDs.

Before integration is declared complete, reconcile these field names, optionality, error envelope/status mapping, Today task target projection, source link policy, POST response, and task/attempt validation with the merged backend contract. Do not add a second frontend business model to preserve this provisional shape.

## Fixture mode

`PUBLIC_API_MODE=contract-fixture` selects an in-memory adapter. The UI always displays:

> DEV FIXTURE / CONTRACT FIXTURE — 仅用于浏览器开发与契约测试，不是 production truth。

The Topic content fixture imports the one checked-in Learning Payload; the static fixture responses and pre-recorded post-attempt replay are only for testing UI states. They do not validate provenance, execute a planner, persist an attempt or establish real Progress/Review facts. `?fixture=` can select deterministic unavailable, invalid-provenance, uninitialized and API-failure cases. Normal mode defaults to HTTP, not fixtures.

## COPY / ADAPT / REJECT

### COPY

No helper was copied from `data-warehouse-visualized` in this slice. The audit's pure scroll/sidebar/visualization kernels remain future candidates only if a demonstrated need appears. No reference-repository code, course text or visualization content is included.

### ADAPT

- LearnShell → a much smaller Topic shell: shared content width, light surface/card hierarchy, semantic links, plain document scrolling, clear loading/error/unavailable states, breadcrumb and mobile-safe layout.
- LessonViewport → Topic content sections with the single document as scroll owner; no lesson next/previous or completion semantics.
- Source/provenance and verification sections adapt PR #36 `TopicExperience`; all facts are fetched from HTTP.
- The current slice intentionally has no taxonomy sidebar/drawer and no route-transition persistence.

### REJECT

No Course/Chapter/Lesson model, `completedLessonIds`, localStorage progress, lesson completion rate, “reading means learned”, next-lesson completion, warehouse course/domain content, SQL/Banking/Loan/Lineage components, sql.sb branding/Logo or Progress Bootstrap logic. UI preferences are not persisted in this slice.

## Responsive and accessibility notes

- Light-first, readable content width, moderate density, semantic headings/sections, visible focus ring, skip link, labeled controls and `aria-live` loading/success states.
- Responsive checks target desktop and 390px/320px mobile. The document/body remains the only vertical scroll owner; content has no nested scroll pane.
- Browser history uses ordinary Astro static links and a full route load. Astro SSR, ClientRouter and persisted islands are deferred.

## Test / integration gates

- Vitest: typed API endpoint/error contract, fixture labels, component loading/initialization/unavailable/error, and Verification success/failure + reread behavior.
- Astro check/build: static two-route build.
- Playwright: Today, Topic, unavailable, not initialized, API error, keyboard navigation, mobile overflow, document scroll ownership, refresh, and Verification success/failure using only the marked contract fixture.
- These tests validate Browser Presentation and assumptions only. They are **not** a FastAPI/cockpit_service integration test, do not prove writes/replay persistence, and do not complete the migration gate in #34.
