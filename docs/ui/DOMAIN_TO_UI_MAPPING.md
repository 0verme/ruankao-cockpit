# Domain → UI Mapping v0.1

> **状态**：PLANNING CONTRACT（Issue #5 · UI.4）
> **边界**：本文件是 Cockpit 唯一合法的「UI 指标 → domain 字段」映射表。**不实现任何字段读取、API 或 read model 代码。**
> **原则**：任何无法映射到 domain contract 的指标，必须显式标记 `Future / Unavailable`。禁止补默认值。

---

## 1. Source Category 枚举

`Source Category` 只允许取以下值：

| 值 | 含义 |
|---|---|
| `aggregate` | 直接来自 replay 输出的聚合事实（`progress-state/v0.1`） |
| `projection` | 由 aggregate 或 user_config 确定性派生的只读投影（可重建、不产生新事实） |
| `user_config` | 用户显式配置的输入（不是 domain 事实） |
| `phase4` | Issue #4 Mastery / Review 派生层。P4.1～P4.9 已通过 Gate；domain 输出可消费，本文件不实现 UI / Read Model |
| `planner` | 依赖 Planner contract 冻结后可得 |
| `future` | 无任何 contract，当前不可用 |

**规则**：`phase4` domain fields 已 Available，可由 Review consumer 读取；`planner` / `future` 中尚未冻结或未定义的字段必须使用 `UnavailableBadge` / 空态。本映射冻结消费语义，不代表 UI / Read Model 代码已经实现。

---

## 2. Current Availability 枚举

| 值 | 含义 |
|---|---|
| `Available` | 当前 main 的 ProgressState 或 MasteryReviewState domain output 已可确定性计算（Phase 4 Gate PASS） |
| `Available (null 可能)` | 可用，但分母为 0 时值为 `null` |
| `Planner` | 未冻结 |
| `Future` | 未定义 contract |
| `User Config` | 用户输入 |

---

## 3. 主映射表 · Available（`aggregate`，Gate A ✅）

