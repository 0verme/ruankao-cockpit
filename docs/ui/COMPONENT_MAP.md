# Component Boundary Map v0.1

> **状态**：PLANNING CONTRACT（Issue #5 · UI.8 · component map 部分）
> **边界**：本文件只冻结**组件职责边界与输入约定**；**不实现任何组件**，不选定前端框架，不定义具体 props 类型。
> **核心约束**：`component only consumes view-model`。

---

## 1. 组件输入约定（冻结）

### 1.1 唯一允许的输入

```text
component ← view-model（已投影、已标注 value_state 的只读数据）
```

### 1.2 硬约束

```text
C1  每个组件只接受 view-model 输入
C2  组件不得直接读取复杂 domain object graph
C3  组件不得调用 replay / policy / planner 计算
C4  组件不得访问事件流、taxonomy 文件或 schema
C5  组件不得使用系统当前时间判断「今天」
C6  组件不得把 null / insufficient_evidence / unavailable 归一化为 0
C7  组件不得自行排序（排序来自 engine）
C8  组件不得写回任何状态
C9  组件不得产生新的业务事实
C10 每个组件必须有明确的 empty / unavailable 行为
```

### 1.3 明确禁止

```text
❌ 巨型 Dashboard 组件（单文件承载所有卡片与所有数据逻辑）
❌ 组件内部 fetch 拼装 domain 数据
❌ 组件内部根据 accuracy 推断 mastery
❌ 组件内部根据事件时间戳推断 streak / 完成日
❌ 组件内部根据 review interval 常量计算 due
❌ 通过 props 传递「整个 ProgressState」让子组件自行取值
```

**规模约束**：单个组件文件不得同时承担 > 1 个职责域的渲染；Dashboard 必须由卡片组件组合而成，不得是单文件巨型实现。

---

## 2. 分层结构

```text
Shell 层       AppShell / TopHeader / ContextStrip / PrimaryNav
Dashboard 层   OverallProgressCard / TodayFocusCard / OperationalStatsGrid
               ExamCountdown / StudyCalendar / SubjectStatusGrid
Review 层      ReviewQueue / ReviewItemCard / DueBadge / MasteryBadge / ExplainPanel
Progress 层    ProgressSummary / TopicAccuracyList / CoverageBreakdown
               ErrorCauseBreakdown / CapabilityEvidenceList
Shared 层      EmptyState / UnavailableBadge / PolicyVersionFooter / ExplainDisclosure
```

依赖方向：

```text
Shared  ← 所有层
Shell   ← 不依赖业务组件的数据
Dashboard / Review / Progress ← view-model，互相不直接引用对方内部状态
```

---

## 3. Shell 层

| 组件 | 职责 | view-model 输入 | empty / unavailable | 禁止 |
|---|---|---|---|---|
| `AppShell` | 布局骨架（header / nav / main / aside / footer）+ landmark 语义 | 布局配置 + 全局 `unavailable[]` | 无 | 不得包含业务计算；不得成为巨型组件 |
| `TopHeader` | 产品名、考试方向、当前阶段、顶层控件入口 | `exam_direction`（user_config）、`plan_phase`（planner / TBD）、`replay` 元数据 | `plan_phase` 未知 → 不渲染；`PlanModeSwitcher` 未冻结 → 不渲染 | 不得渲染禁用态 + 假数据；不得硬编码考试方向 |
| `ContextStrip` | 展示白名单高频上下文 | `exam_direction` / `subject` / `daily_available_minutes` / `target`（user_config）、`policy_version` 摘要 | 未配置 → `not_configured` | 不得成为信息垃圾带；不得放入无消费方字段 |
| `PrimaryNav` | 一级导航与当前路由高亮 | 路由配置 | Future 入口（论文）显示不可用说明 | 不得创建无 user job 的入口；不得创建 `/admin`、`/login`、`/community` |

**`PolicyVersionFooter` 归属**：由 `AppShell` 在页脚统一渲染（见第 6 节）。

---

## 4. Dashboard 层

### 4.1 `OverallProgressCard`

