# Phase 4 Validation Report

> **审计基线**：`main` / `origin/main`，`306cf2d2296ff74903f0b612dff9a70d8ff537ad`（包含 PR #11 merge commit）。
> **验证位置**：基于该 main commit 的 `docs/p4-closeout` closeout 分支；P4.8/P4.9 当前 PR 尚未合并，正式仓库 `main` 未修改。
> **范围**：审计 P4.1～P4.7 的真实实现与验证，并验证本次 P4.8 文档同步；本报告为 P4.9 正式 Gate 结论。未修改 Phase 4 policy、replay 语义或 Progress / Taxonomy contract。

## A. Executive Result

```text
Phase 4 Gate: PASS
```

四个 Gate 问题均有可复跑代码、schema、fixtures / tests 和 validator 证据。P4.1～P4.9 均已完成；本报告只对已提交到基线的实现事实作审计，不把 GitHub Issue #4 尚未同步的 checklist 当作验证证据。

| P4 item | contract | implementation | schema | tests | validator | docs | status |
|---|---|---|---|---|---|---|---|
| P4.1 Review Model v0.1 | Review Item identity / kind / reference | `engine/review/model.py` | `data/review/schema.json` | `tests/test_review_contract.py` | `validate_review_contract.py` | `docs/review/REVIEW_MODEL_V01.md` | PASS |
| P4.2 Review Event / Evidence | 显式 context、policy-neutral evidence projection | `engine/review/model.py` | `data/review/schema.json` | `tests/test_review_contract.py` | `validate_review_contract.py` | `docs/review/REVIEW_EVIDENCE_V01.md` | PASS |
| P4.3 Mastery State Machine | `mastery-policy/spaced-consecutive/v0.1` | `engine/rules/review_policy_v01.py` | `mastery-review-state.schema.json` 输出 contract；policy 常量在 kernel | `tests/test_review_policy.py`、fixture matrix | `validate_review.py` | `MASTERY_POLICY_V01.md`、symbol freeze | PASS |
| P4.4 Scheduling Policy | `review-policy/simple-ladder/v0.1` | `engine/rules/review_policy_v01.py` | `mastery-review-state.schema.json` 输出 contract；policy 常量在 kernel | `tests/test_review_policy.py`、fixture matrix | `validate_review.py` | `REVIEW_SCHEDULING_POLICY_V01.md` | PASS |
| P4.5 deterministic replay | 显式 `as_of` / timezone、adapter、stable ordering | `engine/review/replay.py` | `data/review/mastery-review-state.schema.json` | `tests/test_review_replay.py`、determinism tests | `validate_review.py` | Review / replay 文档 | PASS |
| P4.6 synthetic fixtures + validator | `mastery-review-fixture/v0.1` | manifest + 36 synthetic fixture files | `fixture-schema.v0.1.json` | `tests/test_review_fixture_matrix.py`、fixture plan tests | `scripts/validate_review.py` | `docs/PHASE4_TEST_MATRIX.md` | PASS |
| P4.7 unit tests / edge cases | 边界、rejection、determinism、回归 | `tests/` | Progress / Review schemas | policy / replay / matrix / regression tests | Review / Progress / Taxonomy validators | test matrix | PASS |
| P4.8 Documentation / Architecture Sync | 实现、validator、架构、UI consumer 状态一致 | 文档同步；仅调整 Review validator 的状态说明文本 | 不变 | 全量测试 | 全部 validators | README、architecture、engine、review、data、UI 文档 | PASS |
| P4.9 Validation Report | 本报告及四项 Gate 证据 | 本报告 | 引用冻结 schemas | 引用 fixtures / tests | 引用实际运行输出 | 本文件 | PASS |

PR provenance：P4.3/P4.4（PR #7）、P4.1/P4.2（PR #9）、P4.5（PR #10）、P4.6/P4.7（PR #11）；本报告不以这些 PR 描述替代对 `main` 代码和测试的检查。

## B. Frozen Contracts

以下版本均取自 schema、源码常量或 catalog，不推测额外版本名：

