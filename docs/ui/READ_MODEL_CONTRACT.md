# UI Read Model Consumer Contract v0.1

> **状态**：PLANNING CONTRACT（Issue #5 · UI Read Model Requirements）
> **边界**：本文件只定义**消费契约（consumer contract）**。**不定义 API、不定义传输协议、不写实现、不产生 fixture。**
> **顺序声明**：本文件定义未来 UI 的只读 consumer contract，不是 Cockpit 整体实现已经就绪的证明。Gate B（Review / Mastery）已 PASS；各 consumer 仍须满足其适用 Gate：Planner-bound Today / Plan 需 Gate C，正式前端还受 Read Model / Gate D 范围约束。

---

## 1. Read Model 的定位

```text
事实源：Immutable Progress Events（append-only）
派生层：ProgressState / MasteryReviewState / Plan（deterministic replay）
展示层：UI Read Model（本文件）
```

### 1.1 四条硬约束

```text
Read Model 可以派生
Read Model 可以缓存
Read Model 可以重建

Read Model 不能成为事实源
Read Model 不能被写回 domain
Read Model 不能产生新的业务事实
```

| 允许 | 禁止 |
|---|---|
| 从 replay 输出投影出 UI 友好字段（包括已由 Phase 4 定义的 mastery / due） | 在 read model 中计算 domain 未定义的指标（如 Planner 未冻结时的计划完成度） |
| 为性能缓存 read model | 把缓存当作唯一事实来源 |
| 删除后从 events 重建 | 把 read model 写回 events / ProgressState / MasteryReviewState |
| 重命名 / 聚合已有字段用于展示 | 生成新的「业务事实」（例如把「有事件」升级为「已完成」） |
| 用 `as_of` 生成可复现视图 | 隐式使用系统当前时间 |

### 1.2 与「domain contract」的边界

```text
read model 字段语义 ≈ domain 字段语义（可投影，不可变形）
read model 字段语义 ≠ domain 字段语义时 → 视为新事实，禁止
```

例：

```text
允许：global.accuracy → dashboard.overall.comprehensive.accuracy（同义投影）
禁止：capabilities[*].score_ratio → dashboard.overall.paper.score（跨维度造事实）
```

---

## 2. 通用信封（Common Envelope）

所有 read model 必须携带同一组版本与时间元数据。

| 字段 | 来源分类 | 当前是否可得 | 说明 |
|---|---|---|---|
| `view_version` | `projection` | ✅ 本文件冻结为 `ui-readmodel/v0.1` | read model 自身的契约版本 |
| `as_of` | `projection` | ✅ 必须显式传入 | 视图对应的时间点；不允许隐式 `now()` |
| `timezone` | `user_config` | ✅ 必须显式 | 日历日边界依据 |
| `event_schema_version` | `aggregate` | ✅ `progress-event/v0.1` | 事实事件契约版本 |
| `replay_rule_version` | `aggregate` | ✅ `progress-replay/v0.1` | Progress replay 规则版本 |
| `taxonomy_version` | `aggregate` | ✅ taxonomy v0.1 | Knowledge Topic 契约版本 |
| `capability_version` | `aggregate` | ✅ capability v0.1 | Case Capability 契约版本 |
| `mastery_policy_version` | `phase4` | ✅ 已冻结：`mastery-policy/spaced-consecutive/v0.1`（由 P4.5 replay 输出） | Mastery 状态机 policy 版本 |
| `review_policy_version` | `phase4` | ✅ 已冻结：`review-policy/simple-ladder/v0.1`（由 P4.5 replay 输出） | Review scheduling policy 版本 |
| `policy_version` | `future` | ❌ `TBD — dependent on Planner contract` | 计划策略版本 |
| `plan_version` | `future` | ❌ `TBD — dependent on Planner contract` | 计划实例版本 |
| `unavailable[]` | `projection` | ✅ | 显式列出本视图中不可用的指标及其依赖 |

**信封约束**：

```text
1. `as_of` 与 `timezone` 缺失时，read model 视为无效（不得回退到系统时间）
2. 当视图包含 Phase 4 数据时，`mastery_policy_version` / `review_policy_version` 必须使用 replay 输出的版本；Planner / Future 版本在对应契约冻结前仍允许为空，并须在 `unavailable[]` 中声明
3. 版本字段只读，不得由 UI 覆写
4. UI 必须展示（至少在 Explain / Footer 层）`as_of` + `replay_rule_version`
```

