# UI Read Model Consumer Contract v0.1

> **状态**：PLANNING CONTRACT（Issue #5 · UI Read Model Requirements）
> **边界**：本文件只定义**消费契约（consumer contract）**。**不定义 API、不定义传输协议、不写实现、不产生 fixture。**
> **顺序声明**：本文件不是 Cockpit 实现的前置冻结条件。它描述「未来 UI 期望收到什么形状的只读视图」，实现仍需 Gate B / C / D 全部通过。

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
| 从 replay 输出投影出 UI 友好字段 | 在 read model 中计算 domain 未定义的指标（如 mastery / due / plan completion） |
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
| `mastery_policy_version` | `phase4` | ❌ `TBD — dependent on Issue #4` | Mastery 状态机 policy 版本 |
| `review_policy_version` | `phase4` | ❌ `TBD — dependent on Issue #4` | Review scheduling policy 版本 |
| `policy_version` | `future` | ❌ `TBD — dependent on Planner contract` | 计划策略版本 |
| `plan_version` | `future` | ❌ `TBD — dependent on Planner contract` | 计划实例版本 |
| `unavailable[]` | `projection` | ✅ | 显式列出本视图中不可用的指标及其依赖 |

**信封约束**：

```text
1. `as_of` 与 `timezone` 缺失时，read model 视为无效（不得回退到系统时间）
2. `phase4` / `future` 版本字段在对应契约冻结前允许为空，但必须在 `unavailable[]` 中显式声明
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
| `CockpitDashboardView` | Dashboard `/` | Gate A + User Config + Gate B + Gate C | 🟡 部分（不含 Today / Review 区块） |
| `TodayPlanView` | `/today`、`TodayFocusCard` | Gate C + Gate B | ❌ 未冻结 |
| `SubjectStatusView` | `SubjectStatusGrid` | Gate A + Gate B + essay contract | 🟡 部分（论文不可用） |
| `ReviewQueueView` | `/review`、`ReviewQueue` | Gate B（Issue #4） | ❌ 未冻结 |
| `CalendarView` | `StudyCalendar` | Gate A + Gate B + assessment contract | 🟡 部分（只有「有学习记录」） |
| `ProgressSummaryView` | `/progress` | Gate A + Gate B | 🟡 部分（mastery 区块不可用） |
| `ExplainView` | `ExplainPanel` / `/explain/:kind/:id` | 取决于被解释对象 | 🟡 部分 |

---

### 5.1 `CockpitDashboardView`

| 项 | 内容 |
|---|---|
| **purpose** | 支撑首屏四问：整体怎么样 / 今天做什么 / 哪些要复习 / 离目标多远 |
| **consumer** | `/` Dashboard、`OverallProgressCard`、`TodayFocusCard`、`OperationalStatsGrid`、`ExamCountdown`、`StudyCalendar`、`SubjectStatusGrid` |
| **source categories** | `aggregate` + `projection` + `user_config` + `phase4` + `planner` + `future` |
| **version metadata** | 通用信封 + `mastery_policy_version` / `review_policy_version`（TBD）+ `plan_version`（TBD） |
| **as_of** | 必填；所有子区块共享同一 `as_of`（禁止一个视图内混用多个时间点） |
| **timezone semantics** | 必填；日历区块与倒计时依赖它确定日历日边界 |
| **null semantics** | 每个数值字段必须带 `value_state`；`global.accuracy = null` → `empty`；`capabilities[*].evidence_status = insufficient_evidence` → 同名字段 |
| **future / unavailable** | `overall.paper` → `no_contract` / `essay-contract`；`today.*` → `dependency_open` / `planner-contract`（Gate C）；`review.*` → `dependency_open` / `issue-4`（Gate B）；`stats.due_count` / `stats.mastery_distribution` → 同上；`stats.plan_completion` / `stats.recent_assessment` / `stats.streak` → `no_contract` |

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
  → unavailable_future（Issue #4）或 due 摘要
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
| **future / unavailable** | 全部字段当前不可用：`no_contract` / `planner-contract` / Gate C；`review.due_count` → `dependency_open` / `issue-4` / Gate B |

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
review.due_count                            TBD — dependent on Issue #4
review.overdue_count                        TBD — dependent on Issue #4
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
| **version metadata** | 通用信封 + `mastery_policy_version` / `review_policy_version`（TBD） |
| **as_of** | 必填 |
| **timezone semantics** | 对 review debt 的「今天」判断必需；纯 aggregate 区块可忽略，但仍需携带 |
| **null semantics** | 综合：`attempt_count = 0` → `empty`；案例：capability 无 evidence → `insufficient_evidence`；论文：`unavailable_future` |
| **future / unavailable** | 论文全部字段 → `no_contract` / `essay-contract`；`review_debt` → `dependency_open` / `issue-4` / Gate B |

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
| **version metadata** | 通用信封 + `mastery_policy_version` + `review_policy_version`（均 `TBD — dependent on Issue #4`） |
| **as_of** | **必填且关键**；「今天到期」完全由 `as_of` + `review_policy_version` 决定 |
| **timezone semantics** | 必填；决定 due 的日历日归属与 overdue 的「已逾期 N 天」计算 |
| **null semantics** | 无 evidence → 不得表示为失败或 0；`insufficient_evidence` 与 `mastered` 必须可区分 |
| **future / unavailable** | 当前全部字段不可用：`dependency_open` / `issue-4` / Gate B |

**规划字段（字段名与状态枚举均为 TBD）**

