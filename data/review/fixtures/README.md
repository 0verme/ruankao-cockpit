# Frozen Mastery / Review Fixtures

本目录包含 P4.6/P4.7 冻结的 36 个 synthetic replay fixtures，schema 为 `mastery-review-fixture/v0.1`，结构由 [`../fixture-schema.v0.1.json`](../fixture-schema.v0.1.json) 定义。

每个 fixture 都记录显式 `as_of`、IANA timezone、冻结的 policy/adapter identities、事实输入、contract provenance，以及 expected state projection 或 rejection category。无效样本仅使用正式 replay/Review contract 定义的 rejection category。

fixture-plan status、policy symbols 与磁盘文件由以下入口交叉验证：

```bash
python3 scripts/validate_review.py
python3 -m unittest tests.test_review_fixture_plan tests.test_review_fixture_matrix
```

fixtures 只含 synthetic facts 和来源索引，不含第三方题干、选项、答案、解析、OCR 或 PDF 正文。P4.6/P4.7 已收口；P4.8/P4.9 尚未完成。
