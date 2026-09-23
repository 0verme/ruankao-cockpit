# Mastery State Machine v0.1（冻结）

```text
policy_id      mastery-policy/spaced-consecutive
policy_version v0.1
status         FROZEN（本窗口 P4.3）
```

机器可读常量：`engine/rules/review_policy_v01.py`
可执行转移测试：`tests/test_review_policy.py`

---

## 0. 范围与依赖

本文件只冻结 **mastery 语义**：状态集合、初始状态、升级条件、降级条件、阈值绑定、mastered 维护。

不做以下事情：

- 不定义 `review_item` 是什么、如何获得稳定身份（P4.1）；
- 不定义 Review Evidence schema、事件类型、success / failure 的事实来源（P4.2）；
- 不实现 `MasteryReviewState v0.1` replay（P4.5）；
- 不使用累计 `topic_accuracy` 阈值、SM-2、FSRS、forgetting curve 或 AI 判断。

以上是本 policy 文档自身的范围，不代表全仓库尚未实现 replay：P4.1/P4.2 contracts 已冻结，P4.5 replay 已实现在 `engine/review/replay.py`，P4.6～P4.9 已通过 Phase 4 Gate，见 [`../PHASE4_VALIDATION_REPORT.md`](../PHASE4_VALIDATION_REPORT.md)。

本文件在 P4.3 窗口曾将 P4.1/P4.2 依赖记录在
[`ASSUMPTIONS_PENDING_P4_1_P4_2.md`](ASSUMPTIONS_PENDING_P4_1_P4_2.md)；这些 assumptions 已 reconcile 并冻结在 Review Model / Evidence contracts。该文件名保留历史信息，不表示当前仍 pending。完整状态与 replay 证据见 [`../PHASE4_VALIDATION_REPORT.md`](../PHASE4_VALIDATION_REPORT.md)。

---

## 1. 第一原则：`due` 是时间投影，不是知识状态

旧草案使用的单枚举是：

```text
new / learning / due / mastered
```

本窗口先分析 `due` 的性质，再决定是否照搬。

### 1.1 分析

| 候选状态 | 由什么决定 | 是否需要时间输入 |
| --- | --- | --- |
| `new` | 是否有可评估 evidence | 否 |
| `learning` | evidence 序列的结论（有证据但未达掌握条件） | 否 |
| `mastered` | evidence 序列的结论（达到掌握条件） | 否 |
| `due` | `as_of` 是否到达 `next_due_at` | **是** |
| `overdue` | `as_of` 的本地日期是否晚于到期本地日期 | **是** |

结论：

```text
due / overdue 是 (evidence 序列, 调度策略, as_of) 的时间投影
not 知识状态
```

### 1.2 为什么不能用单枚举表达

1. **不互斥**：一个 item 可以同时是 `mastered` 且到期（已掌握但仍需维护复习）。
   单枚举必须回答“`mastered + due` 是什么状态”，而这只能靠额外规则掩盖。
2. **`overdue` 无法表达**：单枚举里没有 overdue 的位置；若把 due 拆成 due/overdue，则“到期 3 天”
   和“到期 30 天”都没有位置。
3. **`not_scheduled` 无法表达**：`new` 且从未有 evidence 的 item 根本没有到期时间，
   与“有 evidence 且已排期”的 item 完全不同。
4. **transition 不完备**：时间自己不产生证据，却会改变状态 —— 于是状态机里必须出现
   “无 evidence 的 transition”，破坏 “state 是 evidence 的纯函数”这一性质。

因此 v0.1 **拒绝单枚举**，改为两条正交轴。

### 1.3 冻结的分层

```text
Axis 1 — Mastery State（知识轴，由 evidence 决定）
    new | learning | mastered

Axis 2 — Review Scheduling Projection（时间轴，由 policy + as_of 决定）
    not_scheduled | scheduled | due | overdue
```

### 1.4 组合可达性

`mastery_state ⇥ review_status` 的合法组合（v0.1 稳态）：

| mastery \ review_status | not_scheduled | scheduled | due | overdue |
| --- | --- | --- | --- | --- |
| `new` | ✅ 唯一可达 | ❌ 不可达 | ❌ 不可达 | ❌ 不可达 |
| `learning` | ❌ 不可达 | ✅ | ✅ | ✅ |
| `mastered` | ❌ 不可达 | ✅ | ✅ | ✅ |

- `new` 只在“没有任何可评估 evidence”时出现，此时没有到期时间，因此只能是 `not_scheduled`。
- 任何一次可评估 evidence 都会写入 `next_due_at`，所以 `learning` / `mastered` 不可能 `not_scheduled`。
- `mastered × due` 是正常组合，不是一个冲突。

这四类“不可达组合”是 P4.5 / P4.6 可以直接断言的不变量。

---

## 2. 状态定义与互斥性

### 2.1 `mastery_state`

| 状态 | 定义 | 判定依据 |
| --- | --- | --- |
| `new` | 该 item 没有任何可评估 evidence | `evaluated_evidence_count == 0` |
| `learning` | 有可评估 evidence，但当前成功 run 未达到掌握条件 | `evaluated_evidence_count > 0` 且 `consecutive_success_day_count < 3` |
| `mastered` | 当前成功 run 达到掌握条件 | `consecutive_success_day_count >= 3` |

