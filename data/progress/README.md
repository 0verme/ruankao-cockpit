# Progress Event Fixtures

这里的 JSON 只包含 synthetic learning facts，用于验证 `progress-event/v0.1` 和 `progress-state/v0.1`。

- `schema.json`：事件、状态、fixture 和 replay 规则契约；
- `fixtures/*.json`：合法 replay 样本和带 `expected_error` 的拒绝样本；
- 不包含个人真实学习记录、第三方题目正文或题库内容。

运行：

```bash
python3 scripts/validate_progress.py
```

事件是 source of truth；fixture 中没有人工维护的 aggregate state。