---

## 3. 值状态模型（Value State）

为避免 `null != 0` 与 `insufficient_evidence != 0` 被抹平，所有可选字段必须采用显式值状态，而不是裸 `null`。

| `value_state` | 含义 | UI 表达 | 颜色 |
|---|---|---|---|
| `available` | 有证据，且值为真实结果 | 直接显示值 | 根据语义色 |
| `empty` | 分母为 0（确实没有尝试 / 没有会话 / 没有 item） | 「未评估」/「尚无数据」 | 中性灰 |
| `insufficient_evidence` | 有引用但证据不足（例如 capability 无 score evidence） | 「证据不足」 | 中性灰 |
| `not_configured` | 用户尚未配置（例如考试日期 / 时区） | 「未配置」+ 前往设置 | 中性灰 |
| `unavailable_future` | 依赖的 contract 尚未冻结 | 「尚未建立契约」/「依赖 X v0.1」 | 中性灰 |

**硬约束**：

```text
1. `empty` / `insufficient_evidence` / `not_configured` / `unavailable_future` 一律不得渲染为 0 或 0%
2. `available` 且值为 0 时，必须明确显示 0（这是真实事实）
3. 不得用 `null` 同时表示上述四种不同语义；必须通过 `value_state` 区分
4. `value_state` 由 read model 投影决定，不由组件自行推断
```

**建议形状（示意，非实现）**：

```jsonc
// 示意：仅表达值状态的存在，不构成 schema
{
  "value": null,
  "value_state": "insufficient_evidence",
  "reason_key": "capability_without_score_evidence",
  "source_ref": "capabilities.CASE.DATA_DESIGN.evidence_status"
}
```

---

## 4. 不可用表达的通用形状

`unavailable[]` 的每一项必须包含依赖信息，供 UI 生成可行动文案：

| 字段 | 说明 |
|---|---|
| `target` | 视图内的字段路径（如 `overall.paper`、`stats.due_count`） |
| `reason` | 枚举：`no_contract` / `dependency_open` / `not_configured` / `requires_gate` |
| `dependency` | 依赖标识：`issue-4` / `planner-contract` / `assessment-contract` / `essay-contract` / `task-execution-contract` / `user-config` |
| `gate` | 对应的 Gate：`B` / `C` / `D` / `none` |

**禁止**：把不可用项从返回结构中静默删除。UI 必须能区分「字段不存在」与「字段存在但当前不可用」。

---

## 5. Read Model 清单

| Read Model | 主要 consumer | 依赖 | 当前可否实现 |
|---|---|---|---|
| `CockpitDashboardView` | Dashboard `/` | Gate A + User Config + Gate B + Gate C | 🟡 Progress 可用；Review domain inputs Available（Gate B PASS），Today 仍受 Gate C 阻塞；View 未实现 |
| `TodayPlanView` | `/today`、`TodayFocusCard` | Gate C（Planner）+ Gate B（Review data 可消费） | ❌ Planner contract 未冻结；Review domain data Available |
| `SubjectStatusView` | `SubjectStatusGrid` | Gate A + Gate B + essay contract | 🟡 部分（论文不可用） |
| `ReviewQueueView` | `/review`、`ReviewQueue` | Gate B（Issue #4） | ✅ Gate B PASS、所有 domain inputs Available；UI Read Model / frontend 未实现 |
| `CalendarView` | `StudyCalendar` | Gate A + Gate B + assessment contract | 🟡 部分（只有「有学习记录」） |
| `ProgressSummaryView` | `/progress` | Gate A + Gate B | ✅ Gate A / B PASS、Progress 与 mastery domain inputs Available；UI Read Model 未实现 |
| `ExplainView` | `ExplainPanel` / `/explain/:kind/:id` | 取决于被解释对象 | 🟡 部分 |

---

### 5.1 `CockpitDashboardView`