| Contract / artifact | 冻结版本 | 权威来源 |
|---|---|---|
| Review Model | `review-model/v0.1` | `engine/review/model.py`、`data/review/schema.json` |
| Review Item | `review-item/v0.1` | 同上 |
| Review Context Event | `review-event/v0.1` | 同上 |
| Review Evidence | `review-evidence/v0.1` | 同上 |
| MasteryReviewState | `mastery-review-state/v0.1` | `engine/review/replay.py`、`data/review/mastery-review-state.schema.json` |
| Mastery policy | `mastery-policy/spaced-consecutive/v0.1` | `engine/rules/review_policy_v01.py` |
| Review scheduling policy | `review-policy/simple-ladder/v0.1` | 同上 |
| Policy projection | `review-policy-projection/v0.1` | 同上、state schema |
| Outcome adapter | `review-outcome/raw-facts/v0.1` | `engine/review/replay.py`、`docs/review/REVIEW_OUTCOME_ADAPTER_V01.md` |
| Progress Event / State / Replay | `progress-event/v0.1` / `progress-state/v0.1` / `progress-replay/v0.1` | `data/progress/schema.json` |
| Taxonomy / Capability catalog version | `taxonomy_version = 0.1` / `capability_version = 0.1` | `taxonomy/taxonomy.json`、`taxonomy/capabilities.json`、Progress model |
| P4.1/P4.2 contract fixture | `review-fixture/v0.1` | `data/review/schema.json` |
| P4.6/P4.7 replay fixture | `mastery-review-fixture/v0.1` | `data/review/fixture-schema.v0.1.json`、`fixture-plan.json`（manifest `review-fixture-plan/v0.2`） |

ProgressState 不包含 mastery / review 字段；Review 是独立派生状态，不改变 Progress v0.1 语义。

## C. Domain Flow

实际实现链路为：

```text
Immutable Progress Attempt Facts
+ Explicit Review Context Events
+ Explicit Review Item catalog / Taxonomy / Capability inputs
        ↓
Progress / Review contract validation
        ↓
Policy-neutral Review Evidence projection
        ↓
Versioned outcome adapter
  comprehensive correctness → success / failure
  case / capability score   → insufficient（保留 raw score，不猜阈值）
        ↓
Frozen Mastery Policy + Review Scheduling Policy
+ explicit as_of + explicit IANA timezone
        ↓
Deterministic MasteryReview replay
        ↓
MasteryReviewState v0.1
```

`engine/review/replay.py` 先验证 Progress facts 与 Review inputs，再从事实和显式 context 投影 Evidence，适配为 policy primitive 并执行纯 policy projection。派生 state 可删除后从输入重建；不会将 state 回写到 Progress facts。

## D. 四项 Phase 4 Gate 证据

### Gate 1 — Current State：PASS

针对显式声明的 review item catalog，replay 稳定输出：

```text
items[review_item_id].review_item_id
items[review_item_id].item_kind
items[review_item_id].mastery_state / mastery_reason
items[review_item_id].review_status / review_status_reason
items[review_item_id].evidence[]（含 evidence_status、raw value、policy outcome / reason、source trace）
```

无 evidence 的 item 得到 `mastery_state = new`、`review_status = not_scheduled`；缺少足够事实的 evidence 不伪装为 failure 或 0 分。证据：`mastery-new-item`、`mastery-first-success`、`mastery-insufficient-evidence` fixtures；`test_empty_item_is_rebuilt_with_two_independent_axes`、`test_no_evidence_is_not_failure_or_zero`、`test_every_ready_fixture_replays_expected_state_or_category`。

### Gate 2 — Due Set：PASS

replay 要求显式 `as_of` 与 IANA `timezone`（可用 `schedule_timezone`，若两者同时提供必须一致），输出 item-level `review_status` 及 aggregate：

```text
review.due_today_count
review.overdue_count
review.due_count
```

已验证 `due_count == due_today_count + overdue_count == item-level due/overdue projection count`，统计单位是 item 而非 event；due 边界包含精确到期时刻。证据：`sched-before-due`（含边界 variants）、`sched-due-count-consistency`；`test_due_calendar_boundaries_are_inclusive_and_local_date_based`、`test_item_and_aggregate_counts_are_consistent`、`test_due_and_overdue_are_item_counts`。

### Gate 3 — Explainability：PASS

