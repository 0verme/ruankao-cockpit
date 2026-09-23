# Review / Mastery UX Contract v0.1

> **状态**：PLANNING CONTRACT（Issue #5 · UI.5）
> **依赖**：Issue #4 · Mastery / Review Scheduling v0.1 —— P4.1～P4.5 domain contract / replay 已完成
> **重要声明**：本文件只冻结「UI 层如何呈现」的规划。政策层状态枚举、字段名与 policy 标识以 `docs/review/` 为准；UI 只能消费 `MasteryReviewState v0.1`，不能绕过 replay 自行计算。
> **可消费性声明**：P4.5 replay 已提供 domain output；本文件不实现 UI、API 或 read model。

---

## 1. 当前实现状态

Phase 4 已完成 P4.1～P4.9，最终 Gate 为 PASS：

```text
✅ P4.1～P4.2 Review Model / Event / Evidence v0.1
✅ P4.3～P4.4 Mastery / Review Scheduling Policy v0.1
✅ P4.5 deterministic MasteryReviewState v0.1 replay
✅ P4.6～P4.7 36 个 synthetic fixtures、validator 与 edge-case tests
✅ P4.8 documentation / architecture sync
✅ P4.9 validation report（四项 Gate 均有证据）
```

因此：

```text
规则与 domain consumer：Gate B PASS；MasteryReviewState 字段 Available
UI / Read Model / frontend：未实现，不代表整个 Cockpit 已可开发
```

### 1.1 证据来源

| 事实 | 证据 |
|---|---|
| P4.3 / P4.4 已冻结 | `docs/review/README.md`（FROZEN v0.1）、`docs/review/MASTERY_POLICY_V01.md`、`docs/review/REVIEW_SCHEDULING_POLICY_V01.md`、`docs/review/POLICY_SYMBOL_FREEZE_V01.md` |
| 可执行 policy kernel | `engine/rules/review_policy_v01.py` + `tests/test_review_policy.py` |
| P4.1 / P4.2 contract | `docs/review/REVIEW_MODEL_V01.md`、`REVIEW_EVIDENCE_V01.md`（FROZEN） |
| P4.5 replay + P4.6/P4.7 validator | `engine/review/replay.py` 输出 `mastery-review-state/v0.1`；`scripts/validate_review.py` 输出 `REVIEW_FIXTURE_MATRIX_PASS`（仅 matrix）；P4.9 报告判定整个 Gate |
| Phase 4 不改变 ProgressState | `engine/rules/README.md`：mastery / review 是独立派生层 |
| `progress-state/v0.1` 边界 | `data/progress/schema.json` 的 `out_of_scope` 仍包含 `mastery` / `review_due` / `review_interval` |

### 1.2 已冻结的 policy 层字段名

以下字段名由 P4.3 / P4.4 冻结（来源 `docs/review/POLICY_SYMBOL_FREEZE_V01.md` § 3），**重命名需要新 policy version**：

```text
review_item_id
mastery_state              mastery_reason
review_status              review_status_reason      scheduling_reason
last_review_at             last_evidence_id
review_interval_days       next_due_at               next_due_local_date
evaluated_evidence_count   successful_review_count   failure_count
insufficient_evidence_count
consecutive_success_count  consecutive_success_day_count
```

聚合层（policy 层）：

```text
review：  total_items / not_scheduled_count / scheduled_count /
         due_today_count / overdue_count / due_count
mastery： new_count / learning_count / mastered_count
```

元数据（policy 层）：`schema_version` / `policy` / `as_of` / `schedule_timezone` / `tzdata_version`

P4.1 已冻结 `review_item_id` 的稳定 identity：`review/<item_kind>/<stable canonical reference>`。UI 深链仍必须使用 engine 输出的 ID，不得自行拼接。

另外：`MasteryReviewState v0.1` 的顶层 `schema_version`、对象结构与 replay metadata 已由 **P4.5** 命名；本文件不得自行扩展或改写 schema。

---

## 2. 两个独立维度（已由 P4.3 / P4.4 确认为正式契约）

UI 必须把 **mastery status** 与 **scheduling status** 渲染为**两个独立维度**。

```text
维度 1 · mastery status       —— 「我掌握到什么程度」
维度 2 · scheduling status    —— 「我什么时候该复习」
```

**禁止**在 UI 层把它们合并成一个互斥枚举。

这不是 UI 的自行主张：P4.3 / P4.4 已经把两个轴冻结为正交的 policy 输出（`docs/review/README.md`）：