| 项 | 内容 |
|---|---|
| **purpose** | 支撑首屏四问：整体怎么样 / 今天做什么 / 哪些要复习 / 离目标多远 |
| **consumer** | `/` Dashboard、`OverallProgressCard`、`TodayFocusCard`、`OperationalStatsGrid`、`ExamCountdown`、`StudyCalendar`、`SubjectStatusGrid` |
| **source categories** | `aggregate` + `projection` + `user_config` + `phase4` + `planner` + `future` |
| **version metadata** | 通用信封 + P4.5 `mastery_policy_version` / `review_policy_version`；`plan_version` 仍 TBD |
| **as_of** | 必填；所有子区块共享同一 `as_of`（禁止一个视图内混用多个时间点） |
| **timezone semantics** | 必填；日历区块与倒计时依赖它确定日历日边界 |
| **null semantics** | 每个数值字段必须带 `value_state`；`global.accuracy = null` → `empty`；`capabilities[*].evidence_status = insufficient_evidence` → 同名字段 |
| **future / unavailable** | `overall.paper` → `no_contract` / `essay-contract`；`today.*` → `dependency_open` / `planner-contract`（Gate C）；`review.*`、`stats.due_count`、`stats.mastery_distribution` 可由 `MasteryReviewState v0.1` domain replay 提供，但 dashboard read model 尚未实现；`stats.plan_completion` / `stats.recent_assessment` / `stats.streak` → `no_contract` |

**区块结构（规划）**

```text
envelope
overall
  comprehensive { attempt_count, accuracy, coverage, error_note }
  case          { attempt_count, scored_attempt_count, score_ratio, capability_hint }
  paper         → unavailable_future
today
  → unavailable_future（Planner）或完整 TodayPlanView 区块
review
  → replay-derived due 摘要（正式 ReviewQueue read model 未实现）
stats
  study_minutes / session_count / accuracy / coverage / errors / case_score_ratio  （available）
  due_count / mastery_distribution                                                 （phase4）
  plan_completion / recent_assessment / streak                                     （future）
countdown
  exam_date / days_remaining（需 not_configured 分支）
calendar
  → CalendarView 摘要
subjects
  → SubjectStatusView
unavailable[]
```

---

### 5.2 `TodayPlanView`

| 项 | 内容 |
|---|---|
| **purpose** | 回答「我今天应该做什么」，并提供开始入口 |
| **consumer** | `/today`、`TodayFocusCard`、`/plan` 的当日区块 |
| **source categories** | `planner` + `phase4` + `projection` |
| **version metadata** | 通用信封 + `plan_version` + `policy_version`（均 `TBD — dependent on Planner contract`） |
| **as_of** | 必填；必须与 Planner 生成计划时的 `as_of` 语义一致 |
| **timezone semantics** | 必填；决定「今天」是哪一天（日历日边界） |
| **null semantics** | 无计划 → 不返回伪造任务；返回 `value_state = unavailable_future`，或返回带空任务列表的显式空态（由 Planner 契约决定） |
| **future / unavailable** | Planner 任务字段 → `no_contract` / `planner-contract` / Gate C；`review.due_count` domain replay 可用，但 Today read model / queue consumer 尚未实现 |

**规划字段（字段名与枚举均为 TBD）**

```text
day_index                                   TBD — dependent on Planner contract
plan_phase                                  TBD — dependent on Planner contract
day_type                                    TBD — dependent on Planner contract
theme.primary_topic_id                      TBD — dependent on Planner contract
theme.supporting_topic_ids                  TBD — dependent on Planner contract
theme.capability_ids                        TBD — dependent on Planner contract
capacity.planned_minutes                    TBD — dependent on Planner contract
capacity.tier                               TBD — dependent on Planner contract
tasks[].id                                  TBD — dependent on Planner contract
tasks[].type                                TBD — dependent on Planner contract
tasks[].ref                                 TBD — dependent on Planner contract
tasks[].est_minutes                         TBD — dependent on Planner contract
tasks[].required                            TBD — dependent on Planner contract
review.due_count                            ✅ P4.5 replay 输出（unit = review_item）
review.overdue_count                        ✅ P4.5 replay 输出
cta_target                                  TBD — dependent on Planner contract
explain.rule_ids / explain.signal_snapshot  TBD — dependent on Planner contract
```

**约束**：

