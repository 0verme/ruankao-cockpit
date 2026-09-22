# Review Outcome Adapter v0.1

> 状态：**FROZEN（P4.5）**。这是 Review Evidence 到 P4.3/P4.4 policy primitive 的显式、可重放 adapter；它不修改 `review-evidence/v0.1`，也不定义 score threshold。

## 1. Identity

```text
adapter_id      review-outcome/raw-facts
adapter_version v0.1
```

`MasteryReviewState v0.1` 必须记录该 adapter 的完整版本。任何 success/failure 映射规则变化都必须使用新的 adapter version，而不是修改 v0.1。

## 2. Mapping

| Review Evidence | Policy outcome | Reason |
| --- | --- | --- |
| `comprehensive_correctness` + `supported` + `correct=true` | `success` | `comprehensive_correctness_fact` |
| `comprehensive_correctness` + `supported` + `correct=false` | `failure` | `comprehensive_correctness_fact` |
| `insufficient_evidence` | `insufficient` | `insufficient_evidence` |
| `unsupported` | `insufficient` | `unsupported_evidence` |
| `case_score` + `supported` | `insufficient` | `score_outcome_mapping_unfrozen` |
| `case_capability_score` + `supported` | `insufficient` | `score_outcome_mapping_unfrozen` |

`insufficient` 是 policy no-op，不是 failure。案例/能力的 score pair 仍完整保留在 replay 输出的 evidence trace 中；因为 P4.2 没有冻结 rubric 或阈值，v0.1 不把任何 score（包括真实 0 分）猜测成 success 或 failure。

因此：

```text
raw supported score fact
!=
policy success/failure
```

这不是静默忽略：输出同时保留 raw `evidence_status`、`evidence_value`、`evidence_kind`、adapter version 与 `policy_outcome_reason`。未来若要让 score 驱动 mastery，必须新增独立的、版本化的 score outcome adapter。

## 3. Boundary

- adapter 只消费已由 `engine.review.project_review_evidence(...)` 校验的 Evidence。
- adapter 不读 `ProgressState` 的 accuracy、case score ratio、topic 聚合或自由文本。
- adapter 不调用系统时间，不改变输入，不写文件、数据库或网络。
- `MasteryReviewState` 的 mastery / scheduling 仍完全由冻结的 `review_policy_v01` kernel 计算。
- `future_evidence` 仍由 replay fail closed 拒绝；不能由 adapter 过滤。

## 4. Explainability

每个 item 的 `evidence[]` trace 记录：

```text
evidence_id
source_event_id
review_event_id
occurred_at
attempt_context
evidence_kind
evidence_status
evidence_value
source_reference
policy_outcome
policy_outcome_reason
```

这使得 `new`、`learning`、`mastered`、`not_scheduled`、`due` 和 `overdue` 都能回溯到原始 evidence、显式 outcome mapping、policy version、`as_of` 与 timezone。