| 项 | 内容 |
|---|---|
| 职责 | 回答「我现在准备得怎么样」，渲染三科**非同构**维度 |
| view-model | `CockpitDashboardView.overall` |
| 子组件 | 可选 `ReadinessRing`（文本等价的圆环）、`SubjectReadinessList` |
| empty | `global.attempt_count = 0` → 「未评估 —— 尚无综合题作答」 |
| unavailable | 论文维度 → `UnavailableBadge`（`essay-contract`）；mastery domain fields 已 Available（Gate B PASS），但组件 / Read Model 代码未实现 |
| 禁止 | 为三科补齐同构字段；把三科压成一个百分比；把 `accuracy` 标注为 mastery |

### 4.2 `TodayFocusCard`

| 项 | 内容 |
|---|---|
| 职责 | 回答「我今天应该做什么」 |
| view-model | `TodayPlanView`（当前不可用） |
| 子组件 | `TodayThemeHeader`、`TodayTaskList`、`StartTodayCTA` |
| empty | 当前状态：「Planner 尚未生成计划」（P5.3 contract frozen；Phase 5 Gate 未通过）；有效 output 中 `days[0].tasks=[]` 是不同状态 |
| unavailable | PlannerOutput generation → Gate C；结构见 P5.3 `PlannerOutput.days[0]`，复习 domain output 已 Available（Gate B PASS），当前无 UI / Read Model implementation |
| 禁止 | 生成 / 拆分 / 补全 / 重排任务；硬编码 Day 1..30；渲染指向伪造任务流的 CTA |

### 4.3 `OperationalStatsGrid`

| 项 | 内容 |
|---|---|
| 职责 | 渲染运营统计 tile 网格 |
| view-model | `CockpitDashboardView.stats` |
| 子组件 | `StatTile` × N |
| empty | `value_state = empty` → 「尚无数据」 |
| unavailable | Phase 4 fields 从 replay 可用；只有未冻结的 `future` tile 显示 `UnavailableBadge` 与依赖名 |
| 禁止 | tile 无来源声明；把 `null` 渲染为 0；用 UI 推断 `streak` |

**`StatTile` 约束**：每个 tile 必须显式声明 `data source` 与 `unavailable semantics`；不得出现无来源的 tile。

### 4.4 `ExamCountdown`

| 项 | 内容 |
|---|---|
| 职责 | 展示目标考试日期与剩余天数 |
| view-model | `countdown`（`exam_date` 属于 Future 配置；P5.2 User Configuration v0.1 不包含该字段） |
| empty / unavailable | 考试日期暂无正式配置 contract；冲刺阶段不属于 P5.3 output → `UnavailableBadge` |
| 禁止 | 硬编码考试日期；使用浏览器本地时间计算剩余天数；把剩余天数写回 domain |

### 4.5 `StudyCalendar`

| 项 | 内容 |
|---|---|
| 职责 | 展示时间窗口内的事实与状态分布 |
| view-model | `CalendarView` |
| 子组件 | `CalendarLegend` |
| empty | 「本月无学习记录」 |
| unavailable | `due/overdue` domain Available（Gate B PASS）；`assessment` → `assessment-contract`；`completed` → `task-execution-contract`（未解锁图例项不渲染） |
| 禁止 | 把「有事件」渲染为「已完成」；使用本地时区决定日期归属 |

### 4.6 `SubjectStatusGrid`

| 项 | 内容 |
|---|---|
| 职责 | 三科状态卡（模型分离） |
| view-model | `SubjectStatusView` |
| 子组件 | `SubjectStatusCard` × 3 |
| empty | 综合 → 「未评估」；案例 → 「证据不足」；论文 → 「尚未建立契约」 |
| unavailable | review debt domain Available（Gate B PASS，Read Model 未实现）；论文全部字段 → `essay-contract` |
| 禁止 | 三卡同构化；把案例 score_ratio 当考试分数；把 insufficient_evidence 渲染为 0 或红 |

---

## 5. Review 层

