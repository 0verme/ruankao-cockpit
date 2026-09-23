# Progress / Adaptive Engine Rules

本目录记录规则层与当前 Progress Model 的边界。

```text
engine/rules/review_policy_v01.py    Phase 4（P4.3 / P4.4）冻结的 Mastery / Review policy kernel
tests/test_review_policy.py          对应的 policy-level 单元测试
```

这个 kernel 是**纯函数**：输入为 policy-eligible evidence、显式 `as_of` 和显式 IANA timezone，不读系统时间、不读机器时区、不含隐藏状态。`engine.review.replay.replay(...)`（P4.5）负责校验 Progress / Review contract、投影 Evidence、执行 outcome adapter 并组装 `MasteryReviewState v0.1`；kernel 本身仍不定义 Review Item / Review Evidence 契约。

## 当前可读取的 replay 输出

`engine/progress/replay.py` 从 `progress-event/v0.1` 事件生成 `progress-state/v0.1`，当前已经定义并可完全重建的输入包括：

```text
global.accuracy
topics[*].accuracy
capabilities[*].score_ratio
errors.error_count
errors.error_count_by_cause
errors.error_cause_mix
coverage.l1 / coverage.l2 / coverage.l3
case.score_ratio
study.study_minutes
```

其中：

- `topic accuracy` 只来自有 `correct` 事实的综合题；
- capability 使用实际 `score_earned / score_possible` evidence 加权，只有证据充分时 `score_ratio` 非空；
- `error_cause_mix` 的 denominator 是已分类错误，另有 `unclassified_error_count`；
- coverage 的分母明确为 taxonomy 的 L1/L2/L3 总节点数，L3 引用会闭包覆盖父级；
- `study_minutes` 只累加会话时长，不表示学习质量、专注度或效率。

当前没有把 `recent_score` 写成正式 replay 输出：它需要先有明确的 assessment contract（assessment_id、完成时间、总分证据）。`MasteryReviewState` 是独立派生层，不会把 mastery / due 字段加入此处的 `ProgressState`。

## Phase 4 v0.1 frozen policies

```text
mastery-policy/spaced-consecutive/v0.1
review-policy/simple-ladder/v0.1
```

两条正交轴：

```text
Mastery State                  new | learning | mastered
Review Scheduling Projection   not_scheduled | scheduled | due | overdue
```

冻结要点：

- `due` / `overdue` 是时间投影，不是 mastery 状态；`mastered` 与 `due` 可以同时成立；
- mastery 由 item 自身的“跨天连续成功数”决定（阈值 3），不读 `topic_accuracy`；
- interval ladder 为 `1 / 3 / 7 / 15` 天，失败重置为 1 天，mastered 保留 15 天 maintenance；
- 到期时间锚定本地日历日 00:00，时区必须显式传入，禁止 `datetime.now()`；
- `as_of` 早于 evidence 时直接拒绝（`future_evidence`），不静默丢弃或泄漏未来事实；
- `due_count` 是 item 级到期数量，不是事件数。

完整规则、transition table 与 rejected alternatives 见 [`docs/review/README.md`](../../docs/review/README.md)；依赖 P4.1 / P4.2 的假设见 [`ASSUMPTIONS_PENDING_P4_1_P4_2.md`](../../docs/review/ASSUMPTIONS_PENDING_P4_1_P4_2.md)。

本目录**不**包含：planner、自适应排序、SM-2、FSRS、forgetting curve、AI 判断、UI、存储；P4.5 replay 位于 `engine/review/`。

## Review Evidence boundary

`Review Model / Evidence v0.1` 已在独立 contract 中冻结。规则层可以读取由 Progress Events 加显式 `review_context` 投影出的 policy-neutral evidence，但本目录不在 Evidence 层决定 success、failure、mastery 或 review_due。

详见 [`docs/review/REVIEW_EVIDENCE_V01.md`](../../docs/review/REVIEW_EVIDENCE_V01.md)。

## Future inputs

未来规则层可以读取的输入（Mastery / Review v0.1 policy 与 P4.5 replay 已实现；本目录仍只描述 policy kernel 边界）：

```text
recent_score                 Future: assessment contract 未冻结
review_evidence              Current: Review Evidence v0.1；由 P4.5 adapter 接入 policy，不回写 evidence
mastery                      规则已冻结（P4.3）：mastery-policy/spaced-consecutive/v0.1
review_due                   规则已冻结（P4.4）：review-policy/simple-ladder/v0.1
review_interval              规则已冻结（P4.4）；由 P4.5 replay 投影
completion_rate              Future: task execution contract 未实现
capacity_actual              Future
essay_progress               Future
streak                       Future
```

未来规则也可以读取当前 replay 输出，但必须记录：输入事件集合、event schema version、replay rule version、阈值和输出变更。AI 可以辅助分类、解释、论文反馈和错误总结，但不能凭感觉制造 accuracy、score、mastery 或 review_due。

## 计划形态（Future）

```text
30-Day Backbone
+
Rolling 7-Day Plan
+
Daily Adaptive Tasks
```

- **30-Day Backbone**：未来保持阶段、关键里程碑和不可协商的主梁。
- **Rolling 7-Day Plan**：未来根据容量、复习欠债和弱项调整近期配额。
- **Daily Adaptive Tasks**：未来把当天结果写回并生成下一步任务。

本阶段不实现上述 Planner、数据库、API 或 UI。Mastery / Review deterministic replay 已由 `engine/review/` 实现并通过 Phase 4 Gate；此处仍只说明 policy kernel 的职责边界。详见 [`docs/PHASE4_VALIDATION_REPORT.md`](../../docs/PHASE4_VALIDATION_REPORT.md)。
