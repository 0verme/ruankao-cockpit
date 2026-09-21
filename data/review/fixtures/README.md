# Review Fixtures（当前为空）

本目录预留给 Phase 4 synthetic review fixtures，命名规则见
[`../fixture-plan.json`](../fixture-plan.json) 与
[`docs/PHASE4_TEST_MATRIX.md`](../../../docs/PHASE4_TEST_MATRIX.md)。

当前状态：

```text
TEST_DESIGN_READY
WAITING_FOR_CONTRACT_FREEZE（P4.1 / P4.2 / P4.3 / P4.4 / P4.5）
```

因此这里**暂时没有** `*.json` fixture。原因不是遗漏，而是：

- `review_item_id`、review evidence 来源、mastery 状态名、success 阈值和
  interval ladder 尚未冻结，任何 `expected` / `expected_error` 都会提前发明
  业务规则；
- 事件 schema 是否扩展也尚未决定，连 `events` 都无法稳定书写。

contract freeze 后按以下顺序补齐：

1. 在 `../fixture-plan.json` 中把对应条目从 `status: planned` 改为 `status: ready`；
2. 新增 `data/review/fixtures/<fixture_id>.json`，按
   `data/review/fixture-schema.draft.json` 填充事实与 `expected` / `expected_error`；
3. 运行 `python3 scripts/validate_review.py` 与
   `python3 -m unittest discover -s tests -v`。

约束：fixture 必须是 synthetic，不得复制第三方题干、选项、答案、解析、OCR 或 PDF 正文。