```text
items[].review_item_id                      TBD — dependent on Issue #4
items[].item_kind                           TBD — dependent on Issue #4
items[].canonical_ref                       TBD — dependent on Issue #4
items[].mastery_status                      TBD — dependent on Issue #4
items[].scheduling_status                   TBD — dependent on Issue #4
items[].review_due_at                       TBD — dependent on Issue #4
items[].last_review_at                      TBD — dependent on Issue #4
items[].review_interval_days                TBD — dependent on Issue #4
items[].evidence_summary                    TBD — dependent on Issue #4
items[].transition_reason                   TBD — dependent on Issue #4
items[].policy_version                      TBD — dependent on Issue #4
order                                       TBD — dependent on Issue #4（由 engine 提供）
due_count                                   TBD — dependent on Issue #4
overdue_count                               TBD — dependent on Issue #4
```

**约束（冻结）**：

```text
1. `order` 必须来自 engine；UI 不得重新排序
2. `items[].item_kind` 必须返回；不同粒度的 item 不得共用同一进度条
3. mastery 与 due 必须是两个独立字段，不得合并成单一互斥枚举
4. `insufficient_evidence` 不得渲染为红，也不得渲染为 0
```

---

### 5.5 `CalendarView`

| 项 | 内容 |
|---|---|
| **purpose** | 展示某时间窗口内的事实与状态分布 |
| **consumer** | `StudyCalendar`、`CalendarLegend` |
| **source categories** | `aggregate`（有学习记录）+ `phase4`（due / overdue）+ `future`（assessment / 完成日） |
| **version metadata** | 通用信封 + `review_policy_version`（TBD） |
| **as_of** | 必填；未来事件不得泄漏到当前窗口 |
| **timezone semantics** | **必填且关键**；每一天的归属由显式 timezone 的日历日决定，不由浏览器本地时区决定 |
| **null semantics** | 某天无事件 → 该日 `has_learning_record = false`（这是真实事实），不等于「未完成」 |
| **future / unavailable** | `completed_days` → `no_contract` / `task-execution-contract`；`assessment_days` → `no_contract` / `assessment-contract`；`due_days` / `overdue_days` → `dependency_open` / `issue-4` / Gate B |

**规划字段**

```text
window.start / window.end                     projection（由 as_of + timezone 派生）
days[].date                                   projection（含 timezone 语义）
days[].has_learning_record                    aggregate（progress events）
days[].event_type_counts                      aggregate（可选：comprehensive / case / study）
days[].study_minutes                          aggregate
days[].completed                               TBD — task execution contract（Future）
days[].due_count / overdue_count              TBD — dependent on Issue #4
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
| **purpose** | 解释综合 / 案例的事实表现、覆盖与错误结构；mastery 部分待 Issue #4 |
| **consumer** | `/progress`、`ProgressSummary`、`TopicAccuracyList`、`CoverageBreakdown`、`ErrorCauseBreakdown`、`CapabilityEvidenceList` |
| **source categories** | `aggregate` + `phase4` |
| **version metadata** | 通用信封 + `mastery_policy_version`（TBD） |
| **as_of** | 必填 |
| **timezone semantics** | 对 mastery / due 区块必需；aggregate 区块不依赖日历日，但仍必须携带 |
| **null semantics** | `global.accuracy = null` → `empty`；`topics[*].accuracy = null` → `empty`（不可用 0 代替）；`errors.error_cause_mix = null` → `empty`；capability → `insufficient_evidence` |
| **future / unavailable** | `mastery[]` → `dependency_open` / `issue-4` / Gate B |

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
mastery[]        TBD — dependent on Issue #4
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

**已知未决**：`review_due_at` 是 instant、local date 还是二者并存的语义，`TBD — dependent on Issue #4`。在冻结前，`ReviewQueueView` / `CalendarView` 的 due 相关字段不可实现。

---

## 7. 版本元数据清单

| 版本字段 | 当前值 / 状态 |
|---|---|
| `event_schema_version` | `progress-event/v0.1` ✅ |
| `replay_rule_version` | `progress-replay/v0.1` ✅ |
| `taxonomy_version` | taxonomy v0.1 ✅ |
| `capability_version` | capability v0.1 ✅ |
| `state_schema_version` | `progress-state/v0.1` ✅ |
| `mastery_policy_version` | `TBD — dependent on Issue #4` |
| `review_policy_version` | `TBD — dependent on Issue #4` |
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

它是 Phase 4 **测试 fixture** 的字段骨架，不是 `MasteryReviewState`，也不是 UI read model 契约。本文件中的 `phase4` / `planner` 字段仍保持 `TBD`，不得从该 draft 反向推导。

---

## 8. Gate 与实现的对应关系

| Gate | 解锁的 read model 部分 |
|---|---|
| Gate A ✅ | `ProgressSummaryView` 的 aggregate 区块、`CalendarView.has_learning_record`、`SubjectStatusView` 的综合 / 案例区块 |
| Gate B ❌ | `ReviewQueueView` 全部、`CalendarView.due/overdue`、`SubjectStatusView.review_debt`、`ProgressSummaryView.mastery[]`、`ExplainView`（review 对象） |
| Gate C ❌ | `TodayPlanView` 全部、`CockpitDashboardView.today`、`ExplainView`（plan 对象） |
| Gate D 🟡 | 本文件只定义 consumer contract；**Gate D 的完整冻结（字段、来源类别、版本元数据、null / unavailable 语义全部落定）仍依赖 Gate B / C 完成** |
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
❌ 不冻结 Phase 4 / Planner 的最终字段名与状态枚举
❌ 不引入任何由 read model 生成的新业务事实
❌ 不把 read model 写回 domain
```
