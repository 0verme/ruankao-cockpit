# Review Fixtures（当前为空）

本目录预留给 Phase 4 synthetic review fixtures，命名规则见
[`../fixture-plan.json`](../fixture-plan.json) 与
[`docs/PHASE4_TEST_MATRIX.md`](../../../docs/PHASE4_TEST_MATRIX.md)。

当前状态：

```text
TEST_DESIGN_READY
WAITING_FOR_FIXTURE_MATRIX_FINALIZATION（P4.6 / P4.7）
```

因此这里**暂时没有** `*.json` fixture。原因不是遗漏，而是：

- P4.1～P4.5 的 item / evidence / policy / replay contract 已冻结；
- fixture manifest 的 policy-dependent expected、edge-case matrix 与 synthetic
  fixture 文件仍未收口，避免在 fixture 资产中悄然扩展业务规则。

fixture matrix finalization 后按以下顺序补齐：

1. 在 `../fixture-plan.json` 中把对应条目从 `status: planned` 改为 `status: ready`；
2. 新增 `data/review/fixtures/<fixture_id>.json`，按
   `data/review/fixture-schema.draft.json` 填充事实与 `expected` / `expected_error`；
3. 运行 `python3 scripts/validate_review.py` 与
   `python3 -m unittest discover -s tests -v`。

约束：fixture 必须是 synthetic，不得复制第三方题干、选项、答案、解析、OCR 或 PDF 正文。
