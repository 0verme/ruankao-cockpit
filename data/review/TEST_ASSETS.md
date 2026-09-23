# Review / Mastery 测试资产（Phase 4）

本目录属于 **Phase 4：Mastery / Review Scheduling v0.1**，与 `data/progress/` 保持独立；Review 结果是 Progress facts 的独立派生层，不修改 Progress Replay v0.1。

## 当前状态

```text
P4.6 Synthetic fixtures: FROZEN
P4.7 Unit tests / edge cases: COMPLETE
P4.8 Documentation sync: COMPLETE
P4.9 Validation report: COMPLETE
Phase 4 Gate: PASS（见 docs/PHASE4_VALIDATION_REPORT.md）
```

## 文件与 schema 边界

| 文件 | 作用 |
| --- | --- |
| `schema.json` | Review Item / Context Event / Evidence v0.1 contract |
| `contract-fixtures/` | P4.1/P4.2 projection fixtures，使用 `review-fixture/v0.1` |
| `fixture-plan.json` | P4.6/P4.7 replay fixture matrix、冻结 policy symbols 与 contract provenance |
| `fixture-schema.v0.1.json` | P4.6/P4.7 正式 fixture schema：`mastery-review-fixture/v0.1` |
| `fixture-schema.draft.json` | Historical draft，已 superseded；仅保留设计 provenance |
| `fixtures/` | 36 个 synthetic replay fixtures，含 expected state projection 或 rejection category |
| `mastery-review-state.schema.json` | P4.5 output state schema |

Policy values 只引用 P4.1–P4.5 冻结契约。Case/capability score 继续映射为 `insufficient`；不设置阈值。

## 验证入口

```bash
python3 scripts/validate_review.py
python3 -m unittest tests.test_review_fixture_plan tests.test_review_determinism_harness tests.test_review_fixture_matrix
python3 -m unittest discover -s tests
```

`validate_review.py` 成功时报告 `REVIEW_FIXTURE_MATRIX_PASS`，该 validator 只判定 fixture matrix；Phase 4 全 Gate 结论由 `docs/PHASE4_VALIDATION_REPORT.md` 汇总，当前结论为 PASS。
