# Progress Model v0.1 + Deterministic Replay Validation

- **阶段**：Phase 3 — Progress Model v0.1 + Deterministic Replay
- **分支**：`feat/progress-model-v01`
- **契约**：`data/progress/schema.json`
- **Replay 实现**：`engine/progress/model.py`、`engine/progress/replay.py`
- **验证日期**：2026-09-21

## 1. Contract

本阶段只实现：

```text
Immutable Facts / Events
        ↓
Deterministic Replay
        ↓
ProgressState v0.1 基础聚合
```

事件是 source of truth；`ProgressState` 是 replay result，可以删除后由同一组事件、taxonomy/capability 目录和规则版本重新生成。没有人工维护 aggregate state。

### Schema versions

```text
progress-event/v0.1
progress-state/v0.1
progress-fixture/v0.1
progress-replay/v0.1
```

taxonomy 与 capability 使用当前 `0.1` 目录版本。State 同时记录 `event_schema_version`、`replay_rule_version`、`taxonomy_version` 和 `capability_version`。

### Event types

#### `comprehensive_attempt`

一次综合题提交事实：

```text
event_id
schema_version
event_type
occurred_at
question reference
topics[]
correct
error_cause?          # 仅 incorrect 时可选
assessment_id?        # 预留引用，不参与当前指标
session_id?           # 可选关联 study_session，不参与当前指标
note?                 # 人读备注，不参与指标
```

`question` 使用来源引用，不依赖 Golden Set：

```text
source_id
source_commit
source_path
source_question_id
golden_set_record_id?  # 可选增强引用
```

不保存题干、选项、答案、解析、OCR 或 PDF 正文。

#### `case_attempt`

案例不能用布尔 `correct` 表示。事件包含：

```text
event_id
schema_version
event_type
occurred_at
question reference
topics[]
capabilities[]
score_earned? + score_possible?
capability_scores[]?
assessment_id?
session_id?
note?
```

总分证据是可选的成对整数；若存在，`score_possible > 0` 且 `0 <= score_earned <= score_possible`。`capability_scores` 每项包含：

```text
capability_id
score_earned
score_possible
```

能力引用和能力分数证据分开：只有真实 `capability_scores` 才能产生 capability metric。只引用 capability 但没有评分证据时，状态为 `insufficient_evidence`，不制造 ratio。

#### `study_session`

最小学习时长事实：

```text
event_id
schema_version
event_type
occurred_at
session_id
started_at
ended_at? | duration_minutes
activity_type
topics[]?           # context only
note?
```

所有机器时间必须带 timezone。`occurred_at` 定义为 session start，并且与 `started_at` 相同。`duration_minutes` 是非负整数；若同时提供 `ended_at`，必须与精确的整分钟 elapsed duration 一致。

## 2. Append-only / identity

- `event_id` 是全局事件身份；重复 ID 是 validation error，不静默去重。
- `session_id` 在 study session 事件中也必须唯一，避免同一会话被重复累计。
- 已发生事件不原地修改。v0.1 不实现 correction / superseding event；未来修正应通过版本化的更正语义扩展，而不是覆盖历史对象。
- `note` 允许人读自由文本，但不参与 deterministic metric。

## 3. Replay

Replay API：

```python
replay(events, taxonomy, capabilities) -> ProgressState
```

处理步骤：

1. 验证整个事件集合、目录引用、时间、score bounds、来源路径和内容边界；验证失败时不产出部分状态。
2. 将 `occurred_at` 转换为 UTC。
3. 按以下稳定 key 升序排序：

```text
UTC(occurred_at) + event_id
```

4. 依事件类型累加事实派生指标。
5. 以固定的 taxonomy/capability ID 顺序序列化结果。

同一事件集合无论 JSON 原始排列怎样，都会得到相同的 state。ratio 使用整数 numerator / denominator 计算，序列化统一采用四位小数、deterministic half-up rounding；事实中的 count 和 score 始终保留整数。

## 4. Metrics

### Global

`global` 只统计有 `correct` 事实的综合题：

```text
attempt_count  = comprehensive event 数
correct_count  = correct == true 的事件数
incorrect_count = correct == false 的事件数
accuracy       = correct_count / attempt_count
```

`attempt_count == 0` 时 `accuracy = null`，不把未作答伪装为 0%。案例单独放在 `case`，不混入 global correct/incorrect。

### Topic

`topics[topic_id]` 只统计综合题的直接 topic 引用：

```text
attempt_count  = 引用该 topic 的综合题事件数
correct_count
incorrect_count
accuracy       = correct_count / attempt_count
```

未被作答的 topic 仍在 state 中，count 为 0、`accuracy = null`。父 topic 不会因为子 topic 被引用而复制 attempt evidence；父闭包只用于 coverage。

### Case / Capability

案例全局聚合：

```text
case.attempt_count          = case event 数
case.scored_attempt_count   = 有总分 evidence 的 case event 数
case.score_earned           = sum(score_earned)
case.score_possible         = sum(score_possible)
case.score_ratio            = sum(score_earned) / sum(score_possible)
```

