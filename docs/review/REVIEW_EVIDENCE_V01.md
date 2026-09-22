# Review Evidence Contract v0.1

> 状态：**FROZEN（P4.2）**。本文定义 Review Context Event 和 policy-neutral Review Evidence；不实现 mastery、success/failure policy 或 scheduling。
>
> 上游：`progress-event/v0.1`。机器契约：[`data/review/schema.json`](../../data/review/schema.json)。领域身份和 D1–D12 decision record 见 [`REVIEW_MODEL_V01.md`](REVIEW_MODEL_V01.md)。

## 1. 为什么是独立 contract

Progress Event v0.1 已冻结三类事件：

```text
comprehensive_attempt
case_attempt
study_session
```

它们保存 Progress Facts，但没有可靠的 initial/review context。直接增加字段或改变 event type 会改变已有 Progress v0.1 的语义，并迫使 Progress replay 处理尚未冻结的 review policy。因此本阶段建立独立的：

```text
Progress Event v0.1
        +
Review Context Event v0.1
        ↓
Review Evidence v0.1
```

这不是第二个 Progress source of truth：Progress Event 仍保存原始事实，Review Context Event 只保存对某个事实/Item 的显式上下文关联，Evidence 可从两者删除后重建。

## 2. Review Context Event

### 2.1 字段

| 字段 | 要求 | 语义 |
| --- | --- | --- |
| `schema_version` | `review-event/v0.1` | 事件 contract 版本 |
| `event_id` | 非空稳定 ID | Review context 的 immutable identity |
| `event_type` | `review_context` | 固定事件类型 |
| `source_event_id` | 必填 | 指向已有 Progress Attempt Event |
| `review_item_id` | 必填 | 指向 active Review Item |
| `attempt_context` | `initial_learning` 或 `review` | 显式声明首次学习或复习 |
| `occurred_at` | timezone-aware ISO 8601 | 必须与 source event 的 instant 相同 |

示例（synthetic reference，不含任何第三方正文）：

```json
{
  "schema_version": "review-event/v0.1",
  "event_id": "ctx-001",
  "event_type": "review_context",
  "source_event_id": "attempt-001",
  "review_item_id": "review/question/synthetic/q-001",
  "attempt_context": "review",
  "occurred_at": "2026-01-01T10:00:00+08:00"
}
```

### 2.2 规则

- context event 必须指向一个已验证的 `comprehensive_attempt` 或 `case_attempt`；`study_session` 不能成为 item evidence 的 source。
- source event 与 item 的关联必须匹配：question 对应 question reference，topic 必须出现在 `topics`，case capability 必须出现在 `capabilities`。
- 一个 `source_event_id + review_item_id` 最多一个 context event。不能把一条事实同时标记为 initial 和 review，避免重复计数。
- 没有 context event 的 Progress Fact 不会自动投影为 Review Evidence；缺失上下文不是 initial，也不是 review。
- context event 不复制题干、选项、答案、解析、PDF/OCR 或自由文本。

## 3. Evidence record

### 3.1 正式字段

| 字段 | 要求 | 语义 |
| --- | --- | --- |
| `schema_version` | `review-evidence/v0.1` | Evidence contract 版本 |
| `evidence_id` | `evidence/<source_event_id>/<review_item_id>` | 可重建的稳定 evidence identity |
| `review_item_id` | 必填 | Evidence 所属 item |
| `item_kind` | `topic` / `question` / `case_capability` | 必须与 item 完全一致 |
| `source_event_id` | 必填 | 原始 Progress Fact |
| `source_event_type` | `comprehensive_attempt` / `case_attempt` | 原始事实类型 |
| `review_event_id` | 必填 | 产生上下文的 Review Event |
| `occurred_at` | timezone-aware | source event 的 UTC-equivalent instant |
| `attempt_context` | `initial_learning` / `review` | 从 context event 显式复制 |
| `evidence_kind` | 固定枚举 | 事实类型，不是策略结论 |
| `evidence_value` | object 或 null | policy-independent fact |
| `evidence_status` | `supported` / `insufficient_evidence` / `unsupported` | 是否有足够事实 |
| `source_reference` | source ID/commit/path；含 source question ID | 可审计来源，不含正文 |

Evidence 不含：`success`、`failure`、`mastery`、`review_due`、`review_interval`、`due_at` 或 scheduling 参数。

### 3.2 evidence kind 与事实值

#### 综合题 / topic 或 question

```json
{
  "evidence_kind": "comprehensive_correctness",
  "evidence_status": "supported",
  "evidence_value": {"correct": true}
}
```

`correct` 是上游明确记录的事实。Evidence 层不把它重命名为 success，也不把 topic 的累计 accuracy 当成 item outcome。

#### 案例 question

有明确总分时：

```json
{
  "evidence_kind": "case_score",
  "evidence_status": "supported",
  "evidence_value": {"score_earned": 7, "score_possible": 10}
}
```

没有总分时：

```json
{
  "evidence_kind": "case_score",
  "evidence_status": "insufficient_evidence",
  "evidence_value": null
}
```