| 维度 | Policy 字段（已冻结） | 冻结枚举（已冻结） | 权威文档 |
|---|---|---|---|
| mastery status | `mastery_state` | `new` / `learning` / `mastered` | `docs/review/MASTERY_POLICY_V01.md` |
| scheduling status | `review_status` | `not_scheduled` / `scheduled` / `due` / `overdue` | `docs/review/REVIEW_SCHEDULING_POLICY_V01.md` |

**关键语义（已冻结）**：

```text
due / overdue 是时间投影，不是 mastery 状态
mastered 与 due 可以同时成立（maintenance review）
```

因此单一枚举会直接丢失信息，并产生无法解释的组合。UI **永久分离两个维度**。

**渲染形态（冻结）**：

```text
MasteryBadge  —— 只表达 mastery_state
DueBadge      —— 只表达 review_status
两者可在同一行并列显示（如「已掌握 · 今天复习」），但不得互相覆盖、不得互相推导
```

---

## 3. 用户层标签

用户层只显示友好标签（Progressive Disclosure）。工程字段进入 Explain 层。

| 用户可见标签 | 维度 | 对应已冻结枚举值 | 颜色语义 |
|---|---|---|---|
| 未开始 | mastery | `new` | 中性灰 |
| 学习中 | mastery | `learning` | 中性 / 进行中 |
| 已掌握 | mastery | `mastered` | healthy / completed |
| 证据不足 | mastery（解释态） | `insufficient_evidence_count > 0` 且 `mastery_state = new` 时的 UI 解释 | **中性灰** |
| 未安排 | scheduling | `not_scheduled` | 中性灰 |
| 已安排 | scheduling | `scheduled` | 中性 / primary 低强度 |
| 今天复习 | scheduling | `due` | primary / attention |
| 已逾期 | scheduling | `overdue` | risk / overdue |

**约束**：

```text
1. 用户层标签是显示映射，不是新的 domain 枚举
2. 不得为了 UI 对称而新增、拆分或重命名 mastery_state / review_status 取值
3. `insufficient_evidence` 不是一个 mastery_state 取值；P4.3 冻结的语义是
   「effect = no_change，且不是 failure」（计数在 `insufficient_evidence_count`）
   → UI 必须以「证据不足」解释态呈现，不得显示为失败、0 分或红色
4. 状态枚举变更必须走新 policy version，不得原地改 v0.1
```

---

## 4. Explain 层

Explain 层默认折叠，展开后展示可复现的原因链。

| Explain 字段 | 内容 | 来源（policy 层已冻结字段） | 当前状态 |
|---|---|---|---|
| evidence | 支撑该状态的原始事实（correct / score evidence） | `items[].evidence[]` + counters + `last_evidence_id` | ✅ P4.5 replay 输出 |
| last review | 上次复习时间 | `last_review_at` | ✅ P4.5 replay 输出 |
| interval | 当前复习间隔（天） | `review_interval_days` | ✅ P4.5 replay 输出 |
| mastery 原因 | 为什么是这个 mastery 状态 | `mastery_reason` | ✅ P4.5 replay 输出 |
| scheduling 原因 | 为什么是这个调度状态 | `review_status_reason` / `scheduling_reason` | ✅ P4.5 replay 输出 |
| policy version | mastery / review policy 标识 | `policy` + top-level versions + `outcome_adapter` | ✅ P4.5 replay 输出 |
| `as_of` | 该结论对应的时间点 | replay metadata（P4.5） | ✅ 显式输入并回显 |
| schedule timezone | 日历日边界依据 | `schedule_timezone` | ✅ Available：显式 IANA timezone，必填、无隐式默认 |
| tzdata version | 时区数据库版本 | `tzdata_version` | ✅ Available：replay 输出并记录 |
| evidence 明细 | 逐条 evidence | `items[].evidence[]` + Review Evidence v0.1 | ✅ P4.2/P4.5 输出；score adapter reason 显式记录 |

**硬约束**：

```text
1. Explain 内容只能来自 engine 输出
2. engine 未输出原因 → 显示「原因不可用」，UI 不得生成推测性解释
3. Explain 必须显示版本信息（policy + as_of + schedule_timezone），使历史结果可复现
4. AI 只可用于表达润色，不得生成事实型结论
5. mastery 由 item 自身的「跳天连续成功数」（阈值 3）决定，不读 topic_accuracy
   → UI 不得用 accuracy 高低“补充解释” mastery_reason
```

---

## 5. Review Queue 呈现

