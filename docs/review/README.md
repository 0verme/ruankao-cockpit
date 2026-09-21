# Phase 4 Review Policy 文档索引

> 本目录只承载 **Phase 4 规则设计窗口（P4.3 / P4.4）** 冻结的 policy contract。
> 它不实现 replay，不定义 Review Item 身份，也不定义 Review Evidence schema。

## 文档

| 文档 | 内容 | 状态 |
| --- | --- | --- |
| [`MASTERY_POLICY_V01.md`](MASTERY_POLICY_V01.md) | Mastery State Machine v0.1：状态分层、transition table、阈值绑定、mastered 维护 | FROZEN v0.1 |
| [`REVIEW_SCHEDULING_POLICY_V01.md`](REVIEW_SCHEDULING_POLICY_V01.md) | Review Scheduling Policy v0.1：interval ladder、时间语义、failure 语义、`due_count` | FROZEN v0.1 |
| [`POLICY_TEST_MATRIX_V01.md`](POLICY_TEST_MATRIX_V01.md) | 可转成测试的案例表（input → expected） | FROZEN v0.1 |
| [`POLICY_SYMBOL_FREEZE_V01.md`](POLICY_SYMBOL_FREEZE_V01.md) | 对并行测试设计窗口（`test/p4-review-matrix`）的 20 个 policy symbol 与 7 个 CONTRACT GAP 的冻结记录 | FROZEN v0.1 |
| [`ASSUMPTIONS_PENDING_P4_1_P4_2.md`](ASSUMPTIONS_PENDING_P4_1_P4_2.md) | 本窗口对 P4.1 / P4.2 的显式假设 | **UNRESOLVED** |

## 与其他 Phase 4 窗口的关系

| 窗口 | 关系 |
| --- | --- |
| P4.1 / P4.2（Review Model / Evidence） | 本窗口的输入假设记录在 [`ASSUMPTIONS_PENDING_P4_1_P4_2.md`](ASSUMPTIONS_PENDING_P4_1_P4_2.md)；本窗口不反向替其拍板 |
| `test/p4-review-matrix`（P4.6 / P4.7 测试设计，已由 PR #6 合并） | 本窗口提供 [`POLICY_SYMBOL_FREEZE_V01.md`](POLICY_SYMBOL_FREEZE_V01.md)，并按该 manifest 自身的 freeze 机制只填 owner 为 P4.3 / P4.4 的 20 个 symbol；其余 16 个保持 `unfrozen` |
| P4.5（Mastery / Review replay） | 消费本窗口的 policy kernel 与字段名；`as_of` / version metadata / error category 命名空间由 P4.5 收口 |

---

## 机器可读入口

```text
engine/rules/review_policy_v01.py     policy kernel + 冻结常量
tests/test_review_policy.py           policy-level 单元测试
data/review/fixture-plan.json         P4.3 / P4.4 的 20 个 policy symbol 已冻结（其余 16 个待 P4.1 / P4.2 / P4.5）
```

## 边界

```text
本目录 = Mastery / Review 的 policy 语义
!= Review Model / Review Evidence 契约（P4.1 / P4.2，另一窗口）
!= MasteryReviewState replay（P4.5）
!= synthetic fixtures / validator（P4.6）
!= Planner / 30-Day Plan / UI
```

本窗口没有引入 SM-2、FSRS、forgetting curve、adaptive planner 或 AI 判断。所有规则都是确定性函数，
输入为显式 evidence、显式 `as_of` 和显式 IANA timezone。

`progress-state/v0.1` 未被本窗口修改：Phase 4 的 mastery / review 结果是**独立派生层**，不是
ProgressState 的新字段。
