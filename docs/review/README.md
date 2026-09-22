# Phase 4 Review 文档索引

> 本目录同时承载 Phase 4 的上游 Review Model / Evidence contract（P4.1 / P4.2）和下游 Mastery / Scheduling policy contract（P4.3 / P4.4）。各层独立版本化，不把 policy 结论写回 Progress Fact 或 Evidence Fact。

## 上游 Review Model / Evidence

| 文档 | 内容 | 状态 |
| --- | --- | --- |
| [`REVIEW_MODEL_V01.md`](REVIEW_MODEL_V01.md) | Review Item 身份、item kind、canonical/source reference、initial/review 边界、D1–D12 | FROZEN v0.1 |
| [`REVIEW_EVIDENCE_V01.md`](REVIEW_EVIDENCE_V01.md) | Review Context Event、Evidence 字段、事实语义、projection、insufficient/unsupported | FROZEN v0.1 |
| [`ASSUMPTIONS_PENDING_P4_1_P4_2.md`](ASSUMPTIONS_PENDING_P4_1_P4_2.md) | P4.3/P4.4 并行假设的 reconcile 结果与 score outcome adapter 边界 | RECONCILED；含 BLOCKING_DECISION |
| [`REVIEW_OUTCOME_ADAPTER_V01.md`](REVIEW_OUTCOME_ADAPTER_V01.md) | P4.5 Evidence → policy primitive 的保守、版本化 adapter | FROZEN v0.1 |

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
| `test/p4-review-matrix`（P4.6 / P4.7 测试设计，已由 PR #6 合并） | 提供 fixture plan、policy symbol 和 determinism harness；P4.5 replay 已可用，policy-dependent fixture expected / edge-case matrix 仍待收口。 |
| P4.5（Mastery / Review replay） | `engine.review.replay.replay(...)` 消费 Review Evidence、显式 outcome adapter、policy kernel 和 `as_of` / timezone，输出 `MasteryReviewState v0.1`。 |

## 机器可读入口

```text
data/review/schema.json                  Review Item / Event / Evidence contract
engine/review/model.py                   validator + deterministic evidence projection
scripts/validate_review_contract.py      P4.1/P4.2 contract fixture validator
engine/rules/review_policy_v01.py       policy kernel + 冻结常量
engine/review/replay.py                  P4.5 MasteryReviewState deterministic replay

data/review/mastery-review-state.schema.json  P4.5 machine-readable output schema
scripts/validate_review.py               fixture plan validator；P4.6/P4.7 未收口时保持 PENDING
data/review/fixture-plan.json            policy fixture plan；不与 contract-fixtures 混用
```

## 边界

```text
Review Model / Evidence contract
   != Mastery / Scheduling policy
   != MasteryReviewState replay（P4.5，已实现）
   != synthetic policy fixtures / validation report（P4.6 / P4.7 / P4.9）
   != Planner / 30-Day Plan / UI
```

本目录没有引入 SM-2、FSRS、forgetting curve、adaptive planner 或 AI 判断。Review Evidence 保存 policy-independent facts；P4.5 通过 [`REVIEW_OUTCOME_ADAPTER_V01.md`](REVIEW_OUTCOME_ADAPTER_V01.md) 以明确版本化 adapter 将可确定事实接入 policy，所有 replay 接受显式 `as_of` 与 IANA timezone。案例/能力 score 在 rubric 冻结前不会被猜测为 success/failure。

`progress-state/v0.1` 未被本窗口修改：Phase 4 的 mastery / review 结果是**独立派生层**，不是 ProgressState 的新字段。
