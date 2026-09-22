# Phase 4 Review 文档索引

> 本目录同时承载 Phase 4 的上游 Review Model / Evidence contract（P4.1 / P4.2）和下游 Mastery / Scheduling policy contract（P4.3 / P4.4）。各层独立版本化，不把 policy 结论写回 Progress Fact 或 Evidence Fact。

## 上游 Review Model / Evidence

| 文档 | 内容 | 状态 |
| --- | --- | --- |
| [`REVIEW_MODEL_V01.md`](REVIEW_MODEL_V01.md) | Review Item 身份、item kind、canonical/source reference、initial/review 边界、D1–D12 | FROZEN v0.1 |
| [`REVIEW_EVIDENCE_V01.md`](REVIEW_EVIDENCE_V01.md) | Review Context Event、Evidence 字段、事实语义、projection、insufficient/unsupported | FROZEN v0.1 |
| [`ASSUMPTIONS_PENDING_P4_1_P4_2.md`](ASSUMPTIONS_PENDING_P4_1_P4_2.md) | P4.3/P4.4 并行假设的 reconcile 结果与 score outcome adapter 阻塞项 | RECONCILED；含 BLOCKING_DECISION |

## 下游 Mastery / Scheduling policy

| 文档 | 内容 | 状态 |
| --- | --- | --- |
| [`MASTERY_POLICY_V01.md`](MASTERY_POLICY_V01.md) | Mastery State Machine v0.1：状态分层、transition table、阈值绑定、mastered 维护 | FROZEN v0.1 |
| [`REVIEW_SCHEDULING_POLICY_V01.md`](REVIEW_SCHEDULING_POLICY_V01.md) | Review Scheduling Policy v0.1：interval ladder、时间语义、failure 语义、`due_count` | FROZEN v0.1 |
| [`POLICY_TEST_MATRIX_V01.md`](POLICY_TEST_MATRIX_V01.md) | 可转成测试的案例表（input → expected） | FROZEN v0.1 |
| [`POLICY_SYMBOL_FREEZE_V01.md`](POLICY_SYMBOL_FREEZE_V01.md) | 对并行测试设计窗口（`test/p4-review-matrix`）的 policy symbol 与 contract gap 冻结记录 | FROZEN v0.1 |

## 与其他 Phase 4 窗口的关系

| 窗口 | 关系 |
| --- | --- |
| P4.1 / P4.2（Review Model / Evidence） | 已冻结本目录的上游 contract；policy kernel 只能通过显式 adapter 消费 Evidence，不能反向改变 Evidence 事实。 |
| `test/p4-review-matrix`（P4.6 / P4.7 测试设计，已由 PR #6 合并） | 提供 fixture plan、policy symbol 和 determinism harness；policy-dependent fixture expected 仍等待 P4.5 replay。 |
| P4.5（Mastery / Review replay） | 消费 Review Evidence、明确的 score outcome adapter、policy kernel 和 `as_of` / timezone；必须处理本目录 `BLOCKING_DECISION`。 |

## 机器可读入口

```text
data/review/schema.json                  Review Item / Event / Evidence contract
engine/review/model.py                   validator + deterministic evidence projection
scripts/validate_review_contract.py      P4.1/P4.2 contract fixture validator
engine/rules/review_policy_v01.py       policy kernel + 冻结常量
scripts/validate_review.py               P4.6/P4.7 fixture plan validator（P4.5 replay 前保持 PENDING）
data/review/fixture-plan.json            policy fixture plan；不与 contract-fixtures 混用
```

## 边界

```text
Review Model / Evidence contract
   != Mastery / Scheduling policy
   != MasteryReviewState replay（P4.5）
   != synthetic policy fixtures / validation report（P4.6 / P4.7 / P4.9）
   != Planner / 30-Day Plan / UI
```

本目录没有引入 SM-2、FSRS、forgetting curve、adaptive planner 或 AI 判断。Review Evidence 保存 policy-independent facts；所有 mastery/scheduling 规则都是另外版本化的确定性函数，输入必须经过明确的 evidence/outcome adapter，并接受显式 `as_of` 与 IANA timezone。

`progress-state/v0.1` 未被本窗口修改：Phase 4 的 mastery / review 结果是**独立派生层**，不是 ProgressState 的新字段。
