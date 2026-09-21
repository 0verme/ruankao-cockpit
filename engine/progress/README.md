# Progress Model v0.1

本目录实现 Phase 3 的两层基础模型：

```text
Immutable Events
      ↓ replay
ProgressState v0.1
```

`events` 是事实源；`ProgressState` 是可删除、可重建、可复算的派生结果。仓库不要求人工维护 aggregate state。

## Event contract

机器契约见 [`data/progress/schema.json`](../../data/progress/schema.json)。v0.1 有三类事件：

- `comprehensive_attempt`：一次综合题提交，保存 `correct` 事实；错误可以带一个稳定 `error_cause`。
- `case_attempt`：一次案例子问题提交，保存可选的总分证据和可选的 capability-level score evidence；不使用 `correct`。
- `study_session`：一次有测量时长的学习会话；只产生分钟事实，不推断质量、专注度或完成度。

所有事件都必须包含：

```text
event_id
schema_version = progress-event/v0.1
event_type
occurred_at = timezone-aware ISO 8601
```

题目使用来源引用而不是 Golden Set ID：

```json
{
  "source_id": "source-or-bank-id",
  "source_commit": "40-char immutable revision",
  "source_path": "repository/relative/path",
  "source_question_id": "source-defined-question-id",
  "golden_set_record_id": "optional enhancement"
}
```

事件只保存事实和短备注，不保存题干、选项、答案、解析、OCR 或 PDF 正文。Attempt 可选保存 `assessment_id` 和关联 `session_id`，但二者在 v0.1 不参与指标。

### Error cause

错误归因是稳定机器枚举：

```text
knowledge_gap
reading_error
calculation_error
scoring_point_expression
```

错误可以不分类；这种事件进入 `unclassified_error_count`，不会被强行归入某一类。`note` 仅供人读，不参与指标。

### Case score evidence

案例可引用多个 capability，但不能把总分复制给每个 capability：

```json
{
  "capabilities": ["CASE.DATA_DESIGN", "CASE.SOLUTION_TRADEOFF"],
  "score_earned": 6,
  "score_possible": 10,
  "capability_scores": [
    {"capability_id": "CASE.DATA_DESIGN", "score_earned": 4, "score_possible": 6}
  ]
}
```

只有 `capability_scores` 中有实际证据的 capability 才会得到 capability metric。仅有引用的 capability 在状态中保持 `evidence_status: insufficient_evidence`，不会产生 `score_ratio` 的非空值。

## Replay API

`engine.progress.replay.replay(events, taxonomy, capabilities)` 是纯 deterministic 函数：

- `events`：事件对象序列；
- `taxonomy`：`taxonomy/taxonomy.json` 解析后的对象；
- `capabilities`：`taxonomy/capabilities.json` 解析后的对象；
- 返回普通 JSON-compatible `dict`，版本为 `progress-state/v0.1`。

Replay 先验证全部事件，再按：

```text
UTC(occurred_at) + event_id
```

排序。重复 `event_id`、未知 topic/capability、naive timestamp、越界分值和非法来源路径都会失败；不会静默跳过或去重。

## Counting rules

### Comprehensive / topic

全局综合指标只统计综合题：一条事件只增加一次 global attempt。事件列出的每个直接 topic 各增加一次 topic evidence，所以 multi-topic 时：

```text
global attempt_count = 1
topic A attempt_count = 1
topic B attempt_count = 1
```

因此 global count 不等于 topic counts 之和，这是正常且有意的语义。父节点只用于 coverage closure，不自动复制到 topic attempt count。

### Case / capability

每个 case event 只增加一次 case attempt。总分按：

```text
sum(score_earned) / sum(score_possible)
```

聚合，而不是平均每题比例。capability 同样按各自实际 score evidence 加权；没有 evidence 就不计算。

### Null semantics

没有综合题尝试时：`accuracy = null`；没有 score evidence 时：`score_ratio = null`。这与“有数据但全部错误 / 得分为 0”不同。

Coverage 的分母是传入 taxonomy 中全部 L1/L2/L3 节点；引用 L3 会通过 parent closure 覆盖 L2/L1。Coverage ratio 在 taxonomy 分母非零时按 `covered / total` 计算。

## Boundary

本阶段没有实现：

- mastery / mastered；
- review_due / review_interval；
- SM-2 / FSRS / forgetting curve；
- adaptive planner、30-Day Plan 实例化；
- AI 自动评分；
- database、API、UI。