```text
1. 本视图不得包含任何由 UI 生成的任务
2. 本视图不得包含 docs/30_DAY_CURRICULUM_DRAFT.md 中的固定天数、间隔或阈值
3. `theme.*` 中的 topic 与 capability 必须分字段返回，不得合并
4. 无计划时必须可区分「未冻结」与「今天确实没有任务」
```

---

### 5.3 `SubjectStatusView`

| 项 | 内容 |
|---|---|
| **purpose** | 三科各自的真实状态（**模型不强制同构**） |
| **consumer** | `SubjectStatusGrid`、`OverallProgressCard` 的三科维度 |
| **source categories** | `aggregate`（综合 / 案例）+ `phase4`（review debt）+ `future`（论文） |
| **version metadata** | 通用信封 + P4.5 `mastery_policy_version` / `review_policy_version` |
| **as_of** | 必填 |
| **timezone semantics** | 对 review debt 的「今天」判断必需；纯 aggregate 区块可忽略，但仍需携带 |
| **null semantics** | 综合：`attempt_count = 0` → `empty`；案例：capability 无 evidence → `insufficient_evidence`；论文：`unavailable_future` |
| **future / unavailable** | 论文全部字段 → `no_contract` / `essay-contract`；`review_debt` domain replay 可用，正式 SubjectStatus read model 未实现 |

**三科结构差异（冻结，禁止同构化）**

| 科目 | 字段 | 状态 |
|---|---|---|
| 综合 | `attempt_count` / `accuracy` / `coverage` / `error_summary` / `review_debt`（Phase 4） | 🟡 部分 |
| 案例 | `attempt_count` / `scored_attempt_count` / `score_ratio` / `capability_evidence[]` | 🟡 可用 |
| 论文 | 无 | ❌ `unavailable_future` |

**约束**：

```text
1. 三科不得共用一个「mastery 百分比」字段
2. 案例的 score_ratio 必须与 evidence_status 一起返回
3. 论文字段缺省时用 unavailable 表达，不得补造字段以求对称
```

---

### 5.4 `ReviewQueueView`

| 项 | 内容 |
|---|---|
| **purpose** | 回答「今天要复习什么、为什么」，并按 engine 的顺序呈现 |
| **consumer** | `/review`、`ReviewQueue`、`ReviewItemCard`、`DueBadge`、`MasteryBadge`、`ExplainPanel` |
| **source categories** | `phase4`（全部核心字段） |
| **version metadata** | 通用信封 + `mastery_policy_version` + `review_policy_version`（由 P4.5 replay 输出） |
| **as_of** | **必填且关键**；「今天到期」完全由 `as_of` + `review_policy_version` 决定 |
| **timezone semantics** | 必填；决定 due 的日历日归属与 overdue 的「已逾期 N 天」计算 |
| **null semantics** | 无 evidence → 不得表示为失败或 0；`insufficient_evidence` 与 `mastered` 必须可区分 |
| **future / unavailable** | ReviewQueue 的 domain 字段由 `MasteryReviewState v0.1` 提供；正式 UI read model / queue ordering consumer 仍待 UI 实现，Planner 相关字段仍为 `planner-contract` |

**domain 字段（由 replay 提供；UI read model 仍为规划）**

> 下表按 P4.3 / P4.4 的冻结记录和 P4.5 `MasteryReviewState v0.1` 输出更新。
> **domain replay 可消费 ≠ 前端已实现**：本文件仍不定义 API 或 UI 实现。

