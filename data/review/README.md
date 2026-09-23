# Review Model / Evidence v0.1

- `schema.json`：Review Item、Review Context Event、Review Evidence 的机器可读契约摘要。
- `mastery-review-state.schema.json`：`MasteryReviewState v0.1` 的机器可读输出 schema。
- `contract-fixtures/`：P4.1/P4.2 专用 projection fixtures（`review-fixture/v0.1`）。
- `fixtures/`：P4.6/P4.7 专用 replay fixtures（`mastery-review-fixture/v0.1`）；与 contract fixtures 分目录、分 schema。
- Review Item 的领域说明见 [`docs/review/REVIEW_MODEL_V01.md`](../../docs/review/REVIEW_MODEL_V01.md)。
- Evidence 字段、事实语义和 projection 见 [`docs/review/REVIEW_EVIDENCE_V01.md`](../../docs/review/REVIEW_EVIDENCE_V01.md)。

Progress Event v0.1 仍在 `data/progress/schema.json` 中维护；本目录不改变它的三类 event 语义。

运行 P4.1/P4.2 contract validator：

```bash
python3 scripts/validate_review_contract.py
```

Review Context Event 必须显式声明 `initial_learning` 或 `review`。没有 context 的 Progress Fact 不会被猜测成 Review Evidence。

P4.5 的 replay 入口为 `engine.review.replay.replay(...)`，输出 `mastery-review-state/v0.1`。Evidence 到 policy primitive 的保守 adapter 见 [`docs/review/REVIEW_OUTCOME_ADAPTER_V01.md`](../../docs/review/REVIEW_OUTCOME_ADAPTER_V01.md)：综合题 boolean 可确定映射；案例/能力 score 在 rubric 冻结前保留为 `insufficient`，不伪造 success/failure。

P4.6/P4.7 已冻结 `fixture-schema.v0.1.json` 和 `fixture-plan.json`，validator 会加载 `fixtures/*.json`，验证 output schema、期望投影/拒绝 category、版本、时间、证据 trace、aggregate invariants 与 determinism。fixture matrix PASS 是测试资产结论；Phase 4 全部 P4.1～P4.9 的 Gate 结论另见 [`docs/PHASE4_VALIDATION_REPORT.md`](../../docs/PHASE4_VALIDATION_REPORT.md)，最终 Gate 为 PASS。