| UI Metric | UI Meaning | Domain Field | Domain Source | Source Category | Current Availability | Null Semantics | Explain Source | Notes / Constraints |
|---|---|---|---|---|---|---|---|---|
| 综合正确率 | 综合题的事实正确比例 | `global.accuracy` | `progress-state/v0.1`（`correct_count / attempt_count`） | `aggregate` | `Available (null 可能)` | `attempt_count = 0` → `null` → UI 显示「未评估」，**不显示 0%** | `global.correct_count` / `global.attempt_count` / 事件集合 / `replay_rule_version` | **不是 mastery**；不是考试分数；分母只含 `comprehensive_attempt` |
| 综合作答数 | 综合题提交次数 | `global.attempt_count` | 同上 | `aggregate` | `Available` | 无数据 → `0` 是真实事实（0 次作答），不是 null | 事件计数 | **不等于 topic attempt 之和**（multi-topic 时 1 条事件只 +1 global） |
| 综合正确数 / 错误数 | 事实计数 | `global.correct_count` / `global.incorrect_count` | 同上 | `aggregate` | `Available` | `0` 是真实事实 | 事件计数 | `correct` 是事实布尔值，不是模型判断 |
| 错题总数 | 错误事实总数 | `errors.error_count` | `progress-state/v0.1`（= `global.incorrect_count`） | `aggregate` | `Available` | 无错误 → `0` 是真实事实 | 错误事件集合 | `error_count == incorrect_count`，是同一事实的两种视图 |
| 错误归因分布（计数） | 每类错误原因的绝对数量 | `errors.error_count_by_cause` | `progress-state/v0.1` | `aggregate` | `Available` | 无分类错误 → 各值 `0` | 带 `error_cause` 的错误事件 | 枚举固定：`knowledge_gap` / `reading_error` / `calculation_error` / `scoring_point_expression` |
| 错误归因分布（占比） | 已分类错误中的原因占比 | `errors.error_cause_mix` | `progress-state/v0.1` | `aggregate` | `Available (null 可能)` | 无已分类错误（分母 0）→ `null` | `classified_error_count` + 各 cause 计数 | **分母只含已分类错误**，不含 `unclassified` |
| 未分类错误数 | 未给出归因的错误数 | `errors.unclassified_error_count` | `progress-state/v0.1` | `aggregate` | `Available` | 全部已分类 → `0` 是真实事实 | 无 `error_cause` 的错误事件 | 未分类不被强行归入某一类；UI 不得猜测原因 |
| 已分类错误数 | 有归因的错误数 | `errors.classified_error_count` | `progress-state/v0.1` | `aggregate` | `Available` | 无 → `0` | `error_cause` 存在性 | 与 `unclassified` 之和 = `error_count` |
| 知识覆盖 L1 | 已触达的 L1 域比例 | `coverage.l1.ratio` | `progress-state/v0.1` | `aggregate` | `Available (null 可能)` | `total = 0` → `null`（taxonomy 非空时不会发生） | `coverage.l1.covered` / `coverage.l1.total` | **分母 = taxonomy 全量 L1 节点数，不是考试权重**；文案禁止写成「考纲覆盖率」 |
| 知识覆盖 L2 | 已触达的 L2 topic 比例 | `coverage.l2.ratio` | `progress-state/v0.1` | `aggregate` | `Available (null 可能)` | 同上 | `coverage.l2.covered` / `total` | L3 引用经 parent closure 覆盖 L2 |
| 知识覆盖 L3 | 已触达的 L3 subtopic 比例 | `coverage.l3.ratio` | `progress-state/v0.1` | `aggregate` | `Available (null 可能)` | 同上 | `coverage.l3.covered` / `total` | 综合题与案例题的 topic 引用都计入 coverage |
| Topic 正确率 | 某 Knowledge Topic 的事实正确率 | `topics[*].accuracy` | `progress-state/v0.1` | `aggregate` | `Available (null 可能)` | 该 topic `attempt_count = 0` → `null` →「未评估」 | `topics[id].correct_count` / `attempt_count` | **不是 mastery**；父节点不复制子节点计数 |
| Topic 作答数 | 某 topic 的证据条数 | `topics[*].attempt_count` | 同上 | `aggregate` | `Available` | `0` 是真实事实 | 直接引用该 topic 的事件 | multi-topic 时每个直接 topic 各 +1 |
| 案例总作答数 | 案例子问题提交次数 | `case.attempt_count` | `progress-state/v0.1` | `aggregate` | `Available` | `0` 是真实事实 | `case_attempt` 事件计数 | 每条 case 事件只 +1 |
| 案例带分作答数 | 含总分证据的案例数 | `case.scored_attempt_count` | `progress-state/v0.1` | `aggregate` | `Available` | `0` 是真实事实 | 含 `score_earned` / `score_possible` 的事件 | 与 `attempt_count` 的差额 = 无总分证据的案例 |
| 案例加权得分率 | 案例按采分点的事实得分率 | `case.score_ratio` | `progress-state/v0.1`（`sum(earned) / sum(possible)`） | `aggregate` | `Available (null 可能)` | 无总分证据（分母 0）→ `null` →「证据不足」，**不显示 0** | `case.score_earned` / `case.score_possible` | **加权聚合，不是平均每题比例**；**不是 75 分制考试成绩** |
| 案例得分分子 / 分母 | 原始采分点证据 | `case.score_earned` / `case.score_possible` | 同上 | `aggregate` | `Available` | 无证据 → `0` / `0`（此时 ratio 为 `null`） | 逐事件 score 证据 | 必须与 ratio 一起解释，避免 ratio 脱离分母 |
| Capability 得分率 | 某 Case Capability 的事实得分率 | `capabilities[*].score_ratio` | `progress-state/v0.1` | `aggregate` | `Available (null 可能)` | 无 capability-level 证据 → `null` | `capabilities[id].score_earned` / `score_possible` | **只有 `capability_scores` 中带实际证据的 capability 才有值**；总分不复制给 capability |
| Capability 证据状态 | 该 capability 是否有足够证据 | `capabilities[*].evidence_status` | `progress-state/v0.1` | `aggregate` | `Available` | 枚举：`sufficient` / `insufficient_evidence` | `capabilities[id].attempt_count` | `insufficient_evidence` 显示为**中性灰**「证据不足」，**不是红，也不是 0** |
| Capability 证据条数 | 该 capability 的评分证据条数 | `capabilities[*].attempt_count` | `progress-state/v0.1` | `aggregate` | `Available` | `0` 是真实事实 | `capability_scores` 条目 | 仅有 `capabilities` 引用而无 evidence 时为 0 |
| 累计学习时长 | 测量到的学习分钟总数 | `study.study_minutes` | `progress-state/v0.1`（`duration_minutes` 求和） | `aggregate` | `Available` | 无会话 → `0` 是真实事实 | `study_session` 事件 | **只表示测量时长，不表示学习质量 / 专注度 / 效率 / 完成度** |
| 学习会话数 | 测量到时长的会话数 | `study.session_count` | `progress-state/v0.1` | `aggregate` | `Available` | `0` 是真实事实 | `study_session` 事件计数 | 会话的 `topics` 只是上下文，不产生 attempt / coverage 证据 |
| 状态 schema 版本 | 派生状态契约版本 | `schema_version` | `progress-state/v0.1` | `aggregate` | `Available` | 恒有值 | 契约文件 | 展示于 `PolicyVersionFooter`（Explain 层） |
| 重放规则版本 | 生成该状态的规则版本 | `replay_rule_version` | `progress-state/v0.1` | `aggregate` | `Available` | 恒有值 | 契约文件 | 与 `as_of` 一起构成可复现前提 |
| 事件 schema 版本 | 事实事件契约版本 | `event_schema_version` | `progress-state/v0.1` | `aggregate` | `Available` | 恒有值 | 契约文件 | `progress-event/v0.1` |
| Taxonomy 版本 | Knowledge Topic 契约版本 | `taxonomy_version` | `progress-state/v0.1` | `aggregate` | `Available` | 恒有值 | `taxonomy/taxonomy.json` | 影响 coverage 分母与 topic id 稳定性 |
| Capability 版本 | Case Capability 契约版本 | `capability_version` | `progress-state/v0.1` | `aggregate` | `Available` | 恒有值 | `taxonomy/capabilities.json` | 与 `taxonomy_version` 同源但语义独立 |
| 已重放事件数 | 参与本次重放的事件总数 | `replayed_event_count` | `progress-state/v0.1` | `aggregate` | `Available` | 无事件 → `0` | 事件集合 | 用于 Explain 层证明「状态由多少事实重建」 |

