# Progress / Adaptive Engine Rules

本轮只定义未来 Progress / Adaptive Engine 的职责，不实现引擎、Planner、复杂算法或评分模型。

## 未来输入

规则可能读取：

```text
recent_score
topic_accuracy
error_count
mastery
study_minutes
completion_rate
case_score
essay_progress
review_due
streak
```

这些输入应来自可追踪的作答、学习会话、案例记录、论文进度和复习状态，而不是无法复盘的主观判断。

## 计划形态

```text
30-Day Backbone
+
Rolling 7-Day Plan
+
Daily Adaptive Tasks
```

- **30-Day Backbone**：保持阶段、关键里程碑和不可协商的主梁。
- **Rolling 7-Day Plan**：根据容量、复习欠债和弱项调整近期配额。
- **Daily Adaptive Tasks**：把当天结果写回状态，并生成下一步任务。

## 规则原则

规则优先 deterministic，输入、阈值、输出和版本都应可记录、可测试、可复盘。AI 可以辅助分类、解释、论文反馈和错误总结，但不应直接凭感觉生成事实型 score、accuracy、mastery 或 review_due。

后续实现前，先稳定 Domain / Progress Model 和共享数据契约。本目录当前不包含 Progress Engine、Adaptive Planner 或假的评分逻辑。