item projection 与 replay envelope 提供可追溯链：

```text
evidence trace / evidence_status / source reference
outcome adapter id + version + policy_outcome_reason
mastery / review policy version
review_interval_days + scheduling_reason
mastery_reason + review_status_reason
last_review_at + next_due_at + next_due_local_date
as_of + timezone + schedule_timezone + tzdata_version
```

原因来自 evidence、版本化 adapter / policy 与 replay 输出，不由 UI 或 AI 推测。案例和 capability 的 score 即使是 0 或高分，也会保留 raw fact 并映射为 `insufficient`，直至独立 score outcome rubric 冻结。证据：`mastery-mastered`、`mastery-mastered-failure`、`sched-before-due`、`evidence-zero-score`、`evidence-case-score-high`；`test_frozen_success_ladder_and_mastered_maintenance`、`test_failure_from_new_learning_and_mastered_resets_counters_and_schedule`、`test_score_zero_and_high_remain_insufficient_not_failure`。

### Gate 4 — Determinism：PASS

本轮实际验证：

- 同一输入、policy identity、`as_of`、timezone 与相同 timezone database 环境重复 replay 得到相同 state；
- input order independence；evidence 以 `(UTC instant, evidence_id)` 稳定 tie-break，item output order 稳定；
- `as_of` 显式输入并回显；`as_of == occurred_at` 可纳入，future evidence 以 `future_evidence` 拒绝；
- UTC 等价 instant 与不同 offset 表示等价；时区由显式 IANA 名称确定，不读机器本地时区；
- DST 午夜缺口有显式 IANA timezone fixture / test 覆盖；
- 静态 wall-clock guard 检查 Progress / Review replay 与 policy 路径，不允许 `datetime.now()`、`datetime.utcnow()`、`date.today()`、`time.time()` 等隐式当前时间入口。

证据：`determinism-same-timestamp-ordering`、`determinism-same-instant-timezones`、`determinism-asof-exactly-at-event`、`time-local-date-boundary`、`time-dst-sensitive`；`test_repeat_shuffle_and_input_mutation`、`test_same_instant_offsets_produce_identical_state`、`test_same_timestamp_uses_source_event_id_tie_breaker`、`test_future_evidence_is_rejected`、`test_timezone_rollover_and_dst_gap_follow_explicit_iana_calendar`、`test_existing_replay_path_is_scanned_and_clean`、`test_policy_module_has_no_implicit_time_source`。

## E. Fixture / Test Matrix 与验证结果

### Synthetic fixture 文件（36 个）

下表按 frozen manifest 的 fixture ID 前缀分组，数量互斥且合计 36：

| 类别 | 数量 | 代表 fixture | 覆盖 / 结果 |
|---|---:|---|---|
| Mastery state / success ladder / failure | 10 | `mastery-new-item`、`mastery-first-success`、`mastery-repeated-success`、`mastery-mastered`、`mastery-mastered-failure` | 初始无 evidence；1/3/7/15 天 ladder；learning/mastered 维护；failure reset；PASS |
| Evidence / score adapter | 3 | `evidence-zero-score`、`evidence-case-score`、`evidence-case-score-high` | raw score 留痕且 policy outcome 为 insufficient；PASS |
| Scheduling / due aggregate | 2 | `sched-before-due`、`sched-due-count-consistency` | before/exact/after/overdue variants；item 与 aggregate 计数一致；PASS |
| Determinism / explicit as_of | 3 | `determinism-same-timestamp-ordering`、`determinism-same-instant-timezones`、`determinism-asof-exactly-at-event` | tie-break、offset equivalence、as_of 边界；PASS |
| Timezone / local date / DST | 3 | `time-utc-baseline`、`time-local-date-boundary`、`time-dst-sensitive` | 显式时区、本地日期边界、DST gap；PASS |
| Invalid / rejection | 15 | `invalid-future-evidence`、`invalid-duplicate-event-id`、`invalid-evidence-kind-mismatch` | 正式 rejection categories；拒绝无 partial state；PASS |
| **总计** | **36** |  | **36 个 policy symbols 均 frozen；validator replay 36 个 fixture 文件，26 个 expected state 与 15 个 expected rejection case/variant 匹配** |