---

## 4. 主映射表 · `user_config` 与 `projection`

| UI Metric | UI Meaning | Domain Field | Domain Source | Source Category | Current Availability | Null Semantics | Explain Source | Notes / Constraints |
|---|---|---|---|---|---|---|---|---|
| 考试日期 | 用户设定的目标考试日 | —（`exam_date` 不在 User Configuration v0.1） | Future config contract | `future` | `Future` | 不适用 | 尚无正式输入 source | P5.2 明确 OUT / FUTURE；不得假称当前可配置 |
| 距考试剩余天数 | 距目标考试的天数 | —（未来由 exam-date contract + `as_of` + `timezone` 派生） | future projection | `future` | `Future` | 不适用 | 未来配置 + `timezone` + `as_of` | 必须使用显式 as_of 与 timezone；不得使用浏览器本地时间 |
| 时区 | 日历日边界依据 | `timezone` | User Configuration | `user_config` | `User Config` | 未配置 → 必须显式要求配置，不得默认 | 用户输入 | due / calendar 的日期归属依赖它 |
| 每日可用时间 | 用户声明的输入分钟容量 | `daily_available_minutes` | User Configuration v0.1 | `user_config` | `User Config` | 未配置 → contract validation reject | 用户输入 | P5.2 不含 `tier`；与 PlannerOutput `capacity_minutes` 是不同语义 |
| 目标 / 及格线 | 用户设定的目标线 | —（不在 User Configuration v0.1） | Future config contract | `future` | `Future` | 不适用 | 尚无正式输入 source | 需独立配置与 assessment contract；不得假称当前可配置或 domain 事实 |

---

## 5. 主映射表 · `phase4`（Domain Available；UI / Read Model 尚未实现）

> **Phase 4 当前真实状态**：P4.1～P4.9 的契约、实现、fixture、测试、文档与正式 Gate 验证已完成；Gate B PASS。UI / Read Model 仍未实现，只能消费 replay 输出，不能直接调用 policy kernel。详见 [`docs/PHASE4_VALIDATION_REPORT.md`](../PHASE4_VALIDATION_REPORT.md)。
>
> ```text
> Available: review-model/v0.1 + review-event/v0.1 + review-evidence/v0.1
> Available: mastery-policy/spaced-consecutive/v0.1 + review-policy/simple-ladder/v0.1
> Available: mastery-review-state/v0.1（item_order、evidence trace、as_of、timezone）
> Available: mastery_state / review_status / due counts / interval / due dates / reasons / policy metadata
> UI / Read Model code: 未实现
> ```
>
> 因此下表的 `Current Availability` 表示 **domain replay 已可用**；正式 UI read model / 前端仍不在本轮范围。