例如 `2/4` 和 `5/6` 的结果是 `7/10 = 0.7`，不是两个百分比的简单平均。

Capability 聚合只使用对应的真实 score evidence：

```text
capabilities[id].attempt_count = 该 capability 的 score evidence 数
score_earned                   = 对应 evidence 的 earned 总和
score_possible                 = 对应 evidence 的 possible 总和
score_ratio                   = score_earned / score_possible
```

一个案例只增加一次 `case.attempt_count`，但多个 capability 可以分别获得自己的 score evidence。不能因为案例总分 `8/10` 就向所有 capability 复制 `0.8`。没有 evidence 时 `score_ratio = null`，并输出 `evidence_status = insufficient_evidence`。

### Error

错误指标只来自 incorrect comprehensive attempts：

```text
error_count              = incorrect_count
classified_error_count   = 有 error_cause 的错误数
unclassified_error_count = 没有 error_cause 的错误数
```

固定枚举：

```text
knowledge_gap
reading_error
calculation_error
scoring_point_expression
```

`error_count_by_cause` 按单一归因计数。`error_cause_mix` 的 denominator 明确为 `classified_error_count`，即：

```text
cause_count / classified_error_count
```

存在未分类错误时，未分类项不会被硬塞入四类；四类 mix 之和只对已分类错误为 1。没有已分类错误时各 mix 为 `null`。

### Coverage

Coverage 不输出无分母定义的单一数字，而分别输出：

```text
coverage.l1
coverage.l2
coverage.l3
```

每一层包含：

```json
{"covered": 8, "total": 13, "ratio": 0.6154}
```

分母是传入 taxonomy 中该层的全部 canonical nodes（当前为 L1=13、L2=27、L3=110）。综合题和案例题的 question topics 都贡献 coverage；study session 的 context topics 不贡献 coverage。引用 L3 时 parent closure 会同时覆盖它的 L2 和 L1；这不改变 topic attempt count。

### Study

```text
study.session_count = study_session event 数
study.study_minutes = sum(duration_minutes)
```

只表示记录的时长事实，不推导专注度、学习质量、效率分、完成度或掌握度。

## 5. Null semantics

```text
no comprehensive attempts       → global.accuracy = null
no topic attempts               → topics[id].accuracy = null
no aggregate case score         → case.score_ratio = null
no capability score evidence    → capabilities[id].score_ratio = null
no classified errors            → error_cause_mix[*] = null
```

“没有证据”与“有证据但全部错误 / 得分为 0”保持可区分。

## 6. Determinism validation

Synthetic fixtures 位于 `data/progress/fixtures/`：

- 单道综合题正确：`basic.json`；
- 单道综合题错误：`incorrect.json`；
- multi-topic：`multi-topic.json`；
- 多次案例 / multi-capability score：`case-score.json`；
- 无 capability score evidence：`case-no-capability-evidence.json`；
- 四种 error cause + unclassified：`errors.json`；
- study duration：`study.json`；
- 非时间顺序输入：`ordering.json`；
- zero-attempt：`zero.json`；
- duplicate、unknown topic、unknown capability、越界 score、naive timestamp、source path traversal 和非法 error cause：对应 expected rejection fixtures；绝对路径拒绝由 replay validator 和 unittest 运行时构造验证。

Validator 对每个合法 fixture 验证：

```text
replay(events) == replay(events)
replay(events) == replay(deterministically_shuffled(events))
```

并验证重复 ID、未知引用、score bounds、时间和状态越界字段。当前共 16 个 fixture：9 个成功 replay、7 个预期拒绝。

## 7. Validation commands

```bash
python3 scripts/validate_taxonomy.py
python3 scripts/validate_progress.py
python3 -m unittest discover -s tests -v
```

结果：

- taxonomy validator：**PASS**；13/27/110 taxonomy、100 comprehensive、48 case、13/13 capability coverage 保持通过；
- progress validator：**PASS**；contract、repeat、shuffle、duplicate/reference rejection、null semantics 全通过；
- unittest：**PASS**；11 个 replay/domain tests 全通过。

## 8. Explicit boundaries

本 PR 没有实现：

```text
mastery / mastered
review_due / review_interval
forgetting curve
SM-2 / FSRS / 1/3/7/15 scheduling
Adaptive Planner
Rolling 7-Day Plan
30-Day Plan 实例化
AI 自动评分或 AI 生成 accuracy/mastery
assessment-based recent_score
数据库 / SQLite / API / 登录 / UI
```

`recent_score` 只有在未来冻结 assessment/session contract 后才能加入 replay；本阶段不从最近 N 道题猜分数。

## 9. Gate

```text
PASS
```

理由：事实 schema、event ID 唯一性、timezone timestamp、topic/capability 引用、score evidence、multi-topic / multi-capability 语义、null semantics、duplicate rejection 和 deterministic replay 均已有可执行验证；基础 state 可以从 events 完全重建。

因此本模型足够稳定，可以进入下一阶段 **Mastery / Review Scheduling v0.1** 的独立设计。该结论不表示本 PR 已实现任何 mastery 或 scheduling policy。