`26 + 15 = 41` 是因部分 fixture 含多个 replay variants；fixture 文件本身仍为 36 个。P4.7 另有 harness / static guard / Progress regression tests，不计入 synthetic fixture 文件数。

### 本轮最终回归验证

| 命令 | 实际结果 |
|---|---|
| `python3 -m unittest discover -s tests` | **143 tests，1 skipped，OK** |
| `python3 scripts/validate_review_contract.py` | PASS Review Model / Evidence v0.1 schema validation、evidence projection 与 contract boundary |
| `python3 scripts/validate_review.py` | PASS frozen schema / manifest；36 policy symbols；36 fixture files；26 expected states；15 expected rejection categories；output schema、metadata、aggregate invariants、determinism PASS |
| `python3 scripts/validate_progress.py` | PASS；16 fixtures（9 valid replay / 7 expected rejection）；deterministic replay / regression PASS |
| `python3 scripts/validate_taxonomy.py` | PASS；150 topics、13 capabilities、source mapping / Golden Set 校验 PASS |
| `git diff --check` | PASS |

Taxonomy validator 实际报告：150 topics（13 L1 / 27 L2 / 110 L3）、34 aliases、79 source mappings（9 unresolved）、13 capabilities；Golden Set 148 条（100 comprehensive / 48 case），L1 coverage 13/13、L2 25/27、L3 75/110、capability 13/13。9 个 unresolved mapping 与 L2/L3 coverage gap 是 validator 明示的诊断项，不是本轮新增 drift，也不使 validator 失败。

## F. Known Limitations / Future

- `review-outcome/raw-facts/v0.1` **不会**将 `case.score_ratio` 或 capability score 解释为 success/failure；目前即使 raw score 有值，`policy_outcome = insufficient`。这是 v0.1 的保守、显式设计，不是实现 bug，也不以案例得分证明 Review success/failure 已完整支持。
- Topic、Question、Case Capability 是不同 Review item 粒度；Evidence 语义和来源关联不互相复制、不跨粒度升级。案例总分不复制为 Topic / Capability 证据。
- `review_item_id` v0.1 identity 已冻结，但 taxonomy / source identity split、merge、retirement 的自动 migration 未实现；policy 新版本的历史状态 migration / replay-retention 策略也未实现。
- 本轮 policy 是简单、可解释的 v0.1 选择；**SM-2、FSRS、forgetting curve、个性化权重未实现**，不属于 P4 Gate blocker。
- Adaptive Planner、Rolling 7-Day Plan、Daily Adaptive Tasks、30-Day Plan instance 均未实现；**Planner 未冻结，Today Card / PlanTimeline / PlanModeSwitcher / Adaptive Daily Tasks 仍 BLOCKED BY PLANNER CONTRACT**。未为 Planner 指派 Phase 编号。
- Assessment / `recent_score`、Essay state / score / planner、task completion / `completion_rate` / streak 均无 contract，仍 Future / unavailable。
- API、database、login、正式 Web UI / frontend / UI Read Model 均未实现；Gate B PASS 不表示整个 Cockpit 已可实现。
- timezone 计算记录 `tzdata_version`；本轮确定性验证针对同一 tzdata 环境。若未来运行环境的 IANA timezone database 升级，历史本地日边界的再现需按记录的 tzdata version 解释。

## G. Final Gate

| Issue #4 Gate | 结论 | 核心证据 |
|---|---|---|
| 1. Current State | PASS | item fields、evidence trace；new/success/failure/insufficient fixtures 与 replay tests |
| 2. Due Set | PASS | 显式 `as_of` / timezone、item status、aggregate consistency fixture/test |
| 3. Explainability | PASS | evidence / adapter / policy / interval / reason / last & next due trace |
| 4. Determinism | PASS | repeatability、input shuffle、tie-break、offset equivalence、DST、future rejection、static no-wall-clock guard |
| **Phase 4 Gate** | **PASS** | 四项均由当前 main 代码、schema、fixtures、tests 与 validators 验证 |

本报告是仓库侧 Gate 结论；GitHub Issue #4 checklist / comment / closure 应在本 PR 合并后由负责人单独同步。