| UI Metric | UI Meaning | Domain Field | Domain Source | Source Category | Current Availability | Null Semantics | Explain Source | Notes / Constraints |
|---|---|---|---|---|---|---|---|---|
| mastery | 某 review item 的掌握状态 | `mastery_state`（枚举已冻结） | MasteryReviewState v0.1（P4.5 replay） | `phase4` | `Available`（由 replay 提供） | 无 evidence → `new`（不是 `insufficient_evidence`） | `mastery_reason` + `consecutive_success_day_count` + `policy` + `as_of` | 枚举：`new` / `learning` / `mastered`；**accuracy ≠ mastery**；mastery 由 item 自身跨天连续成功数（阈值 3）决定，不读 `topic_accuracy`；UI 不得推断 |
| mastery 分布 | 各状态的 item 数量 | `new_count` / `learning_count` / `mastered_count` | MasteryReviewState（P4.5 replay） | `phase4` | `Available`（由 replay 提供） | 无 item → `0`（真实事实） | 状态计数 | 用于 `OperationalStatsGrid` T8 |
| 到期复习数 `due_count` | 截至 `as_of` 到期的 item 数量 | `due_count` | MasteryReviewState（P4.5 replay） | `phase4` | `Available`（由 replay 提供） | 无 item → `0`；无 policy → 不可用 | `policy` + `as_of` + `schedule_timezone` | **unit = review_item（不是事件数）**；已冻结不变量 `due_count == due_today_count + overdue_count`；UI 不得自行重算 |
| 下次到期时间 | 该 item 下次到期时刻 / 本地日 | `next_due_at`（UTC instant）+ `next_due_local_date`（YYYY-MM-DD） | MasteryReviewState（P4.5 replay） | `phase4` | `Available`（由 replay 提供） | 未进入调度 → `null` | `scheduling_reason` + `review_status_reason` | 二者同时保存；canonical = instant；due 边界含，overdue 边界不含 |
| 复习间隔 `review_interval_days` | 当前 policy 下的间隔天数 | `review_interval_days`（整数或 `null`） | Review policy v0.1（P4.5 replay） | `phase4` | `Available`（由 replay 提供） | 未进入调度 → `null` | `policy` + `review_status_reason` | ladder 已冻结为 `1 / 3 / 7 / 15`，failure 重置为 `1`，mastered 保留 `15` maintenance |
| 上次复习时间 `last_review_at` | 最近一次 review evidence 的时刻 | `last_review_at`（UTC instant） | MasteryReviewState（P4.5 replay） | `phase4` | `Available`（由 replay 提供） | 无 review → `null` | `last_evidence_id` + `items[].evidence[]` | 逐条 evidence trace 已由 P4.2/P4.5 输出 |
| 到期状态 `review_status` | `due` / `overdue` 时间投影 | `review_status` | Review policy v0.1（P4.5 replay） | `phase4` | `Available`（由 replay 提供） | 无 evidence → `not_scheduled` | `review_status_reason` + `as_of` + `schedule_timezone` | 枚举：`not_scheduled` / `scheduled` / `due` / `overdue`；**与 mastery 是两个独立维度**；`mastered + due` 合法 |
| transition reason | 为什么状态 / 到期时间变成现在这样 | `mastery_reason` + `review_status_reason` + `scheduling_reason` | MasteryReviewState（P4.5 replay） | `phase4` | `Available`（engine replay 输出） | engine 未输出 → UI 显示「原因不可用」 | policy 输出 | **UI 不得生成推测性解释**；不得用 accuracy 补充解释 mastery |
| review item 身份 | 复习对象的稳定 id | `review_item_id` | Review Model（P4.1） | `phase4` | `Available`（catalog 已校验） | 不适用 | P4.1 身份构成规则 | `review/<item_kind>/<stable canonical reference>`；UI 不得自行拼 `review_item_id` |
| review item 粒度 | item kind | `item_kind` | Review Model（P4.1） | `phase4` | `Available` | 不适用 | P4.1 契约 | UI 必须显示 `item_kind`；不同粒度不得混用同一进度条；v0.1 对三种 kind 使用同一套 policy 数学 |
| 证据详情 | 逐条 review evidence | `items[].evidence[]` | Review Evidence + outcome adapter（P4.2 / P4.5） | `phase4` | `Available` | 不适用 | `evidence_id` / source reference / policy outcome reason | raw score 保留；未冻结 rubric 时不映射为 success/failure |
| policy 标识 / 版本 | 解释可复现所需的 policy 标识 | `policy`（policy_identity）+ `schema_version` | MasteryReviewState（P4.5） | `phase4` | `Available` | 不适用 | policy 元数据 | 顶层 schema：`mastery-review-state/v0.1`；另记录 outcome adapter `review-outcome/raw-facts/v0.1` |
| 调度时区 | 日历日边界依据 | `schedule_timezone`（显式 IANA，必填） | MasteryReviewState（P4.5） | `phase4` | `Available` | 无隐式默认；不得回退到机器时区 | `tzdata_version` | replay 同时回显 common envelope 的 `timezone`；UI 不得混用用户本地隐式时区 |
| 时区数据库版本 | 解释可复现所需 | `tzdata_version` | policy 层已冻结 | `phase4` | `Available` | replay 输出并记录运行环境 tzdata version | policy 元数据 | 进入 `PolicyVersionFooter` |

