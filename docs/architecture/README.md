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
Review Item / Evidence v0.1  ✅
   ↓
Mastery / Review             ✅ Phase 4 Gate PASS（P4.1～P4.9）
   ↓
Adaptive Planner             ⏳ Phase 5（Issue #13；contract / Gate 待完成）
   ↓
30-Day Plan                  ⏳
   ↓
Cockpit UI                   ⏳
```

当前仓库的依赖关系是：先保留来源与版权边界，再稳定元数据和归一化模型；学习事实只能以 append-only event 保存；ProgressState 是由事件和版本化 replay rule 计算出的结果，而不是人工维护的事实源。

## 当前阶段

Phase 2 已完成 Golden Set 扩量：100 道综合题、48 道案例子问题；taxonomy coverage 为 L1 13/13、L2 25/27、L3 75/110，Case Capability 为 13/13。

Phase 3 已完成 Progress Model v0.1 的基础契约与 deterministic replay；Phase 4 P4.1/P4.2 已冻结独立的 Review Item / Review Evidence v0.1：

- `comprehensive_attempt` 保存正确 / 错误事实、来源引用、topic 和可选错误归因；
- `case_attempt` 保存可选总分证据及 capability-level score evidence；
- `study_session` 保存可测量的时长事实；
- replay 生成 global、topic、case/capability score、error、coverage 和 study 基础聚合；
- 事件是 source of truth，状态可以删除后重新构建；
- Review Context Event 显式关联 Progress Attempt 与 `initial_learning` / `review`；没有 context 不猜测 Review Evidence；
- Review Evidence 只保存 policy-independent facts；不实现 mastery、review_due 或 scheduling。

详见 [`docs/review/REVIEW_MODEL_V01.md`](../review/REVIEW_MODEL_V01.md) 与 [`docs/review/REVIEW_EVIDENCE_V01.md`](../review/REVIEW_EVIDENCE_V01.md)。

## Phase 4（Gate PASS）

Phase 4 的规则设计部分（P4.3 / P4.4）已冻结 v0.1 contract，P4.5 已将 Review Evidence 与 policy kernel 串接为可重建的 `MasteryReviewState v0.1`。

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

Phase 4 P4.1～P4.9 已完成并通过 Gate；36 个冻结的 synthetic replay fixtures、validator、边界测试与正式 validation report 见 [`docs/PHASE4_VALIDATION_REPORT.md`](../PHASE4_VALIDATION_REPORT.md)。Phase 5（Issue #13）当前只完成 P5.1 Planner 输入契约与 P5.2 User Configuration v0.1；输入冻结不代表 Planner 已实现或 Phase 5 Gate 通过。P5.3+、Rolling 7-Day Plan、30-Day Plan 实例化、数据库、API 与 UI 仍未实现。契约见 [`docs/planner/README.md`](../planner/README.md)。

`progress-state/v0.1` 的字段与语义不因 Phase 4 改变：mastery / review 是**独立派生层**，不是 ProgressState 的新字段。

## 边界

```text
Progress Model
   != Review Model / Evidence
   != Mastery Algorithm
   != Review Scheduling
   != Adaptive Planner
```

Phase 4 的 mastery / review policy 已冻结为确定性规则，但**不是**自适应复习算法：没有 SM-2、FSRS、forgetting curve、难度参数或 AI 判断；replay 仍必须显式接受 `as_of` 与时区。Phase 4 没有实现 30-Day Plan 实例化、数据库、API 或 UI。`recent_score` 也暂不计算，因为本阶段没有冻结 assessment contract；后续只能从明确的 assessment/session 事实定义它。

详细契约和验证结果见 [`docs/PROGRESS_MODEL_V01_VALIDATION.md`](../PROGRESS_MODEL_V01_VALIDATION.md)、[`docs/review/README.md`](../review/README.md)、[`docs/review/REVIEW_MODEL_V01.md`](../review/REVIEW_MODEL_V01.md) 与 [`data/progress/schema.json`](../../data/progress/schema.json)。

## Cockpit UI（仅规划）

`Cockpit UI` 的**规划**已沉淀为文档，位于 [`docs/ui/`](../ui/README.md)：

- [`COCKPIT_UI_BLUEPRINT.md`](../ui/COCKPIT_UI_BLUEPRINT.md)：Product Goal、UX Principles、IA、Dashboard 卡片数据语义；
- [`PAGE_MAP.md`](../ui/PAGE_MAP.md)：路由矩阵与实现 Gate；
- [`DOMAIN_TO_UI_MAPPING.md`](../ui/DOMAIN_TO_UI_MAPPING.md)：UI 指标 → domain 字段映射与 null / unavailable 语义；
- [`READ_MODEL_CONTRACT.md`](../ui/READ_MODEL_CONTRACT.md)：UI Read Model consumer contract；
- [`REVIEW_MASTERY_UX.md`](../ui/REVIEW_MASTERY_UX.md)、[`TODAY_PLANNER_UX.md`](../ui/TODAY_PLANNER_UX.md)；
- [`DESIGN_DIRECTION.md`](../ui/DESIGN_DIRECTION.md)、[`COMPONENT_MAP.md`](../ui/COMPONENT_MAP.md)、[`RESPONSIVE_ACCESSIBILITY.md`](../ui/RESPONSIVE_ACCESSIBILITY.md)。

边界说明：

- 这些文档只是**规划**，不改变上图的阶段顺序，也不占用任何 Phase 编号；
- 仍然**没有**前端工程、API、数据库、账号系统或写路径；
- UI 不得自行推算 mastery / review_due / plan completion；Today 与 Review 的呈现分别依赖 Adaptive Planner 与 `MasteryReviewState` replay；
- UI Read Model 可派生、可缓存、可重建，但**不是**事实源。

### Review / Mastery 的当前状态

Phase 4 当前已冻结 P4.1/P4.2 的 Review Model / Evidence、P4.3/P4.4 的 Mastery/Scheduling policy，并已实现 P4.5 replay：

```text
已冻结：Review Item / Review Evidence（P4.1 / P4.2）
        review-model/v0.1 + review-event/v0.1 + review-evidence/v0.1
        stable identity、explicit context、policy-neutral facts
        Mastery State Machine / Review Scheduling Policy（P4.3 / P4.4）

已实现：`MasteryReviewState v0.1` replay 与显式 `as_of` / timezone API（P4.5）
已完成：fixture expected 值与 matrix validation（P4.6 / P4.7）
        Documentation sync / validation report（P4.8 / P4.9，Phase 4 Gate PASS）
未实现：Adaptive Planner
```

因此：

```text
规则/证据契约冻结 + P4.5 replay = 可消费的 MasteryReviewState domain output
UI 仍只能消费 replay 输出；不得绕过 replay 直接调用 policy kernel
```