```text
items[].review_item_id                      ✅ P4.1 stable identity 已冻结并由 catalog 校验
items[].item_kind                           ✅ `topic` / `question` / `case_capability`
items[].canonical_ref                       ✅ P4.1 canonical reference
items[].mastery_state                       ✅ 已冻结：new / learning / mastered
items[].mastery_reason                      ✅ 字段名已冻结
items[].review_status                       ✅ 已冻结：not_scheduled / scheduled / due / overdue
items[].review_status_reason                ✅ 字段名已冻结
items[].scheduling_reason                   ✅ 字段名已冻结
items[].next_due_at                         ✅ 字段名与粒度已冻结（UTC instant）
items[].next_due_local_date                 ✅ 字段名与粒度已冻结（YYYY-MM-DD）
items[].last_review_at                      ✅ 字段名已冻结（UTC instant）
items[].last_evidence_id                    ✅ 字段名已冻结
items[].review_interval_days                ✅ 字段名已冻结（整数或 null）
items[].evidence[]                          ✅ evidence trace + 已冻结计数
                                            （evaluated_evidence_count / successful_review_count /
                                              failure_count / insufficient_evidence_count /
                                              consecutive_success_count / consecutive_success_day_count）
policy / outcome_adapter                    ✅ 顶层 policy identity + adapter version
item_order                                  ✅ P4.5 replay 提供稳定 lexical item 顺序；UI 不得自行重排
due_count                                   ✅ 字段名已冻结；unit = review_item，不变量 due_count == due_today_count + overdue_count
due_today_count / overdue_count              ✅ 字段名已冻结
not_scheduled_count / scheduled_count        ✅ 字段名已冻结
total_items                                  ✅ 字段名已冻结
new_count / learning_count / mastered_count  ✅ 字段名已冻结
as_of / timezone / schedule_timezone / tzdata_version ✅ P4.5 replay 输出
schema_version                               ✅ `mastery-review-state/v0.1`
```

**约束（冻结）**：

```text
1. `item_order` 必须来自 engine；UI 不得重新排序
2. `items[].item_kind` 必须返回；不同粒度的 item 不得共用同一进度条
3. mastery 与 due 必须是两个独立字段（mastery_state / review_status），不得合并成单一互斥枚举
   —— 已由 P4.3 / P4.4 确认冻结；mastered + due 是合法组合
4. `insufficient_evidence` 不得渲染为红，也不得渲染为 0
   —— P4.3 的语义是「effect = no_change，且不是 failure」
5. UI 不得调用 `engine.rules.review_policy_v01` 自行计算 item 状态；只能消费 replay 输出
6. `due_count` 不得由 UI 重算；若展示子计数，必须满足 due_count == due_today_count + overdue_count
```

---

### 5.5 `CalendarView`

| 项 | 内容 |
|---|---|
| **purpose** | 展示某时间窗口内的事实与状态分布 |
| **consumer** | `StudyCalendar`、`CalendarLegend` |
| **source categories** | `aggregate`（有学习记录）+ `phase4`（due / overdue）+ `future`（assessment / 完成日） |
| **version metadata** | 通用信封 + `review_policy_version`（由 P4.5 replay 输出） |
| **as_of** | 必填；未来事件不得泄漏到当前窗口 |
| **timezone semantics** | **必填且关键**；每一天的归属由显式 timezone 的日历日决定，不由浏览器本地时区决定 |
| **null semantics** | 某天无事件 → 该日 `has_learning_record = false`（这是真实事实），不等于「未完成」 |
| **future / unavailable** | `completed_days` → `no_contract` / `task-execution-contract`；`assessment_days` → `no_contract` / `assessment-contract`；`due_days` / `overdue_days` 可由 P4.5 domain replay 提供，Calendar read model 仍待实现 |

**规划字段**

```text
window.start / window.end                     projection（由 as_of + timezone 派生）
days[].date                                   projection（含 timezone 语义）
days[].has_learning_record                    aggregate（progress events）
days[].event_type_counts                      aggregate（可选：comprehensive / case / study）
days[].study_minutes                          aggregate
days[].completed                               TBD — task execution contract（Future）
days[].due_count / overdue_count              ✅ domain 值由 P4.5 replay 提供；Calendar read model 待实现
days[].has_assessment                         TBD — assessment contract（Future）
legend                                        projection
```

**约束（冻结）**：

```text
有学习事件 != 完成学习
```

在 completion contract 冻结前，`days[].completed` 与 `legend ●` 不得渲染。

---

### 5.6 `ProgressSummaryView`

| 项 | 内容 |
|---|---|
| **purpose** | 解释综合 / 案例的事实表现、覆盖与错误结构；mastery domain 值来自 `MasteryReviewState v0.1`，read model 仍待实现 |
| **consumer** | `/progress`、`ProgressSummary`、`TopicAccuracyList`、`CoverageBreakdown`、`ErrorCauseBreakdown`、`CapabilityEvidenceList` |
| **source categories** | `aggregate` + `phase4` |
| **version metadata** | 通用信封 + `mastery_policy_version`（由 P4.5 replay 输出） |
| **as_of** | 必填 |
| **timezone semantics** | 对 mastery / due 区块必需；aggregate 区块不依赖日历日，但仍必须携带 |
| **null semantics** | `global.accuracy = null` → `empty`；`topics[*].accuracy = null` → `empty`（不可用 0 代替）；`errors.error_cause_mix = null` → `empty`；capability → `insufficient_evidence` |
| **future / unavailable** | `mastery[]` domain replay 可用；ProgressSummary read model 未实现时为实现层 unavailable |