互斥性：三者由 `evaluated_evidence_count` 与 `consecutive_success_day_count` 两个派生量唯一决定，
且 `new`（count = 0）与 `learning` / `mastered`（count > 0）互斥，`learning` 与 `mastered`
由 `>= 3` 与否互斥。

状态不是一个可以自由修改的字段，而是 **evidence 序列的纯函数**。因此：

```text
same evidence stream
+ same as_of
+ same schedule_timezone
+ same policy version
= same mastery_state
```

### 2.2 为什么 mastery 不读 `topic_accuracy`

`topic` 级 accuracy 是**聚合事实**，不是 item 状态：

- 它混合了不同 item、不同时间、不同难度；
- 它无法表达“这个具体复习对象现在是否掌握”；
- 用 `topic_accuracy >= X → mastered` 会让相邻 item 互相污染，并让 mastery 不可解释。

v0.1 明确：`mastery` **只**绑定 `review_item` 与 `review_item` 自身的 evidence。

---

## 3. 派生 run 量

mastery 与 scheduling 都只读两个从 evidence 序列派生的量：

| 派生量 | 定义 |
| --- | --- |
| `consecutive_success_count`（`c`） | 自最近一次 failure 以来的 success 条数（无 failure 则从序列开头算起） |
| `consecutive_success_day_count`（`d`） | 上述 success 覆盖的**不同本地日期**数量 |

性质：

- `1 <= d <= c`；有 failure 后 `c = d = 0`；
- 由于时间单调，同一 run 内的本地日期非递减，`d` 等于“首次成功 + 每次比前一条成功更晚的本地日期的成功”数量；
- `c` 只用于解释与统计，**不参与** mastery 判定与 interval 判定；
- `d` 同时驱动 mastery（阈值 3）与 interval ladder（见 scheduling 文档）。

不使用“可变 ladder 指针”作为独立状态，是 v0.1 保持可 replay 的关键：状态越少，非法跃迁越少。

---

## 4. Mastery transition table

设 evidence 按 `(occurred_at UTC, evidence_id)` 升序逐条应用。下表覆盖全部
`(mastery_state, evidence)` 组合，因此 **transition 完整且 total**。

| # | Current | Evidence | Next | Reason code | 说明 |
| --- | --- | --- | --- | --- | --- |
| T1 | `new` | （无 evidence） | `new` | `no_evaluated_evidence` | 初始状态 |
| T2 | `new` | `failure` | `learning` | `failure_enters_learning` | 首次失败即进入 learning，不留在 new |
| T3 | `new` | `success` | `learning` | `success_enters_learning` | 单次成功不足以掌握 |
| T4 | `learning` | `success`，`d < 3` | `learning` | `learning_success_below_mastery` | 继续累积跨天成功 |
| T5 | `learning` | `success`，`d >= 3` | `mastered` | `learning_success_reaches_mastery` | 唯一升入 mastered 的路径 |
| T6 | `learning` | `failure` | `learning` | `learning_failure_keeps_learning` | 状态不变，run 清零 |
| T7 | `mastered` | `success` | `mastered` | `mastered_success_maintenance` | maintenance，不改变状态 |
| T8 | `mastered` | `failure` | `learning` | `mastered_failure_demotes_learning` | **mastered 可被撤销** |
| — | 任意 | `insufficient` | 不变 | （不产生 mastery transition） | 只增加 `insufficient_evidence_count` |

说明：

- 表中没有“非法跃迁”。transition function 对 `(state, evidence)` 全域有定义，
  “非法状态跃迁”在 v0.1 中**不可能发生**，因此不需要拒绝机制。
- 非法输入仍在输入层拒绝：naive timestamp、future evidence、重复 `evidence_id`、
  未知 outcome、未知 timezone。这些属于输入校验，不属于状态机。
- `mastered` 的降级只由 failure 触发；时间流逝（due / overdue）不会降级 mastery。

---

## 5. 阈值绑定

`mastered` 的条件是：

```text
    当前连续成功 run 中
AND 成功发生在 >= 3 个不同本地日期
AND evidence outcome 属于 policy primitive `success`
AND 该 item 自身（不是 topic 聚合）
AND 使用 review policy `v0.1` + mastery policy `v0.1` 的 transition 语义
```

即阈值被显式绑定到：

| 绑定项 | 取值 |
| --- | --- |
| specific review item | 是，`review_item_id` |
| minimum evidence | 3 条 `success`，且跨越 3 个不同本地日期 |
| evidence kind | policy primitive `success`（原始事实到 primitive 的映射属 P4.2） |
| policy version | `mastery-policy/spaced-consecutive/v0.1` |
| transition semantics | `T5`，唯一升入 mastered 的 transition |

明确禁止：

```text
topic_accuracy >= X  ->  mastered          # 禁止作为唯一规则
successful_review_count >= 3  ->  mastered # 禁止（累计计数）
```

---

## 6. 关键问题逐条回答

