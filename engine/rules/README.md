# Progress / Adaptive Engine Rules

本目录记录未来规则层与当前 Progress Model 的边界。Phase 3 只实现事实事件和基础 deterministic replay，不实现规则决策。

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

当前没有把 `recent_score` 写成正式 replay 输出：它需要先有明确的 assessment contract（assessment_id、完成时间、总分证据）。

## Future inputs

未来 Mastery / Review / Adaptive Planner 可以在单独版本化后读取：

```text
recent_score                 Future: assessment contract 未冻结
mastery                      Future: 状态机 / 算法未实现
review_due                   Future: review policy 未实现
review_interval              Future
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

本阶段不实现上述 Planner、Mastery Algorithm、Review Scheduling、数据库、API 或 UI。
