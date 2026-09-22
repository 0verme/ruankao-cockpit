# Review Model / Evidence v0.1

- `schema.json`：Review Item、Review Context Event、Review Evidence 的机器可读契约摘要。
- `mastery-review-state.schema.json`：`MasteryReviewState v0.1` 的机器可读输出 schema。
- `contract-fixtures/`：P4.1/P4.2 专用 synthetic projection fixtures；不与 P4.6/P4.7 的 policy fixture 目录混用。
- Review Item 的领域说明见 [`docs/review/REVIEW_MODEL_V01.md`](../../docs/review/REVIEW_MODEL_V01.md)。
- Evidence 字段、事实语义和 projection 见 [`docs/review/REVIEW_EVIDENCE_V01.md`](../../docs/review/REVIEW_EVIDENCE_V01.md)。

Progress Event v0.1 仍在 `data/progress/schema.json` 中维护；本目录不改变它的三类 event 语义。

运行 P4.1/P4.2 contract validator：

```bash
python3 scripts/validate_review_contract.py
```

Review Context Event 必须显式声明 `initial_learning` 或 `review`。没有 context 的 Progress Fact 不会被猜测成 Review Evidence。

P4.5 的 replay 入口为 `engine.review.replay.replay(...)`，输出 `mastery-review-state/v0.1`。Evidence 到 policy primitive 的保守 adapter 见 [`docs/review/REVIEW_OUTCOME_ADAPTER_V01.md`](../../docs/review/REVIEW_OUTCOME_ADAPTER_V01.md)：综合题 boolean 可确定映射；案例/能力 score 在 rubric 冻结前保留为 `insufficient`，不伪造 success/failure。