| 项 | 规则 |
|---|---|
| 排序 | **100% 来自 engine**。UI 不得重新排序、不得自行计算优先级 |
| 分组 | 若 engine 提供分组，UI 按 engine 分组渲染；若 engine 未提供，UI 不得自行聚合 |
| 分页 / 截断 | 允许，但必须显示「已截断」并保留 engine 的总数与顺序语义 |
| 同 timestamp 事件 | policy 层顺序为 `(occurred_at_utc, evidence_id)` 升序；同日重复成功计入 evidence 但不推进间隔、不改变到期日 |
| 「今天到期」 | 由 engine 根据显式 `as_of` + `schedule_timezone` 决定；UI 不得用本地时间判断 |
| 到期边界 | 本地日历日 00:00 为锚点；`due` 含边界，`overdue` 从下一个本地 00:00 起 |
| 空态 | 无到期项 → 「今天没有到期的复习」；不得显示 0 个假 item |
| 不可用态 | domain replay 可用；若 UI read model 未接入则显示实现层 unavailable，不得自行计算 |

**`due_count` 不变量（已冻结）**：

```text
unit      = review_item（不是事件数）
statuses  = due + overdue
due_count == due_today_count + overdue_count
```

UI 不得自行重新统计 `due_count`；若展示子计数，必须与总量自洽。

**Review item 粒度**：

review item 可能是 Topic / Question / Case Capability 三种粒度之一。UI 必须：

```text
1. 显示 item_kind
2. 不得混用同一进度条（例如用 topic 进度条渲染 question item）
3. 不同粒度的 evidence 不得互相升级 / 降级
```

`item_kind` 字段名与取值已由 P4.1 冻结并由 replay 输出：`topic` / `question` / `case_capability`。三种 item kind 保持独立 identity / evidence，但 v0.1 使用同一套 frozen policy 数学；alias 输入不属于 replay API，详见 `fixture-plan.json` 的 `not_applicable` 决策。

---

## 6. Badge 语义

### 6.1 MasteryBadge

| 项 | 约束 |
|---|---|
| 表达对象 | 仅 `mastery_state` |
| 数据来源 | `mastery_state` + `mastery_reason`（P4.5 replay） |
| 取值 | `new` / `learning` / `mastered`（已冻结，不得新增） |
| 证据不足态 | 以 `insufficient_evidence_count` 作为解释依据；图标 / 文字 + 中性灰；**不是红，也不是 0** |
| 无障碍 | 必须提供 screen-reader 文案（如「证据不足，尚无足够作答记录」）；不得只用颜色 |
| 禁止 | 不得由 `topic accuracy`、`capability score_ratio` 或任何 aggregate 自行推导 |

### 6.2 DueBadge

| 项 | 约束 |
|---|---|
| 表达对象 | 仅 `review_status` |
| 数据来源 | `review_status` + `review_status_reason` + `next_due_at` / `next_due_local_date`（P4.5 replay） |
| 取值 | `not_scheduled` / `scheduled` / `due` / `overdue`（已冻结，不得新增） |
| 逾期表达 | 必须显示具体信息（如「已逾期 N 天」），不得只用一个红点 |
| 无障碍 | screen-reader 文案必须包含天数与语义 |
| 禁止 | 不得由 UI 用 `last_review_at + 常量` 自行计算；不得自行决定 `due` / `overdue` 边界 |

### 6.2.1 两个字段共存是合法状态（已冻结）

```text
mastered + due   是合法组合（maintenance review），不是矛盾
```

UI 不得把该组合视为错误、不得隐去其中一个 badge、不得用一个 badge 覆盖另一个。

### 6.3 组合渲染

```text
[MasteryBadge] [DueBadge]
```

两者独立，允许同时出现（如「已掌握 · 今天复习」）。该组合已由 P4.3 / P4.4 确认合法（mastered maintenance review），不再是待定项。

---

## 7. 颜色与对比度

| 语义 | 颜色 | 用途 |
|---|---|---|
| 证据不足 / 未评估 | 中性灰 | `insufficient_evidence`、`empty`、Future |
| 今天到期 | primary / attention（暖橙） | 需要今天行动 |
| 已逾期 | risk（红） | 已超过 due |
| 已掌握 / 状态良好 | healthy（绿） | 完成、健康 |

**冻结规则**：

```text
insufficient_evidence = neutral（灰），不是 red
```

原因：证据不足只是「尚未评估」，不是失败。用红色会制造虚假的负面判断，并违反 `Honest null` 原则。

---

## 8. 与 Progress 语义的隔离

必须同时成立：

```text
topic accuracy      != mastery
capability score_ratio != mastery
case.score_ratio    != mastery
mastery             != due status
```

禁止的 UI 行为：

```text
1. 用 accuracy 高低给 MasteryBadge 上色
2. 用 capability score_ratio 推断「已掌握」
3. 用「连续答对 N 题」在前端判定 mastered（该规则属于课程草案，不是契约）
4. 用「有 review 类 activity_type 的 study_session」推断完成了一次复习
```

