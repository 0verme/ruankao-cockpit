# Frontend Migration Slice 1 — Astro + React Topic Shell

**Status: `BACKEND_CONTRACT_RECONCILED`; TypeScript HTTP client ↔ live FastAPI round-trip PASS in an isolated local directory. Playwright remains fixture-backed; deployed same-origin browser serving is not tested.**

This slice owns Browser Presentation only. Astro emits two static routes and shell; React islands fetch the merged FastAPI contract. Python `cockpit_service` and domain replay remain the only business truth source.

```text
Browser
  → Astro static routes + React islands
  → same-origin HTTP /api/*
  → FastAPI transport (merged PR #40)
  → cockpit_service
  → Planner / Progress replay / Review replay / validated Learning Payload / Taxonomy
```

## Routes and scope

- `/` — Today API read, explicit initialization action only after API returns `not_initialized`, server-provided tasks/capacity, entry to the supported Topic.
- `/topics/ARCH.CLOUD_NATIVE.CONTAINERS_SERVERLESS` — static Astro route with a React island that fetches the API's Topic response.
- The Topic page renders the existing TopicExperience projection: header and Taxonomy breadcrumb, payload state/version, objectives, core knowledge, exam context, source/provenance metadata, light Progress/Review read state, and an optional Verification form.
- API `learning_payload_status="unavailable"` is rendered as **材料尚未整理**. `invalid_learning_payload` / `invalid_source_provenance` is a distinct fail-closed API error. No runtime content generation is attempted.
- Verification is available only when entered from a Today task (`task_id` query parameter). The browser sends actual answer time, source reference, correct/incorrect and optional error cause, then rereads Topic and Today from the API.

The frontend has no browser-owned planner, task→Topic mapping, provenance validator, Progress/Review policy, localStorage learning truth, `event_id`, `review_context_id`, mastery, due date or progress percentage.

## Reconciled FastAPI v0.1 contract (merged PR #40)

The consumer types now match [`docs/api/FRONTEND_API_V01.md`](../api/FRONTEND_API_V01.md). Contract facts below are served by the backend; the frontend does only view/presentation mapping.

| Endpoint | Merged wire contract consumed |
|---|---|
| `POST /api/init` | No body. Returns `{ state: "created" | "already_exists" }`. Initialization is explicit; GET never initializes. |
| `GET /api/today` | Returns `{ planner, task_topics, progress, review }`. Today is `planner.days[0]`. Each mapped task's `task_id` indexes Python-resolved `task_topics[task_id]` (`topic_id`, `topic_name`, Taxonomy breadcrumb and Payload availability/version). React does not map review item IDs to Topics. |
| `GET /api/topics/{topic_id}` | Returns `{ topic, learning_payload_status, learning_payload_version, learning_payload, progress, review, verification_sources }`. `topic` holds canonical name/id/version/breadcrumb; progress/review fields remain server projections. A legal missing Payload is explicit `unavailable` with a null object/version. Invalid provenance and non-active Topics use distinct API categories. |
| `POST /api/attempts` | Request is `{ task_id, occurred_at, question, correct, error_cause? }`; `question` contains source reference metadata. Response includes server-owned `recorded` counts and replayed `today`. Client rereads `GET /api/today` and `GET /api/topics/{topic_id}` for the refreshed page. |

Error envelope is `{ "error": { "category": string, "message": string } }`. The frontend branches on stable `category`, never parses message text. It handles `not_initialized`, `incomplete_local_data`, `unknown_topic`, `unknown_task`, `non_active_topic`, `invalid_request`, `invalid_timestamp`, `invalid_attempt`, `invalid_source_reference`, `invalid_source_provenance`, `invalid_learning_payload`, `forbidden_path`, `future_evidence`, `target_mismatch`, `task_not_scheduled`, `duplicate_event`, transaction conflicts, storage/catalog errors, network failure and generic API failure.

The contract does not return source URLs. The page shows returned provenance metadata (source ID/commit/path/anchor/question ID/confidence) and does not synthesize links. No frontend-specific adapter fields are required for the merged contract.

## Fixture mode and integration limit

`PUBLIC_API_MODE=contract-fixture` selects an in-memory fixture adapter. The UI always displays:

> DEV FIXTURE / CONTRACT FIXTURE — 仅用于浏览器开发与契约测试，不是 production truth。

The fixture wire responses mirror PR #40; its Topic content imports the one checked-in Learning Payload. The pre-recorded after-attempt response only exercises UI state. It does not call FastAPI, validate provenance, persist an attempt, run replay or establish production Progress/Review facts. Query `?fixture=` selects deterministic unavailable, invalid-provenance, uninitialized and API/network failure states. Normal mode defaults to HTTP, not fixtures.

Unit/component/E2E tests use the marked fixture adapter. Separately, the real TypeScript `createHttpApiClient` was loaded through Vite and run against a loopback Uvicorn server with a newly created temporary `COCKPIT_LOCAL_DIR`: explicit init → Today → Topic/source → POST test attempt → fresh Topic/Today reads. The isolated run confirmed one persisted Progress event and the server replay attempt count in both POST response and reread; its temporary data directory was deleted. This synthetic attempt was test-only and never touched user `.local` data. The Python FastAPI transport suite also passed (8 tests).

This verifies the HTTP client and API persistence/replay contract, but is not a real-browser test against the backend: Playwright still exercises only the visible contract fixture, and a deployed same-origin frontend/API setup has not been validated.

## COPY / ADAPT / REJECT

### COPY

No helper was copied from `data-warehouse-visualized` in this slice. The audit's pure scroll/sidebar/visualization kernels remain future candidates only if a demonstrated need appears. No reference-repository code, course text or visualization content is included.

### ADAPT

- LearnShell → a smaller Topic shell: content width, light surface/card hierarchy, semantic links, document scrolling, loading/error/unavailable states, breadcrumb and mobile-safe layout.
- LessonViewport → Topic content sections with the document as sole scroll owner; no lesson next/previous or completion semantics.
- PR #36 `TopicExperience` is rendered from the merged API response; all domain facts are fetched from HTTP.
- The current slice intentionally has no taxonomy sidebar/drawer and no route-transition persistence.

### REJECT

No Course/Chapter/Lesson model, `completedLessonIds`, localStorage progress, lesson completion rate, “reading means learned”, next-lesson completion, warehouse course/domain content, SQL/Banking/Loan/Lineage components, sql.sb branding/Logo or Progress Bootstrap logic. UI preferences are not persisted in this slice.

## Responsive and accessibility notes

- Light-first, readable content width, moderate density, semantic headings/sections, visible focus ring, skip link, labeled controls and `aria-live` loading/success states.
- Responsive checks target desktop and 390px/320px mobile. The document/body remains the only vertical scroll owner; content has no nested scroll pane.
- Browser history uses ordinary Astro static links and a full route load. Astro SSR, ClientRouter and persisted islands are deferred.

## Test / integration gates

- Vitest: exact wire endpoint/request/response contract, error categories, fixture labels, component loading/initialization/unavailable/error, Verification success/failure and reread behavior.
- Astro check/build: static two-route build.
- Playwright: Today, Topic, unavailable, not initialized, API/network error, keyboard navigation, mobile overflow, document scroll ownership, refresh, and Verification success/failure using only the marked contract fixture.
- Those browser tests validate Browser Presentation and fixture behavior only. The separate live TypeScript HTTP client ↔ Uvicorn run and Python transport tests validate API persistence/replay; neither is a deployed-browser/same-origin test. No broader production integration is claimed.