---

## 6. 主映射表 · `planner`（P5.3 output contract 已冻结；Planner generation 未实现）

| UI Metric | UI Meaning | Domain Field | Domain Source | Source Category | Current Availability | Null Semantics | Explain Source | Notes / Constraints |
|---|---|---|---|---|---|---|---|---|
| Today Plan | 今天应该做什么 | `PlannerOutput.days[0]` | `planner-output/v0.1` | `planner` | Contract frozen；尚无生成器 / consumer | 无 PlannerOutput = unavailable；有效空日为 `tasks=[]` | `explain_traces[]` | Today 是 `days[0]` alias，不双写；UI 不生成 / 拆分 / 补全 / 重排任务 |
| Rolling horizon | 未来短周期容器 | `horizon` + `days[0..6]` | `planner-output/v0.1` | `planner` | Contract frozen；尚未生成 | 无 PlannerOutput = unavailable | output metadata | 7 个连续 local calendar days；不是 30-day curriculum |
| 日期 / 学习日 | 本地日期与配置学习日投影 | `generated_for_local_date` / `days[].day_offset` / `local_date` / `study_day` | `planner-output/v0.1` + P5.2 config | `planner` / `user_config` | Contract frozen | 不适用 | `as_of` + `timezone` + `study_days` | 禁止用机器时区；P5.3 不规定非学习日 capacity |
| 计划容量 | 单日计划容量、已分配与剩余分钟 | `days[].capacity_minutes` / `planned_minutes` / `remaining_minutes` | `planner-output/v0.1` | `planner` | Contract frozen；P5.4 allocation 未实现 | 无 output = unavailable | policy-specific structured trace | 与 `daily_available_minutes` 语义不同；不显示为实际耗时 |
| 任务列表 | v0.1 复习任务 | `tasks[].task_id / task_type / target_kind / target_ref / planned_minutes / explain_trace_id` | `PlannerOutput.days[]` | `planner` | Contract frozen；尚无生成器 | 有效无任务日 = 空数组 | `explain_traces[]` | v0.1 仅 `review`；UI 保留 output 顺序，不内联第三方正文 |
| 任务 target | 正式 Review Item identity | `target_kind = review_item` / `target_ref = review_item_id` | Review Item / MasteryReviewState input | `planner` / `phase4` | 已有稳定 Review identity | 未知 / 不支持引用应拒绝 | trace `target_ref` + input references | label != identity；展示名不得作为引用 |
| Unmet Demand | 合法需求未进入计划 | `unmet_demand[].demand_id / demand_type / target_kind / target_ref / requested_minutes / explain_trace_id` | `PlannerOutput.days[]` | `planner` | Contract frozen；selection policy 未实现 | 空数组表示无未满足 demand | `explain_traces[]` | 与 invalid / unsupported input 拒绝语义不同；不是 overflow task |
| Explain | 任务 / unmet demand 的结构化说明 | `explain_traces[].reason_code / planner_policy / input_references / target / decision_category / structured_inputs` | `planner-output/v0.1` | `planner` | 容器 frozen；业务 reason 留给 P5.4 | 无 output = unavailable | 同一结构化 trace；`display_message` 可选 | 自然语言不能成为唯一机器依据 |
| 计划视图切换（14 / 30 天） | 切换其它窗口 | —（P5.3 v0.1 不支持） | — | `future` | 未定义 | 不渲染控件 | — | v0.1 horizon 固定 7 天 |
| 冲刺阶段 / 主题 / milestone | 课程阶段 / Backbone 内容 | —（P5.3 v0.1 不输出） | — | `future` | P5.5 未冻结 | 不渲染 / 不推导 | — | 不得从 `docs/30_DAY_CURRICULUM_DRAFT.md` 推断 |

