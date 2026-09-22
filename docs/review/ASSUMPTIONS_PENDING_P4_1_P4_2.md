# ASSUMPTIONS_PENDING_P4_1_P4_2

> **状态：RECONCILED（P4.1 / P4.2 已冻结）**
> 历史状态：`UNRESOLVED`（P4.1/P4.2 contract freeze 前）；以下记录已完成逐条 reconcile。
> 本文件记录 P4.3 / P4.4 规则设计窗口对 Review Model / Review Evidence 的并行假设，以及本窗口完成后的逐条 reconcile 结果。
>
> Review Item / Context Event / Evidence 的正式定义见 [`REVIEW_MODEL_V01.md`](REVIEW_MODEL_V01.md) 与 [`REVIEW_EVIDENCE_V01.md`](REVIEW_EVIDENCE_V01.md)。本文件不把 P4.3/P4.4 的 policy 反向升级为 Evidence 事实。

机器可读的 policy 适配点：`engine/rules/review_policy_v01.py` 中的 `PolicyEvidence` 与
`derive_projection(evidence_by_item, ...)`。Policy kernel 消费的是下游 adapter shape，不直接定义 Review Evidence schema。

---

## 假设清单与 reconcile

| ID | 原并行假设 | reconcile 结果 | 状态 |
| --- | --- | --- | --- |
| A1 | 存在属于一个 review item 且带 outcome primitive 的 policy-eligible evidence 序列。 | 已冻结 `review-evidence/v0.1`：一条 record 属于一个 item，保存 raw `evidence_kind/value/status`。它不直接保存 outcome primitive；由显式 adapter 提供给 policy kernel。 | RECONCILED_WITH_ADAPTER |
| A2 | outcome primitive 为 `success` / `failure` / `insufficient` 或等价表示。 | Evidence 使用 `supported`、`insufficient_evidence`、`unsupported`。`insufficient_evidence` 明确不是 failure；`success/failure` 不写入 Evidence。综合题的 `correct` 可由 adapter 无歧义映射，score 类 evidence 见 BLOCKING_DECISION。 | BLOCKING_DECISION（仅 score outcome adapter） |
| A3 | 每条 evidence 有稳定 `evidence_id`，`occurred_at` 是 timezone-aware instant。 | 已冻结 `evidence/<source_event_id>/<review_item_id>`，timestamp 必须 aware，并规范化为 UTC；同 instant 可由稳定 source/item ID 排序。 | RECONCILED |
| A4 | item 的 evidence 可枚举排序，item 集合由调用方声明。 | Item catalog 是显式输入；只有显式 `review_context` 才投影 evidence；按 UTC instant + source/event/item ID 排序。没有 context 的 Progress Fact 不隐式进入集合。 | RECONCILED |
| A5 | Topic / Question / Case Capability 使用同一套 policy 数学，item 不互相升级/降级。 | 三类 item 独立 identity 和 evidence mapping，不跨粒度复制或升级。是否使用同一套下游数学由 policy adapter 负责，本窗口不改变 P4.3/P4.4 的 policy contract。 | RECONCILED_WITH_ADAPTER |
| A6 | 首次学习与复习由 P4.1/P4.2 决定。 | `review-event/v0.1` 的 `review_context` 必须显式写 `initial_learning` 或 `review`；同一 source event + item 最多一个 context；没有 context 不产生 Evidence。 | RECONCILED |
| A7 | score 是否等价于 failure/success 由 Evidence contract 的版本化映射决定。 | Evidence 只保存 score pair；没有冻结阈值、rubric 或采分点 outcome 规则，不伪造 success/failure。需要 score outcome 的 P4.5 adapter 必须先采用独立版本化 outcome contract。 | BLOCKING_DECISION |
| A8 | item 的来源引用、provenance、无正文语义由 P4.1 负责。 | 已冻结：source_id、immutable source_commit、repository-relative source_path；question 另需 source_question_id；不复制第三方正文。 | RECONCILED |
| A9 | mastered item 仍保留在 review projection 中，供 maintenance。 | P4.4 已冻结 mastered maintenance interval；本窗口保持 item identity/evidence 可追踪，不删除历史 evidence。active/retired item 迁移另有显式规则。 | RECONCILED_BY_P4_4 |
| A10 | `MasteryReviewState v0.1` 是独立派生层，不修改 `progress-state/v0.1`。 | 保持成立。本窗口没有修改 `data/progress/schema.json` 或 Progress replay；Review Evidence 是独立可重建 projection。 | RECONCILED |

---

## BLOCKING_DECISION：score evidence 的 policy outcome adapter

P4.3/P4.4 的 `PolicyEvidence` 需要 `success` / `failure` / `insufficient` primitive，但 P4.2 明确要求 Evidence 尽量 policy-neutral。当前冻结结果是：

1. `comprehensive_correctness` 的 raw fact 是 `correct: true/false`；下游 adapter 可以确定性地映射为 `success/failure`。`insufficient_evidence` 映射为 `insufficient`，不能变成 failure。
2. `case_score` 和 `case_capability_score` 只有 `score_earned/score_possible` fact。v0.1 没有决定 `score >= X`、采分点 rubric 或其他 success threshold，因此不能把 score 直接喂成 success/failure。
3. P4.5 若要消费案例/能力 evidence，必须先冻结一个独立、版本化的 outcome mapping（建议 `review-outcome/.../v0.1`），记录 rubric/threshold、适用 item kind、版本和解释；该映射不能回写到 Evidence record，也不能由 AI 产生。
4. 在该 mapping 冻结前，P4.5 不得宣称 case/capability mastery 已由 raw score 产生。可以保留 Evidence，或在明确 adapter 语义下将其视为 `insufficient`；不得静默视为 failure/zero。

这不是本窗口偷做 P4.3/P4.4，而是向 P4.5 暴露的明确阻塞决策。建议由 P4.5/相关 policy owner 先确认 outcome adapter，再接入 `PolicyEvidence`。

---

## 已完成的 contract 对应关系

1. 证据字段：`evidence_id`、`review_item_id`、`item_kind`、`source_event_id`、`occurred_at`、`evidence_kind`、`evidence_value`、`evidence_status`、`source_reference` 均已冻结。
2. Evidence 身份和排序：稳定 ID + UTC-aware timestamp，兼容 policy kernel 的排序要求。
3. 不可评估语义：`insufficient_evidence` / `unsupported` 显式可表示，不伪装为 failure 或 0 分。
4. item 集合：三类 item 的 identity 与 catalog 显式输入，不跨粒度共享 state。
5. initial/review：context event 显式声明，不能由 session type、自由文本或时间间隔推断。
6. 重复计数：同一个 source event + item 最多一条 context/evidence。

P4.5 需要更新 policy adapter 或报告 score outcome 阻塞时，应在 PR / validation report 中引用本文件的 `BLOCKING_DECISION`，不得通过扩展 Progress v0.1 或在 Evidence 中偷偷加入 `success` 字段规避。
