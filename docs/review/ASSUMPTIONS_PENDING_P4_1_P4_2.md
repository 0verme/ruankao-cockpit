# ASSUMPTIONS_PENDING_P4_1_P4_2

> **状态：UNRESOLVED**
> 本文件记录 P4.3 / P4.4 规则设计窗口对 **P4.1 Review Model / P4.2 Review Evidence** 的显式假设。
> 这些假设**不是**既定事实，也不是本窗口的产出契约；它们只用于让规则设计可以并行推进。
> P4.1 / P4.2 的最终契约一旦落地，必须逐条对照本文件 rebase / reconcile。

机器可读的适配点：`engine/rules/review_policy_v01.py` 中的 `PolicyEvidence` 与
`derive_projection(evidence_by_item, ...)`；代码中以 `DEPENDS_ON_P4_1_P4_2` 标注。

---

## 假设清单

| ID | 假设 | 为什么本窗口需要它 | 如果 P4.1 / P4.2 决定不同 | 状态 |
| --- | --- | --- | --- | --- |
| A1 | 存在“policy-eligible evidence”序列：每条记录属于一个 review item，且带一个 outcome primitive。 | 状态机需要一个最小输入面。 | 若 P4.2 使用不同命名/结构，只在适配层重命名，不改本窗口的 transition 语义。 | UNRESOLVED |
| A2 | outcome primitive 取值集合为 `success` / `failure` / `insufficient`（或等价的“不可评估”表示）。 | 必须让“失败”与“证据不足”可区分。 | 若 P4.2 用 `null` 表达式表示证据不足，则调用方在适配层映射为 `insufficient`。 | UNRESOLVED |
| A3 | 每条 evidence 有稳定身份 `evidence_id`，且 `occurred_at` 为 timezone-aware instant。 | 排序键 `(UTC instant, evidence_id)` 需要稳定 tie-breaker。 | 若 P4.2 不提供独立 evidence id，使用 `event_id`；若同一事件可产生多条 evidence，需要 P4.2 提供子标识。 | UNRESOLVED |
| A4 | 一个 item 的 evidence 可以被完整枚举并排序，item 集合由调用方声明。 | policy kernel 不负责从 Progress Events 推导 item。 | 若 P4.1 由事件隐式发现 item，则 P4.5 负责求并集；policy kernel 不变。 | UNRESOLVED |
| A5 | v0.1 对 item kind（Topic / Question / Case Capability）使用同一套 policy 数学，且 item 之间不互相升级/降级。 | 避免跨粒度污染，保持可解释。 | 若 P4.1 要求按 kind 区分阈值，必须新增 `review-policy/.../v0.2`，不得原地改 v0.1。 | UNRESOLVED |
| A6 | 首次学习与复习的关系由 P4.1 / P4.2 决定；policy kernel 只处理“被 P4.2 判定为 policy-eligible 的 evidence”。 | 本窗口不得替 P4.1 拍板。 | 若 P4.2 只把部分记录视为 review evidence，则传入 kernel 的正是该子集；`evaluated_evidence_count` 的含义随之定义为“policy-eligible 条数”。 | UNRESOLVED |
| A7 | 实际 0 分 / 部分得分是否等价于 `failure`，由 P4.2 的版本化映射决定；policy kernel 只看 outcome。 | score → success 的映射需要采分点契约。 | 若 P4.2 定义 `score_ratio >= X → success`，该阈值属于 P4.2，并在 P4.2 文档中冻结；policy 不变。 | UNRESOLVED |
| A8 | `review_item` 的来源引用、provenance、无正文语义由 P4.1 负责，policy 不读取题干或正文。 | 版权边界。 | 无影响；policy kernel 不接触正文。 | UNRESOLVED |
| A9 | `mastered` 的 item 仍保留在 review 投影中（v0.1 选择 maintenance），因此 P4.1 的 item 集合不能因为 mastered 而被剪掉。 | `due_count` 不变量要求 item-level 投影完整。 | 若 P4.1 决定 mastered item 退出活动集合，`due_count` 语义与 maintenance 规则必须重新协商。 | UNRESOLVED |
| A10 | P4.5 的 `MasteryReviewState v0.1` 是独立派生层，不修改 `progress-state/v0.1` 的既有字段。 | 保持 Explore #4 的“边界不破坏既有 Progress Replay 语义”。 | 若 P4.5 需要扩展 progress replay，必须单独记录并保持 v0.1 fixture 语义不变。 | UNRESOLVED |

---

## 需要 reconcile 的对象

当 P4.1 / P4.2 契约可见时，逐项确认：

1. 证据记录字段名与本窗口 `PolicyEvidence` 的对应关系；
2. evidence 身份与排序键是否与 `(UTC instant, evidence_id)` 兼容；
3. “不可评估”是否显式可表示（且不会被伪装成 failure 或 0 分）；
4. item 集合与 item kind 是否影响 policy 数学；
5. 首次学习 / review 的边界是否与本窗口“首次 evidence 决定首个 due”的假设一致；
6. 是否存在同一事实同时作为 initial evidence 和 review evidence 的可能（重复计数风险）。

若有任何一项不成立，本窗口负责更新
[`MASTERY_POLICY_V01.md`](MASTERY_POLICY_V01.md) 与
[`REVIEW_SCHEDULING_POLICY_V01.md`](REVIEW_SCHEDULING_POLICY_V01.md)，
并在 PR 中明确写出 rebase / reconcile 结果；不得通过自行扩展 P4.1 / P4.2 schema 规避依赖。