| 问题 | v0.1 结论 |
| --- | --- |
| 无 evidence 时的初始状态 | `new`，且 `review_status = not_scheduled` |
| 首次成功 | → `learning`，不是 `mastered` |
| 连续成功 | 只有跨天成功才推进；第三次跨天成功才 → `mastered` |
| 失败 | run 清零；`mastered` → `learning`，`learning` 保持 `learning` |
| `learning` 失败 | `learning`，reason `learning_failure_keeps_learning` |
| `mastered` 后成功 | 保持 `mastered`，reason `mastered_success_maintenance` |
| `mastered` 后失败 | **降级**为 `learning`，reason `mastered_failure_demotes_learning` |
| `mastered` 是否永久 | **否**。mastered 表达“当前已证明掌握”，不是终身徽章 |
| `successful_review_count` 是否决定 mastery | **否**。它只用于解释/统计 |
| 连续成功与累计成功是否不同 | **是**。只有连续 run（且跨天）决定 mastery |
| 失败是否清零连续成功 | **是**，`c = d = 0` |
| `insufficient` evidence 是否改变 mastery | **否**，完全 no-op（只计数） |
| 未作答是否等于 failure | **否**。未作答不产生 policy outcome；若被记录，则为 `insufficient` |
| 实际 0 分是否等于 failure | Mastery policy 本身不从 score 判定 failure；P4.5 `review-outcome/raw-facts/v0.1` 保留 case/capability raw score 并映射为 `insufficient`。新 score outcome 必须使用新 adapter version |
| 非法状态跃迁如何处理 | 不存在非法跃迁；输入层非法值被显式拒绝 |
| 不同 item kind 之间是否互升级/降级 | **不允许**；P4.1 冻结 item catalog，Topic / Question / Case Capability 各自拥有独立 evidence stream 与 state |

---

## 7. Examples

以下 trace 使用 `Asia/Shanghai`，`d` = 跨天成功数。

| 事件 | occurred_at（本地） | mastery | reason | `d` | applied interval | next due |
| --- | --- | --- | --- | --- | --- | --- |
| （无） | — | `new` | `no_evaluated_evidence` | 0 | — | 不排期 |
| success | 03-01 10:00 | `learning` | `success_enters_learning` | 1 | 1 天 | 03-02 |
| success | 03-01 21:00 | `learning` | `learning_success_below_mastery` | 1 | 1 天 | 03-02（不变） |
| success | 03-02 10:00 | `learning` | `learning_success_below_mastery` | 2 | 3 天 | 03-05 |
| success | 03-05 10:00 | `mastered` | `learning_success_reaches_mastery` | 3 | 7 天 | 03-12 |
| success | 03-12 09:00 | `mastered` | `mastered_success_maintenance` | 4 | 15 天 | 03-27 |
| failure | 03-27 20:00 | `learning` | `mastered_failure_demotes_learning` | 0 | 1 天 | 03-28 |
| success | 03-28 09:00 | `learning` | `learning_success_below_mastery` | 1 | 1 天 | 03-29 |

注意 03-01 的第二次成功：它增加 `c`，但 `d` 不变，因此 mastery 与 interval **都不推进**。

---

## 8. Rejected Alternatives

| 方案 | 拒绝理由 |
| --- | --- |
| 单枚举 `new / learning / due / mastered` | 不互斥（`mastered` 可以同时 due）；无法表达 `overdue` 与 `not_scheduled`；需要无 evidence 的状态跃迁 |
| `topic_accuracy >= X → mastered` | 聚合事实冒充 item 状态；不可解释；跨 item 污染 |
| `successful_review_count >= 3 → mastered` | 累计计数；允许同一天刷 3 次；旧成功可以为近期失败背书 |
| 同一本地日内重复成功也推进 mastery | 允许“同一天刷掌握”，与间隔复习的语义冲突 |
| mastered 永久（不可撤销） | mastered 会退化为终身标记，长期失败的 item 仍显示 mastered |
| mastered 后失败保留 mastered（只改排期） | 同上；且会让 Gate 的“当前状态”问题给出误导性答案 |
| `unknown` / `suspended` 等额外 mastery 状态 | v0.1 没有驱动它们的稳定事实来源 |
| 用 `last evidence` 的分数阈值决定 mastery | 需要 score → success 映射；该映射属于 P4.2，且会引入阈值参数 |
| 由 AI 或自由文本判定 mastery | 违反 `AGENTS.md`：AI 不得凭感觉制造事实型学习指标 |
| 跨粒度互相升级（题目成功 → topic mastered） | v0.1 无冻结的聚合升级契约；会重复计数并破坏可解释性 |

---

## 9. Future Extensions（不实现）

- `ever_mastered` 终身标记（独立增量字段，不改变 v0.1 语义）；
- 按 item kind 区分的 mastery 阈值（必须作为新 policy version）；
- `suspend` / `retire` item 生命周期；
- 由 P4.2 提供的 score → success 映射（例如案例 capability 的采分点命中率）；
- 降级后的“部分保留”策略（当前为完全清零）。

历史状态不需要隐藏状态：任意历史 mastery 都可以用 `as_of` 回到过去进行 replay 得到。
