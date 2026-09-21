# 当前架构方向

本阶段记录领域依赖顺序，不提前设计完整软件架构，也不初始化数据库、服务或 UI。

```text
Sources
   ↓
Source Metadata
   ↓
Normalized Taxonomy          ✅
   ↓
Golden Set                   ✅
   ↓
Immutable Progress Events    ✅
   ↓
Progress Model v0.1          ✅
   ↓
Deterministic Replay         ✅
   ↓
Mastery / Review Policy      ⏳
   ↓
Adaptive Planner             ⏳
   ↓
Cockpit UI                   ⏳
```

当前仓库的依赖关系是：先保留来源与版权边界，再稳定元数据和归一化模型；学习事实只能以 append-only event 保存；ProgressState 是由事件和版本化 replay rule 计算出的结果，而不是人工维护的事实源。

## 当前阶段

Phase 2 已完成 Golden Set 扩量：100 道综合题、48 道案例子问题；taxonomy coverage 为 L1 13/13、L2 25/27、L3 75/110，Case Capability 为 13/13。

Phase 3 已完成 Progress Model v0.1 的基础契约与 deterministic replay：

- `comprehensive_attempt` 保存正确 / 错误事实、来源引用、topic 和可选错误归因；
- `case_attempt` 保存可选总分证据及 capability-level score evidence；
- `study_session` 保存可测量的时长事实；
- replay 生成 global、topic、case/capability score、error、coverage 和 study 基础聚合；
- 事件是 source of truth，状态可以删除后重新构建。

## 边界

```text
Progress Model
   != Mastery Algorithm
   != Review Scheduling
   != Adaptive Planner
```

本阶段没有实现 mastery、mastered、review_due、SM-2、FSRS、1/3/7/15 scheduling、30-Day Plan 实例化、数据库、API 或 UI。`recent_score` 也暂不计算，因为本阶段没有冻结 assessment contract；后续只能从明确的 assessment/session 事实定义它。

详细契约和验证结果见 [`docs/PROGRESS_MODEL_V01_VALIDATION.md`](../PROGRESS_MODEL_V01_VALIDATION.md) 与 [`data/progress/schema.json`](../../data/progress/schema.json)。