---

## 7. 主映射表 · `future`（无任何 contract）

| UI Metric | UI Meaning | Domain Field | Domain Source | Source Category | Current Availability | Null Semantics | Explain Source | Notes / Constraints |
|---|---|---|---|---|---|---|---|---|
| 论文状态 | 论文准备进度 | —（无 essay contract） | — | `future` | **`Future` / 不可用** | 不适用；UI 只显示「尚未建立契约」 | 不适用 | **禁止显示任何分数、篇数或进度条** |
| 模拟考试分数 / `recent_score` | 最近一次限时套卷成绩 | —（无 assessment contract） | — | `future` | `Future` | 不适用 | 不适用 | **禁止由 UI 换算 `case.score_ratio` 或 `global.accuracy` 得到分数** |
| assessment 记录 | 模拟考试完成事实 | —（无 assessment contract） | — | `future` | `Future` | 不适用 | 不适用 | 不建 `/assessment` 页面，不显示「完成 N 场模拟」 |
| 计划完成度 | 任务完成比例 | —（无 task execution contract） | — | `future` | `Future` | 不适用 | 不适用 | 不得由 UI 用「有事件」推断「已完成」 |
| task completion | 单个任务是否完成 | —（无 task execution contract） | — | `future` | `Future` | 不适用 | 不适用 | 未来必须来自显式 completion contract |
| 完成日（Calendar ●） | 某天是否达标完成 | —（无 task execution contract） | — | `future` | `Future` | 不适用 | 不适用 | Calendar 当前只能显示「有学习记录」 |
| 连续学习天数 `streak` | 连续达标天数 | —（无 contract） | — | `future` | `Future` | 不适用 | 不适用 | **禁止由 UI 用事件时间戳推断** |
| `capacity_actual` | 实际容量统计 | —（无 task execution contract） | — | `future` | `Future` | 不适用 | 不适用 | 未来由 Planner 消费，不由 UI 计算 |
| `completion_rate` | 近 N 日完成率 | —（无 task execution contract） | — | `future` | `Future` | 不适用 | 不适用 | 同上 |
| 笔记作为事实 | 笔记影响学习指标 | —（无 contract） | — | `future` | `Future` | 不适用 | 不适用 | `Note != Progress Fact != Review Evidence` |
| 考试分数换算（75 分制） | 把事实比例换算为卷面分 | —（无 normalization contract） | — | `future` | `Future` | 不适用 | 不适用 | **禁止任何形式的换算展示** |

---

## 8. 必须保持的语义不变量

以下五条是本映射表的核心不变量。任何 UI 实现违反其中一条即为契约违规。

### 8.1 `accuracy != mastery`

```text
accuracy       = 事实正确率（correct_count / attempt_count）
mastery        = 由 MasteryReviewState v0.1 replay 派生、绑定到 review item 的掌握状态
```

禁止：

```text
topic_accuracy >= 阈值 → 显示为「已掌握」
capability score_ratio 高  → 显示为「已掌握」
```

### 8.2 `case.score_ratio != 75 分制考试成绩`

```text
case.score_ratio = sum(score_earned) / sum(score_possible)   # 采分点事实比例
考试分数          = 需要 assessment + score normalization contract（不存在）
```

禁止把 `case.score_ratio` 乘以任何常数（例如换算成满分卷面分）后展示为分数。

### 8.3 `insufficient_evidence != 0`

```text
insufficient_evidence = 没有足够证据
0                     = 有证据，且结果为 0
```

在 UI 层：`insufficient_evidence` 使用**中性灰** + 文字「证据不足」，不得使用红色，不得显示为 `0%`。

### 8.4 `null != 0`

```text
accuracy = null       → 「未评估」
accuracy = 0.0        → 「全部答错」
case.score_ratio = null → 「证据不足」
case.score_ratio = 0.0  → 「有证据且得分为 0」
```

UI 必须能区分这两种状态。禁止用 `?? 0`、`|| 0`、`Number(x) || 0` 一类默认值抹平 `null`。

