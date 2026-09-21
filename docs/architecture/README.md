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
Mastery / Review Policy v0.1 ✅ 规则冻结（P4.3 / P4.4）
   ↓
Mastery / Review Replay      ⏳ (P4.5)
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

## Phase 4（进行中）

Phase 4 的规则设计部分（P4.3 / P4.4）已冻结 v0.1 contract，但还没有实现 replay。

冻结的分层是：

```text
Axis 1  Mastery State                  new / learning / mastered
Axis 2  Review Scheduling Projection   not_scheduled / scheduled / due / overdue
```

- `due` / `overdue` 是时间投影，不是与 `new` / `learning` / `mastered` 并列的知识状态；
- interval ladder 固定为 `1 / 3 / 7 / 15` 天，failure 重置为 1 天；
- 到期时间锚定**本地日历日 00:00**，时区必须显式传入，禁止 `datetime.now()`；
- `due_count` 是 item 级到期数量，不是事件数；
- policy 标识：`mastery-policy/spaced-consecutive/v0.1` + `review-policy/simple-ladder/v0.1`。

完整规则见 [`docs/review/README.md`](../review/README.md)。

本阶段仍然没有实现：

- Review Model / Review Evidence 契约（P4.1 / P4.2，独立窗口）；
- `MasteryReviewState v0.1` replay（P4.5）与 fixture / validation report（P4.6 / P4.7 / P4.9）；
- Adaptive Planner、Rolling 7-Day Plan、30-Day Plan 实例化、数据库、API、UI。

`progress-state/v0.1` 的字段与语义不因 Phase 4 改变：mastery / review 是**独立派生层**，
不是 ProgressState 的新字段。

## 边界

```text
Progress Model
   != Mastery Algorithm
   != Review Scheduling
   != Adaptive Planner
```

Phase 4 的 mastery / review policy 已冻结为确定性规则，但**不是**自适应复习算法：
没有 SM-2、FSRS、forgetting curve、难度参数或 AI 判断；replay 仍必须显式接受 `as_of` 与时区。
Phase 4 没有实现 30-Day Plan 实例化、数据库、API 或 UI。`recent_score` 也暂不计算，因为
本阶段没有冻结 assessment contract；后续只能从明确的 assessment/session 事实定义它。

详细契约和验证结果见 [`docs/PROGRESS_MODEL_V01_VALIDATION.md`](../PROGRESS_MODEL_V01_VALIDATION.md)、
[`docs/review/README.md`](../review/README.md) 与 [`data/progress/schema.json`](../../data/progress/schema.json)。
