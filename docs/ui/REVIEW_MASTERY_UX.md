# Review / Mastery UX Contract v0.1

> **状态**：PLANNING CONTRACT（Issue #5 · UI.5）
> **依赖**：Issue #4 · Mastery / Review Scheduling v0.1 —— **尚未实现**
> **重要声明**：本文件只冻结「UI 层如何呈现」的规划。**最终字段名与状态枚举由 Issue #4 Contract 决定。** 本文件中所有指代 Issue #4 的字段名均为规划占位，不得当作已冻结契约。

---

## 1. 当前实现状态

```text
mastery                       ❌ 不存在
mastered / learning / new     ❌ 不存在
review_due                    ❌ 不存在
review_due_at                 ❌ 不存在
review_interval               ❌ 不存在
due_count                     ❌ 不存在
overdue                       ❌ 不存在
review_item / review_item_id  ❌ 不存在
review evidence               ❌ 不存在
transition reason             ❌ 不存在
mastery / review policy 版本   ❌ 不存在
```

现状证据：

- `engine/progress/README.md` 的 **Boundary** 明确列出未实现项。
- `engine/rules/README.md` 把 `mastery`、`review_due`、`review_interval` 列为 **Future inputs**。
- `data/progress/schema.json` 的 `out_of_scope` 显式包含 `mastery`、`mastered`、`review_due`、`review_interval`、`SM-2`、`FSRS`、`forgetting_curve`。

### 1.1 「测试骨架已存在」不等于「契约已冻结」

仓库目前**已经存在** Phase 4 的**测试设计资产**：

```text
docs/PHASE4_TEST_MATRIX.md              P4.6 / P4.7 测试矩阵设计稿，状态 TEST_DESIGN_READY / WAITING_FOR_CONTRACT_FREEZE
data/review/fixture-plan.json           78 条 fixture / harness / regression / static 计划项
data/review/fixture-schema.draft.json   review-fixture/v0.1-draft（status: draft, frozen: false）
tests/reviewkit.py + test_review_*.py   确定性 harness 骨架
scripts/validate_review.py              输出 PENDING_CONTRACT_FREEZE
```

但它们**都不提供 UI 可消费的字段**：

```text
不存在：Review Model 正式契约
不存在：Mastery State Machine
不存在：Review Scheduling Policy
不存在：engine.review replay
不存在：任何 mastery / due / interval 字段
```

**关于并行工作**：仓库可能有未合并分支正在推进 P4.1～P4.5。这类分支上的 policy symbol 或 draft 字段**不构成 Gate B 的输入**；只有合并进 `main` 并附带 validation report 后，才能被视为已冻结契约。本文件始终以 `main` 为准。

所以：

```text
Review Queue / MasteryBadge / DueBadge 在 Issue #4 contract freeze 前
只允许渲染 UnavailableBadge，不得渲染任何推测状态。
```

---

## 2. 两个独立维度（核心冻结决策）

UI 必须把 **mastery status** 与 **scheduling status** 渲染为**两个独立维度**。

```text
维度 1 · mastery status       —— 「我掌握到什么程度」
维度 2 · scheduling status    —— 「我什么时候该复习」
```

**禁止**在 UI 层提前把它们强行合并成一个互斥枚举。

| 维度 | 语义 | 用户层候选标签（规划） |
|---|---|---|
| mastery status | 掌握程度 | `学习中` / `已掌握` / `证据不足` |
| scheduling status | 调度状态 | `今天复习` / `已逾期` |

**为什么必须分离**：`due` / `overdue` 更可能是 **scheduling projection**，而不是与 `new` / `learning` / `mastered` 并列的 mastery 语义。若合并成单一枚举，会破坏互斥性并产生无法解释的组合（例如「已掌握但今天到期」）。

> 若 Issue #4 最终契约明确证明「单枚举仍互斥且可解释」，UI 才可考虑合并；否则永久分离。

**渲染形态（规划）**：

```text
MasteryBadge  —— 只表达 mastery status
DueBadge      —— 只表达 scheduling status
两者可在同一行并列显示，但不得互相覆盖、不得互相推导
```

---

## 3. 用户层标签

用户层只显示友好标签（Progressive Disclosure）。工程字段进入 Explain 层。

| 用户可见标签 | 维度 | 对应状态（占位） | 颜色语义 |
|---|---|---|---|
| 学习中 | mastery | `TBD — dependent on Issue #4` | 中性 / 进行中 |
| 已掌握 | mastery | `TBD — dependent on Issue #4` | healthy / completed |
| 证据不足 | mastery | `TBD — dependent on Issue #4`（预计与 `insufficient_evidence` 对应） | **中性灰** |
| 今天复习 | scheduling | `TBD — dependent on Issue #4` | primary / attention |
| 已逾期 | scheduling | `TBD — dependent on Issue #4` | risk / overdue |

**注意**：

```text
1. 上表标签为 UI 规划文案，不是 Issue #4 的状态枚举
2. 最终枚举名、互斥规则、转移条件以 Issue #4 Contract 为准
3. 若 Issue #4 最终状态集与上表不一致，必须更新本文件而不是扭曲契约
```

---

## 4. Explain 层

Explain 层默认折叠，展开后展示可复现的原因链。