### 8.5 有学习事件 != 完成学习

```text
有 progress event   → 「有学习记录」
完成学习            → 需要 task execution / completion contract（不存在）
```

Calendar、streak、完成度、计划进度都受此约束。

---

## 9. 禁止由 UI 自行计算的字段

以下字段即使「看起来可以从现有数据推出来」，也**禁止**由 UI 计算：

| 禁止计算的字段 | 为什么禁止 |
|---|---|
| `mastery` / `mastered` | 影响学习计划的指标必须来自版本化 policy + immutable facts |
| `review_due` / `next_due_at` / `overdue` | policy 与显式 `as_of` 已冻结；UI 必须读取 replay 输出，不得自行计算 |
| `due_count` | 已有 replay 聚合；UI 必须读取输出并保持 aggregate/item projection 一致 |
| `review_interval_days` | policy 参数已冻结；UI 必须读取 replay 输出 |
| 今日任务 / 任务数量 / 任务顺序 | 只能读取 PlannerOutput（生成与业务排序仍未实现） |
| 计划完成度 / `completion_rate` | task execution contract 未冻结 |
| `streak` | 无 contract；易与「有事件」混淆 |
| `recent_score` / 考试分数 | assessment contract 未冻结 |
| 论文进度 / 论文分数 | essay contract 未冻结 |
| 目标达成度 / 距离及格线 | assessment + normalization contract 未冻结 |
| 「已完成 / 打卡」 | 无 completion contract |
| 覆盖率的考试权重含义 | taxonomy 分母 ≠ 考试权重；权重来源未冻结 |

---

## 10. 非契约参考值清单（`reference-only` / `synthetic` / `non-contract`）

以下数值来自 Issue #5 描述的**参考 UI 截图**。它们在本轮中：

```text
标记：reference-only · synthetic · non-contract
用途：仅用于说明「为什么必须拒绝此类数值」
状态：禁止进入 production contract、fixture、domain、engine 或任何 validator
```

| 参考元素（非契约） | 标记 | 拒绝理由 |
|---|---|---|
| 圆环百分比样式值 | `reference-only` / `non-contract` | 只能绑定真实 aggregate（如 `global.accuracy`），或显示「未评估」 |
| 论文分数形值（`x/75`） | `reference-only` / `non-contract` | 论文无任何 domain contract → 必须显示 Future / unavailable |
| 案例分数形值（`x/75`） | `reference-only` / `non-contract` | `case.score_ratio` 是加权 earned/possible，不是 75 分制 |
| 综合分数形值（`x/75`） | `reference-only` / `non-contract` | 无 assessment contract，不能生成 75 分制分数 |
| 计划天数（`14 天`、`Day 1..N`） | `reference-only` / `non-contract` | v0.1 仅冻结 7 日 Rolling projection；30 天仍是 Draft，不得硬编码 |
| 单日分钟数（`120 分钟`） | `reference-only` / `non-contract` | 未来来自 Planner capacity；当前只能是 user configuration 或 Future |
| 倒计时天数（`36 天`） | `reference-only` / `non-contract` | P5.2 User Configuration v0.1 不含 exam_date；需未来正式配置契约，不得硬编码 |
| 模拟场次形值（`x/y Mock`） | `reference-only` / `non-contract` | 需要 assessment contract |
| 个人激励文案（`买车奖励`） | `reference-only` / `non-contract` | 个人文案不进 contract；未来最多作为用户自定义字段 |

**隔离规则**：

```text
1. 参考截图值不得写入任何 fixture、schema、validator 或 domain 常量
2. 若未来需要 demo / prototype，只能使用明确命名的 synthetic fixture，并与真实数据目录隔离
3. 任何 PR 若在 docs/ui 之外引入上述数值，必须显式标注 synthetic 来源
```

---

## 11. 映射完整性规则

```text
R1  任何 UI 上出现的指标，必须在本文件中存在一条映射
R2  映射不存在时，该指标不得渲染
R3  `phase4` fields 从 replay 输出消费且 domain status 为 Available；`planner` / `future` 未冻结字段只能渲染空态 / 不可用态
R4  映射表不得包含「UI 计算出的中间值」作为新事实
R5  新增指标时必须同时声明：domain source、null semantics、explain source、constraints
R6  上游契约版本变化时，必须同步更新本表的 Domain Field 与 Current Availability
```