| 组件 | 职责 | view-model 输入 | empty / unavailable | 禁止 |
|---|---|---|---|---|
| `ReviewQueue` | 渲染 engine 给出的有序队列 | `ReviewQueueView`（含 engine `item_order`；Gate B PASS 后 domain input Available） | 无到期项 → 「今天没有到期的复习」；UI / Read Model 尚未实现 | 重新排序；自行分组；自行分页截断而不标注 |
| `ReviewItemCard` | 渲染单个 review item | `items[]` 中的一项 | 不适用 | 混用不同粒度的进度条；把 mastery 与 due 合并成一个字段 |
| `DueBadge` | 表达 scheduling status | `review_status`（Available from replay） | 无 due → 不渲染 | 由 UI 用 `last_event_at + 常量` 计算；只显示红点而无文案 |
| `MasteryBadge` | 表达 mastery status | `mastery_state`（Available from replay） | `insufficient_evidence` → 中性灰「证据不足」 | 由 `topic accuracy` / `capability score_ratio` 推导；用红色表达证据不足 |
| `ExplainPanel` | 展开原因链 | `ExplainView` | engine 未输出原因 → 「原因不可用」 | 生成推测性解释；展示未经 engine 输出的 rule / policy |

**`ReviewItemCard` 必须显示 `item_kind`**（`topic` / `question` / `case_capability`），并使用 replay 输出的 stable `review_item_id`。

**已冻结字段可进入 view-model 设计**：P4.1～P4.5 已提供 `review_item_id` / `item_kind` / `canonical_ref` / `mastery_state` / `review_status` / `review_interval_days` / `next_due_at` / `next_due_local_date` / `mastery_reason` / `review_status_reason` / `scheduling_reason` / `last_review_at` / `last_evidence_id` 及各计数。domain replay 可渲染；正式 UI read model 仍未实现。

---

## 6. Progress 层

| 组件 | 职责 | view-model 输入 | empty / unavailable | 禁止 |
|---|---|---|---|---|
| `ProgressSummary` | 组合进度明细区块 | `ProgressSummaryView` + `MasteryReviewState v0.1` projection | mastery domain fields Available（Gate B PASS）；组件 / Read Model 未实现 | 把 `topic accuracy` 标注为 mastery |
| `TopicAccuracyList` | 渲染 topic 级事实正确率 | `topics[]` | 某 topic `attempt_count = 0` → 「未评估」（不是 0%） | 用 accuracy 颜色暗示 mastery；隐藏 `attempt_count` |
| `CoverageBreakdown` | 渲染 L1 / L2 / L3 覆盖 | `coverage` | 分母为 0 → `empty` | 把 taxonomy 分母描述为「考试权重覆盖」 |
| `ErrorCauseBreakdown` | 渲染错误归因分布 | `errors` | 无已分类错误 → `error_cause_mix = empty`（不是 0%） | 把 `unclassified_error_count` 静默并入某一类；隐藏 mix 的分母 |
| `CapabilityEvidenceList` | 渲染 capability 得分与证据状态 | `capabilities[]` | `insufficient_evidence` → 中性灰「证据不足」 | 用案例总分填充 capability；把证据不足渲染为 0 或红 |

---

## 7. Shared 层

| 组件 | 职责 | 输入 | 约束 |
|---|---|---|---|
| `EmptyState` | 统一表达「没有数据」并说明原因 | `reason_key` + 文案 | 必须说明**为什么**没有数据；不得显示 0 |
| `UnavailableBadge` | 统一表达 Future / 依赖未冻结 | `dependency` + `gate` | 必须显示依赖名；不得只显示一个灰色标记 |
| `PolicyVersionFooter` | 展示可复现所需的版本与 `as_of` | `as_of` / `timezone` / `event_schema_version` / `replay_rule_version` / `taxonomy_version` / `capability_version` / `policy_version?` | 默认折叠；不得展示未冻结的版本号（不得虚构） |
| `ExplainDisclosure` | 折叠容器，承载 Explain 内容 | `expanded` + 子内容 | 键盘可达（`button` + `aria-expanded`）；默认折叠；Explain 动效尊重 `prefers-reduced-motion` |

---

## 8. 值状态与颜色的组件归属