| Explain 字段 | 内容 | 依赖 | 当前状态 |
|---|---|---|---|
| `evidence` | 支撑该状态的原始事实（correct / score evidence） | Issue #4 | ❌ `TBD — dependent on Issue #4` |
| `last review` | 上次复习时间与结果 | Issue #4 | ❌ `TBD — dependent on Issue #4` |
| `interval` | 当前复习间隔 | Issue #4 | ❌ `TBD — dependent on Issue #4` |
| `policy version` | mastery / review policy 版本 | Issue #4 | ❌ `TBD — dependent on Issue #4` |
| `transition reason` | 为什么状态 / 到期时间变成现在这样 | Issue #4 | ❌ `TBD — dependent on Issue #4` |
| `as_of` | 该结论对应的时间点 | envelope | ✅ 可提供（一旦有 review 视图） |
| `timezone` | 日历日边界依据 | user_config | ✅ 可提供 |

**硬约束**：

```text
1. Explain 内容只能来自 engine 输出
2. engine 未输出原因 → 显示「原因不可用」，UI 不得生成推测性解释
3. Explain 必须显示版本信息（policy version + as_of），使历史结果可复现
4. AI 只可用于表达润色，不得生成事实型结论
```

---

## 5. Review Queue 呈现

| 项 | 规则 |
|---|---|
| 排序 | **100% 来自 engine**。UI 不得重新排序、不得自行计算优先级 |
| 分组 | 若 engine 提供分组，UI 按 engine 分组渲染；若 engine 未提供，UI 不得自行聚合 |
| 分页 / 截断 | 允许，但必须显示「已截断」并保留 engine 的总数与顺序语义 |
| 「今天到期」 | 由 engine 根据显式 `as_of` + `timezone` + `review_policy_version` 决定；UI 不得用本地时间判断 |
| 空态 | 无到期项 → 「今天没有到期的复习」；不得显示 0 个假 item |
| 不可用态 | Issue #4 未完成 → `UnavailableBadge`「依赖 Mastery / Review v0.1」 |

**Review item 粒度（规划）**：

review item 可能是 Topic / Question / Case Capability 三种粒度之一。UI 必须：

```text
1. 显示 item_kind
2. 不得混用同一进度条（例如用 topic 进度条渲染 question item）
3. 不同粒度的 evidence 不得互相升级 / 降级
```

`item_kind` 字段名与取值：`TBD — dependent on Issue #4`。

---

## 6. Badge 语义

### 6.1 MasteryBadge

| 项 | 约束 |
|---|---|
| 表达对象 | 仅 mastery status |
| 数据来源 | `TBD — dependent on Issue #4` |
| 证据不足态 | 图标 / 文字 + 中性灰；**不是红，也不是 0** |
| 无障碍 | 必须提供 screen-reader 文案（如「证据不足，尚无足够作答记录」）；不得只用颜色 |
| 禁止 | 不得由 `topic accuracy`、`capability score_ratio` 或任何 aggregate 自行推导 |

### 6.2 DueBadge

| 项 | 约束 |
|---|---|
| 表达对象 | 仅 scheduling status |
| 数据来源 | `TBD — dependent on Issue #4` |
| 逾期表达 | 必须显示具体信息（如「已逾期 N 天」），不得只用一个红点 |
| 无障碍 | screen-reader 文案必须包含天数与语义 |
| 禁止 | 不得由 UI 用 `last_event_at + 常量` 自行计算 |

### 6.3 组合渲染

```text
[MasteryBadge] [DueBadge]
```

两者独立，允许同时出现，例如「已掌握 · 今天复习」（maintenance review）—— 具体是否存在该组合取决于 Issue #4 契约。

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
UI → immutable review evidence（append-only，Issue #4 契约）
UI ✗→ 直接写 mastery / due / interval
```

| 允许 | 禁止 |
|---|---|
| 提交 review evidence 事件 | 直接改 mastery status |
| 请求 replay（显式 `as_of`） | 直接改 `review_due_at` |
| 读取 review queue view | 把 UI 缓存当作 state 事实源 |

---

## 10. 依赖状态汇总

| 依赖项 | 状态 |
|---|---|
| Issue #4 Review Model（P4.1） | ❌ 未冻结 |
| Issue #4 Review Evidence contract（P4.2） | ❌ 未冻结 |
| Issue #4 Mastery State Machine（P4.3） | ❌ 未冻结 |
| Issue #4 Review Scheduling Policy（P4.4） | ❌ 未冻结 |
| Issue #4 Mastery / Review replay（P4.5） | ❌ 未冻结（`engine.review` 不可用） |
| Issue #4 测试骨架（P4.6 / P4.7） | 🟡 **已进入 main**，但输出 `PENDING_CONTRACT_FREEZE` |
| Progress replay（`as_of` 语义先例） | ✅ 语义已由 `tests/baselines/progress_v01_semantics.json` 冻结；但**不提供** `as_of` 参数，Phase 4 需自行定义 |
| UI 实现 | ⛔ 被 Gate B 阻塞 |

**本 PR 的诚实声明**：

```text
Review / Mastery implementation dependency = unresolved
本文件只完成 consumer contract 侧规划
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
