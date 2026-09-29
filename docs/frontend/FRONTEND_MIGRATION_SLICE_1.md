# Frontend Migration Slice 1 — Astro + React Topic Shell

**Status: `DEPLOYED_UAT_PASS` (2026-09-28, after PR #41). Real Chromium verified the production Astro static build → same-origin `/api/*` proxy → loopback FastAPI → `cockpit_service` → immutable facts / deterministic replay chain.**

This document records the earlier Slice 1 Browser Presentation/UAT only. Astro emitted two routes in that slice; later PR #54 added static Learning Unit routes and Issue #55 adds `/learn` plus manifest-derived previous/next navigation. The current endpoint/read-model semantics are documented in [`FRONTEND_API_V01.md`](../api/FRONTEND_API_V01.md) and [`LEARNING_PATH_V01.md`](../learning-path/LEARNING_PATH_V01.md). Python domain loaders remain the source for Path/Unit identity and order; browser navigation remains read-only.

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

This earlier client round-trip is superseded by the deployment UAT below. The checked-in Playwright suite still uses explicitly marked contract fixtures for deterministic presentation tests; a separate temporary UAT suite exercised the built frontend against real FastAPI over same-origin HTTP, without a mock API.

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
- Checked-in Playwright: Today, Topic, unavailable, not initialized, API/network error, keyboard navigation, mobile overflow, document scroll ownership, refresh, and Verification success/failure using only the marked contract fixture.
- Deployment UAT: see the closeout record below; it exercised the built artifact with a live FastAPI backend and no mock API.

## Deployment UAT closeout (2026-09-28; PR #41)

**Topology:** real browser `http://127.0.0.1:<frontend-port>/` and same-origin `/api/*`; an ephemeral Python standard-library reverse proxy served the built Astro `dist/` and forwarded `/api/*` to Uvicorn bound only to `127.0.0.1`. FastAPI used one explicit absolute `COCKPIT_LOCAL_DIR` under `/tmp`; no Streamlit writer shared it. This proxy was UAT-only and removed, not a committed production deployment configuration.

**Real Browser:** Chromium completed explicit init; verified GET-before-init returned `409 not_initialized` without creating the local directory; read Today from the API (server Planner task order/minutes/topic metadata); navigated to `ARCH.CLOUD_NATIVE.CONTAINERS_SERVERLESS`; rendered the live validated Payload/version, breadcrumb, objectives, core knowledge, exam context, sources/provenance, Progress, Review, and Verification. Production bundle defaulted to the HTTP client and showed no fixture banner.

A test-only attempt submitted through the UI used server task `task-e7eb1a30c93b33d4c4ec765e6a9451a47e1aab8e0820bdd4ae6533f84b2743f1`, occurred at `2026-09-28T10:13:55.000Z`, and indexed source `gs-comp-2024-h1-q65` (`younghong1992`, commit `c467a7cbc16970c52cf6d723badbb22938963ae6`, question `2024-h1-comprehensive-q65`); `correct=true`. The browser request contained no client-owned event/context ID or Progress/Review state flags.

- Facts before attempt: 0 Progress events, 0 Review contexts, 0 Review Items. After: **1 / 1 / 1**.
- Replay: `attempt_count=1`, `accuracy=1.0`, `mastery=learning`, `review_status=scheduled`, `next_due_local_date=2026-09-29`, `policy_version=review-policy/simple-ladder/v0.1`.
- UI rereads matched FastAPI; fixed-`as_of` FastAPI planner/progress/review/topic responses matched direct `cockpit_service` replay. Duplicate resubmission returned `409 task_not_scheduled` after the task left Today; invalid source returned `422 forbidden_path`, invalid timestamp `422 invalid_timestamp`, invalid task `409 task_not_scheduled`; all rejection cases left fact-file hashes unchanged.
- Two browser refreshes and repeated init did not change persisted fact counts or bytes. FastAPI restart with the same explicit local directory restored the same state; restarting the static frontend from the same build artifact also preserved it.
- Live API distinguished unavailable (`200`, null Payload), unknown Topic (`404 unknown_topic`), and invalid provenance (`422 invalid_source_provenance`). Temporary source-copy-only test variants rendered unavailable and invalid-provenance states distinctly; neither modified repository content or the UAT facts directory.
- Desktop, 390px, and 320px Chromium smoke passed; Verification input/button remained visible and operable, keyboard skip/focus worked, no horizontal overflow or nested scroll owner. PR #41 fixed the discovered 3px 320px Verification input overflow and added a task-context regression test.

**Post-fix test evidence:** Python unittest **233 passed, 1 skipped**; all five repository validators PASS; frontend Vitest **14 passed**; Astro check **0 errors / 0 warnings / 0 hints**; static build **2 routes**; fixture-backed Playwright **10 passed**; post-merge real-browser UAT **6 scenario runs passed**. GitHub PR #41 CI passed.

**Known limits / non-goals at the time of PR #41:** only `/` and the one implemented Topic route were shipped; this did not prove broad content value or product direction. The API remains local, single-user, without auth/database/cloud or multi-writer locking. The UAT reverse proxy is not a supported production config; a future deploy still needs a documented same-origin static-server/reverse-proxy setup and must preserve explicit local-data ownership. No Learn Directory, Search, Chat/LLM, CMS, SSR, DB, or Streamlit deletion was added in Slice 1. The read-only Learn Directory and Unit navigation added later do not change those retained boundaries.