**规划字段**

```text
global           { attempt_count, correct_count, incorrect_count, accuracy }     aggregate
topics[]         { topic_id, level, attempt_count, correct_count, incorrect_count, accuracy }
coverage         { l1, l2, l3 }（covered / total / ratio）                       aggregate
errors           { error_count, classified_error_count, unclassified_error_count,
                   error_count_by_cause, error_cause_mix }                       aggregate
case             { attempt_count, scored_attempt_count, score_earned,
                   score_possible, score_ratio }                                 aggregate
capabilities[]   { capability_id, attempt_count, score_earned, score_possible,
                   score_ratio, evidence_status }                                aggregate
study            { session_count, study_minutes }                                aggregate
mastery[]        ✅ domain 值由 P4.5 replay 提供；ProgressSummary read model 待实现
meta             { replayed_event_count, schema_version, replay_rule_version,
                   taxonomy_version, capability_version }                        aggregate
```

**约束**：

```text
1. coverage 必须与「分母 = taxonomy 节点数」的说明一起返回/展示
2. topic accuracy 不得标注为 mastery
3. capability 必须同时返回 evidence_status
4. error_cause_mix 必须与 unclassified_error_count 一起展示，避免误读分母
```

---

### 5.7 `ExplainView`

| 项 | 内容 |
|---|---|
| **purpose** | 为任意状态 / 任务 / 指标提供可复现的原因链 |
| **consumer** | `ExplainPanel`、`ExplainDisclosure`、`/explain/:kind/:id` |
| **source categories** | 取决于被解释对象：`aggregate` / `phase4` / `planner` / `projection` |
| **version metadata** | 通用信封 + 被解释对象所属的 policy 版本（`replay_rule_version` / `mastery_policy_version` / `review_policy_version` / `plan_version`） |
| **as_of** | 必填；解释结果必须绑定生成时的 `as_of` |
| **timezone semantics** | 涉及日期边界（due / 日历日）时必填 |
| **null semantics** | engine 未输出原因 → `reason_available = false`，UI 显示「原因不可用」。**不得由 UI 生成推测性解释** |
| **future / unavailable** | 依赖对象未冻结时（`review_item` / `plan_task`）→ `dependency_open` + 对应 dependency |

**规划字段**

```text
subject_kind                     projection（progress / capability / review_item / plan_task / metric）
subject_id                       projection（必须是稳定 canonical id，不得是展示名称）
reason_available                 projection
evidence[]                       aggregate / phase4 / planner（随 subject_kind）
policy_id / policy_version       取决于对象
rule_id                          planner / phase4
signal_snapshot                  planner / phase4
transition_reason                phase4
as_of                            envelope
versions                         envelope
```

**约束（冻结）**：

```text
1. Explain 内容只能来自 engine 输出
2. `subject_id` 不得是展示名称、题干或自由文本
3. 深链必须能确定 `as_of`，否则解释不可复现
4. Explain 默认折叠（Progressive Disclosure）
5. AI 不得生成事实型结论；只允许表达润色
```

---

## 6. 时区与 `as_of` 语义

| 规则 | 内容 |
|---|---|
| T1 | `as_of` 必须是 timezone-aware instant；naive 时间视为无效 |
| T2 | 日历日归属由显式 `timezone` 决定，不由浏览器本地时区决定 |
| T3 | 同一 `(events, policy, as_of, timezone)` 必须产生完全一致的 read model |
| T4 | `as_of` 早于事件发生时间时，必须显式拒绝或标记 future-evidence，**不得静默泄漏未来事实** |
| T5 | 不得在 read model 投影中调用系统当前时间 |
| T6 | 若视图跨越 DST 边界，必须记录 timezone 与日历语义 |