第 4 点的原因：`progress-event/v0.1` 中 `study_session.activity_type` 含 `review` 取值，但它只产生分钟事实，**不产生 review evidence**。

---

## 9. 写路径

```text
UI → immutable Progress Attempt + explicit Review Context events（append-only，P4.1/P4.2 契约）
engine → deterministic Review Evidence projection → MasteryReviewState replay
UI ✗→ 直接写 Evidence projection / mastery_state / review_status / review_interval_days / next_due_at
```

| 允许 | 禁止 |
|---|---|
| 提交 review evidence 事件（P4.2 冻结后） | 直接改 `mastery_state` |
| 请求 replay（显式 `as_of` + `schedule_timezone`） | 直接改 `next_due_at` / `next_due_local_date` |
| 读取 review queue view | 直接改 `review_interval_days` |
| 读取 `mastery_reason` / `review_status_reason` | 把 UI 缓存当作 state 事实源 |
| — | 调用 `engine.rules.review_policy_v01` 自行计算 item 状态 |

最后一条很重要：policy kernel 虽然是纯函数且已冻结，但它是 **P4.5 replay 的内部实现**；UI 不得绕过 replay 直接调用它拼装视图，否则会出现“UI 自己算 mastery”的实质违规。

---

## 10. 依赖状态汇总

| 依赖项 | 状态 |
|---|---|
| Issue #4 Review Model（P4.1） | ✅ `review-model/v0.1`；stable identity / item kind / canonical reference 已冻结 |
| Issue #4 Review Evidence contract（P4.2） | ✅ `review-event/v0.1` + `review-evidence/v0.1`；score rubric 仍由独立 adapter 管理 |
| Issue #4 Mastery State Machine（P4.3） | ✅ **已冻结 v0.1**：`mastery-policy/spaced-consecutive/v0.1`；`new / learning / mastered` |
| Issue #4 Review Scheduling Policy（P4.4） | ✅ **已冻结 v0.1**：`review-policy/simple-ladder/v0.1`；`not_scheduled / scheduled / due / overdue` |
| Issue #4 policy 层字段名 | ✅ 已冻结（`POLICY_SYMBOL_FREEZE_V01.md` § 3） |
| Issue #4 Mastery / Review replay（P4.5） | ✅ `mastery-review-state/v0.1`；P4.6～P4.9 已完成，Phase 4 Gate PASS |
| Issue #4 fixture / tests（P4.6 / P4.7） | ✅ 36 个 policy symbols 全部 frozen；36 个 fixture、validator 和 edge-case tests 已通过 |
| Issue #4 P4.1 / P4.2 假设 | ✅ `ASSUMPTIONS_PENDING_P4_1_P4_2.md` 已 reconcile；case/capability score threshold/rubric 仍未冻结，v0.1 adapter 输出 `insufficient` |
| Progress replay（`as_of` 语义先例） | ✅ 语义已由 `tests/baselines/progress_v01_semantics.json` 冻结；但**不提供** `as_of` 参数，Phase 4 需自行定义 |
| UI 实现 | ⛔ 本轮不实现；domain Gate B 已由 P4.5 replay 解锁 |

**Gate B 判定：PASS**。Issue #4 的「当前状态 / 今日到期集合 / 到期原因 / 完全确定性」四问均由 P4.5 replay、P4.6/P4.7 fixtures 与 tests、P4.9 report 验证。该 PASS 解锁 Review / Mastery consumer；不表示 UI / Read Model 已实现，Planner-bound 功能仍受 Gate C 阻塞。

**本 PR 的诚实声明**：

```text
Review / Mastery domain replay dependency = available
本文件仍只完成 consumer contract 侧规划；不实现 UI / API / read model
```

---

## 11. 与其余 UI 文档的关系

| 关注点 | 文档 |
|---|---|
| Read model 字段与不可用语义 | [`READ_MODEL_CONTRACT.md`](READ_MODEL_CONTRACT.md) §5.4 / §5.7 |
| 指标 → domain 映射 | [`DOMAIN_TO_UI_MAPPING.md`](DOMAIN_TO_UI_MAPPING.md) §5 |
| 路由（`/review`）| [`PAGE_MAP.md`](PAGE_MAP.md) §2.3 |
| 语义色与 token 方向 | [`DESIGN_DIRECTION.md`](DESIGN_DIRECTION.md) |
| 组件边界 | [`COMPONENT_MAP.md`](COMPONENT_MAP.md) |
| 断点与无障碍 | [`RESPONSIVE_ACCESSIBILITY.md`](RESPONSIVE_ACCESSIBILITY.md) |