| 值状态 | 归属组件 | 表达 |
|---|---|---|
| `available` | 各业务组件 | 真实值 |
| `empty` | `EmptyState` | 「尚无数据 / 未评估」+ 原因 |
| `insufficient_evidence` | `EmptyState` / 业务组件内联 | 「证据不足」+ 中性灰 |
| `not_configured` | `EmptyState` | 「未配置」+ 前往设置 |
| `unavailable_future` | `UnavailableBadge` | 「尚未建立契约」/「依赖 X v0.1」 |

**约束**：状态判断在 view-model 投影层完成；组件不得自行推断 `value_state`。

---

## 9. 组件 × 依赖矩阵

| 组件 | Gate A | Gate B（Issue #4，PASS） | Gate C（Planner） | User Config | Future contract |
|---|---|---|---|---|---|
| `AppShell` / `PrimaryNav` / `ContextStrip` | — | — | 🟡（阶段字段） | ✅ | — |
| `TopHeader` | ✅（replay 元数据） | — | 🟡（`PlanModeSwitcher` 不渲染） | ✅ | — |
| `OverallProgressCard` | ✅ | ✅ domain fields Available；UI 未实现 | — | — | 🟡（论文） |
| `TodayFocusCard` | — | ✅ Review fields Available；UI 未实现 | ❌ Planner tasks 阻塞 | 🟡 | — |
| `OperationalStatsGrid` | ✅ | ✅ due / mastery fields Available；UI 未实现 | — | — | 🟡（plan / assessment / streak） |
| `ExamCountdown` | — | — | 🟡（冲刺阶段） | ✅ | — |
| `StudyCalendar` | ✅（有学习记录） | ✅ due / overdue Available；UI 未实现 | — | ✅ | 🟡（assessment / completion） |
| `SubjectStatusGrid` | ✅ | ✅ review debt Available；UI 未实现 | — | — | 🟡（论文） |
| `ReviewQueue` 系列 | — | ✅ PASS；domain input Available，UI 未实现 | — | ✅（timezone） | — |
| `ProgressSummary` 系列 | ✅ | ✅ PASS；domain mastery Available，UI 未实现 | — | — | — |
| `EmptyState` / `UnavailableBadge` / `PolicyVersionFooter` / `ExplainDisclosure` | ✅ | ✅ | ✅ | ✅ | ✅ |

图例：✅ 可用 · 🟡 部分 / 降级 · ❌ 阻塞

---

## 10. 可选子组件（命名建议，不冻结）

以下命名出现在 Issue #5 的组件草案中。它们**不是必须实现的组件**，但若实现，必须遵守本文件的输入约定。

```text
ReadinessRing              圆环可视化（必须提供文本等价）
SubjectReadinessList       三科维度列表
StatTile                   单个统计 tile（必须声明 data source）
TodayThemeHeader           今日主题头
TodayTaskList              今日任务列表
StartTodayCTA              开始按钮
CalendarLegend             日历图例
SubjectStatusCard          单科状态卡
PlanTimeline / PlanDayAccordion / PlanMilestoneBadge    （Planner 冻结后）
DailyNoteCard              （Future；默认折叠）
```

---

## 11. 与其余 UI 文档的关系

| 关注点 | 文档 |
|---|---|
| 卡片数据语义 | [`COCKPIT_UI_BLUEPRINT.md`](COCKPIT_UI_BLUEPRINT.md) |
| view-model 字段与值状态 | [`READ_MODEL_CONTRACT.md`](READ_MODEL_CONTRACT.md) |
| 指标 → domain 映射 | [`DOMAIN_TO_UI_MAPPING.md`](DOMAIN_TO_UI_MAPPING.md) |
| Review 呈现规则 | [`REVIEW_MASTERY_UX.md`](REVIEW_MASTERY_UX.md) |
| Today / Plan 呈现规则 | [`TODAY_PLANNER_UX.md`](TODAY_PLANNER_UX.md) |
| 无障碍要求 | [`RESPONSIVE_ACCESSIBILITY.md`](RESPONSIVE_ACCESSIBILITY.md) |
| 语义色 | [`DESIGN_DIRECTION.md`](DESIGN_DIRECTION.md) |