**已解决（曾为未决）**：`next_due_at` 的粒度已由 P4.4 冻结为“同时保存 UTC instant 与 local date”，canonical = instant；due 边界含，overdue 从下一个本地 00:00 起；时区必须显式传入 IANA `schedule_timezone`。`review_due_at` 不是本仓库的字段名，已统一为 `next_due_at` / `next_due_local_date`。

---

## 7. 版本元数据清单

| 版本字段 | 当前值 / 状态 |
|---|---|
| `event_schema_version` | `progress-event/v0.1` ✅ |
| `replay_rule_version` | `progress-replay/v0.1` ✅ |
| `taxonomy_version` | taxonomy v0.1 ✅ |
| `capability_version` | capability v0.1 ✅ |
| `state_schema_version` | `progress-state/v0.1` ✅ |
| `mastery_policy_version` | ✅ `mastery-policy/spaced-consecutive/v0.1`（由 P4.5 replay 输出） |
| `review_policy_version` | ✅ `review-policy/simple-ladder/v0.1`（由 P4.5 replay 输出） |
| `review_projection_schema_version` | ✅ `review-policy-projection/v0.1`；MasteryReviewState 顶层 schema 为 `mastery-review-state/v0.1` |
| `schedule_timezone` | ✅ 字段名已冻结；必填、无隐式默认 |
| `tzdata_version` | ✅ 字段名已冻结 |
| `policy_version` | `TBD — dependent on Planner contract` |
| `plan_version` | `TBD — dependent on Planner contract` |
| `assessment_version` | `TBD — assessment contract 未冻结` |
| `essay_version` | `TBD — essay contract 未冻结` |
| `as_of` | 每次视图请求必须显式提供 |
| `timezone` | 每次视图请求必须显式提供 |

**约束**：

```text
1. 不得为了文档完整性虚构 Phase 4 / Planner / Assessment / Essay 的最终 schema 或版本号
2. 版本字段必须随视图返回，以便历史结果可复现
3. 版本变化时，映射表与 read model 契约必须同步更新
```

**已知 draft（不得当作本契约的字段来源）**：

```text
data/review/fixture-schema.draft.json → review-fixture/v0.1-draft（status: draft, frozen: false）
```

它是 Phase 4 **测试 fixture** 的字段骨架，不是 `MasteryReviewState`，也不是 UI read model 契约。

**方向相反的情况**：`docs/review/POLICY_SYMBOL_FREEZE_V01.md` 是**正式冻结契约**，其 policy 层字段名与枚举已直接用于本文件的 `ReviewQueueView`；MasteryReviewState 顶层对象名与 `schema_version` 已由 P4.5 冻结，UI 仍不得从 policy kernel 自行拼装。

---

## 8. Gate 与实现的对应关系

| Gate | 解锁的 read model 部分 |
|---|---|
| Gate A ✅ | `ProgressSummaryView` 的 aggregate 区块、`CalendarView.has_learning_record`、`SubjectStatusView` 的综合 / 案例区块 |
| Gate B ✅ PASS | P4.1～P4.9 全部 Gate 问题已验证；`ReviewQueueView` 所需 mastery / scheduling / explain domain fields Available；正式 UI Read Model 与 frontend 仍未实现 |
| Gate C ❌ | `TodayPlanView` 全部、`CockpitDashboardView.today`、`ExplainView`（plan 对象） |
| Gate D 🟡 | 本文件只定义 consumer contract；Gate B 已 PASS，但完整 Cockpit Read Model 的 Gate D 仍需收口 Planner-bound / Future view fields（Gate C 仍未通过） |
| Gate 之外 | `essay` / `assessment` / `resources` 相关部分 |

**结论**：

```text
本文件 = Gate D 的输入，不是 Gate D 的完成
在 Gate B / C 通过前，禁止开始正式前端实现
```

---

## 9. 明确不做的事

```text
❌ 不定义 API endpoint / 传输协议 / 序列化格式
❌ 不定义数据库 / 缓存实现
❌ 不产生任何 fixture 或 mock 数据
❌ 不重新定义或改写已冻结的 Phase 4 字段；Planner / Assessment / Essay 等未冻结 contract 仍不得猜造
❌ 不引入任何由 read model 生成的新业务事实
❌ 不把 read model 写回 domain
```