不能把缺少 score 当作错误或零分。

#### 案例 capability

只有 exact capability score 才能生成：

```json
{
  "evidence_kind": "case_capability_score",
  "evidence_status": "supported",
  "evidence_value": {"score_earned": 4, "score_possible": 6}
}
```

如果案例只引用 capability，没有 `capability_scores` 中的对应 score：

```json
{
  "evidence_kind": "case_capability_score_missing",
  "evidence_status": "insufficient_evidence",
  "evidence_value": null
}
```

案例 aggregate score 永远不会被复制到各 capability。

#### 案例 topic

`case_attempt.topics` 是 coverage/context，不是 topic-level score。若显式关联 topic review，v0.1 输出：

```json
{
  "evidence_kind": "case_topic_score_unavailable",
  "evidence_status": "unsupported",
  "evidence_value": null
}
```

这比伪造一个 topic score 更安全；后续若要支持案例 topic evidence，必须先定义实际 topic attribution contract。

## 4. 确定性生成

`engine.review.project_review_evidence(...)` 执行以下纯投影：

1. 使用现有 Progress validator 验证所有 Progress Events，不改变 Progress replay 语义。
2. 验证 Review Item catalog：stable ID、canonical reference、taxonomy/capability membership、source reference、duplicate。
3. 验证每个 context event 的 source/item 关系、显式 context、timezone-aware timestamp 和唯一性。
4. 对每个 context event 按 item kind 和 source event 的事实字段选择 evidence kind/value/status。
5. 将 source event 的 `occurred_at` 规范化为 UTC `Z` 表示；不调用当前时间。
6. 按 `UTC occurred_at + source_event_id + review_item_id + review_event_id` 排序。
7. 验证生成结果的 item kind、source reference、evidence ID、status/value 和时间一致性。

相同的：

```text
Progress Events
+ Review Context Events
+ Review Item catalog
+ taxonomy/capability version
```

必定产生相同的 Evidence。打乱输入顺序不会改变结果；删除 Evidence 后可以重新投影。Evidence 本身不接受 policy version，也不预先决定 success/failure。

## 5. 时间与 null 语义

- 所有 evidence timestamp 必须带 timezone；naive timestamp 拒绝。
- UTC 等价的 `+08:00` 和 `Z` 表示指向同一 instant，规范化输出相同。
- Evidence timestamp 来自 source fact，不由 review session 日期或“距上次学习天数”推断。
- `supported` 的 `correct` 或 score 是事实；`insufficient_evidence` / `unsupported` 的 value 必须为 `null`。
- null/insufficient、实际错误、实际零分保持可区分。

## 6. Validator 覆盖

`engine/review` 与 `tests/test_review_contract.py` 覆盖：

- 稳定 item ID 不受 name、题干、source path/commit 变化影响；
- unknown item kind、unknown topic、unknown capability；
- missing canonical/source reference；
- duplicate item/context/evidence；
- question identity 不依赖题干；
- evidence/item-kind mismatch；
- capability evidence 缺失的 `insufficient_evidence`；
- case aggregate 不复制到 topic/capability；
- source path traversal、绝对/本地 path；
- timezone-naive evidence timestamp；
- policy 字段混入 Evidence 的拒绝；
- input order independence 和 UTC timestamp normalization。

## 7. Outcome adapter 与下游边界

P4.3/P4.4 policy kernel 的 `PolicyEvidence` 使用 `success / failure / insufficient` primitive；本 contract 刻意不把这些 policy/outcome 结论写入 Evidence。两层之间必须有显式 adapter：

- `comprehensive_correctness.correct=true/false` 是明确二值事实，adapter 可以确定性地映射为 success/failure；`insufficient_evidence` 只能映射为 insufficient。
- `case_score` 与 `case_capability_score` 只保存 score pair。v0.1 没有冻结 score threshold、采分点 rubric 或 success mapping，因此 P4.5 使用独立、版本化的保守 adapter（[`REVIEW_OUTCOME_ADAPTER_V01.md`](REVIEW_OUTCOME_ADAPTER_V01.md)）：score 保留为 raw fact，policy outcome 为 `insufficient`，不产生 success/failure。
- adapter 不能由 AI、自由文本或当前时间产生，也不能把 score 缺失改写成 failure/zero；adapter version 和解释由 replay 输出记录。未来 score rubric 必须使用新的 adapter version。

本 contract 不回答：

- score 达到什么阈值才算 success；
- 没有 evidence 的 item 是什么 mastery state；
- interval、due、overdue、maintenance review；
- `as_of` 下的 Mastery / Scheduling replay。

这些是 P4.3/P4.4/P4.5 的下游版本化决策。若下游需要直接修改 Evidence 的事实语义，必须先提出 `BLOCKING_DECISION`，不能在 policy 实现里隐式完成。完整 reconcile 见 [`ASSUMPTIONS_PENDING_P4_1_P4_2.md`](ASSUMPTIONS_PENDING_P4_1_P4_2.md)。
