# ruankao-cockpit

> 软考高级 · 系统架构设计师 30 天自适应备考工作台

## 项目定位

`ruankao-cockpit` 的目标不是重新生产一套软考教材，而是把分散的公开内容组织成可追踪、可解释、可自适应的备考控制面：

```text
公开内容源
→ 统一知识索引
→ Immutable Learning Facts
→ Deterministic Progress Replay
→ Mastery / Review Policy
→ Adaptive Plan
→ Cockpit
```

项目优先建设内容元数据、知识归一化、学习进度与计划规则；正文内容默认通过来源引用和索引接入，而不是复制第三方资料。

## 这不是

- 软考资料合集
- PDF 下载站
- 真题镜像站
- 范文合集

## 项目要解决的问题

- 内容来源分散，难以统一检索和引用
- 不同来源的 taxonomy 不统一，题目难以稳定归因
- 学习状态难以量化，完成不等于掌握
- 固定计划不能根据真实表现、复习欠债和可用时间调整
- 综合、案例、论文缺乏统一的学习控制面

## 当前状态

```text
Research Audit        ✅
Repository Bootstrap  ✅
Taxonomy v0.1         ✅
Golden Set Expansion  ✅
Progress Model v0.1   ✅
Progress Replay       ✅
Mastery / Review Policy ✅ 规则冻结
Mastery / Review Replay ⏳
Adaptive Planner      ⏳
30-Day Plan           ⏳
Cockpit UI            ⏳
```

当前仓库已完成 Taxonomy v0.1、Case Capability v0.1、Golden Set 数据契约和 Phase 2 扩量验证（100 道综合题、48 道案例子问题），并已建立 Progress Event v0.1、基础 ProgressState 和 deterministic replay。ProgressState 始终由事件重建。

Phase 4 的规则层已完成 P4.3 / P4.4 的 contract 冻结：Mastery State Machine v0.1 与 Review Scheduling Policy v0.1 已给出可测试的确定性规则（状态互斥、transition table、interval ladder、时间语义、`due_count`），并附带 policy-level 单元测试。它们是**确定性 policy**，不是自适应复习算法、不是 SM-2 / FSRS、也不是 Planner。Review Model / Review Evidence（P4.1 / P4.2）、`MasteryReviewState` replay（P4.5）、fixture / validation report 与 Adaptive Planner、30 天计划实例化、UI 仍未实现。

## 文档入口

- [内容源审计](docs/CONTENT_SOURCE_AUDIT.md)
- [30 天课程草案](docs/30_DAY_CURRICULUM_DRAFT.md)
- [当前架构方向](docs/architecture/README.md)
- [Taxonomy 边界](taxonomy/README.md)
- [Golden Set 策略](data/golden-set/README.md)
- [Phase 2 Golden Set 扩量验证报告](docs/GOLDEN_SET_EXPANSION_VALIDATION.md)
- [Progress Model v0.1 / Replay 边界](engine/progress/README.md)
- [Progress Model v0.1 验证报告](docs/PROGRESS_MODEL_V01_VALIDATION.md)
- [Mastery / Review Policy v0.1 文档索引](docs/review/README.md)
- [Mastery State Machine v0.1](docs/review/MASTERY_POLICY_V01.md)
- [Review Scheduling Policy v0.1](docs/review/REVIEW_SCHEDULING_POLICY_V01.md)
- [Policy Test Matrix v0.1](docs/review/POLICY_TEST_MATRIX_V01.md)
- [Policy Symbol Freeze v0.1](docs/review/POLICY_SYMBOL_FREEZE_V01.md)
- [Phase 4 测试矩阵设计稿](docs/PHASE4_TEST_MATRIX.md)
- [Progress / Adaptive Engine 边界](engine/rules/README.md)
- [Cockpit UI / UX Blueprint（规划，未实现）](docs/ui/README.md)

## 开发边界

本阶段不初始化前端技术栈、数据库、API 或 Planner；当前实现标准库 Progress Event / Replay 基础，以及 Phase 4 冻结的 Mastery / Review policy kernel。详细的版权、数据边界、测试优先级和领域约束见 [AGENTS.md](AGENTS.md)。

Cockpit UI 目前只有**规划文档**（[`docs/ui/`](docs/ui/README.md)）：信息架构、页面地图、Domain → UI 映射、UI Read Model consumer contract、Design Direction 与组件边界已冻结为可审计文档，但仍**没有**前端工程、API、数据库或账号系统。UI 的实现 Gate 依赖 `MasteryReviewState` replay 输出（P4.5）与 Adaptive Planner 的正式契约，详见 [`docs/ui/README.md`](docs/ui/README.md) 的 Gate 状态表。
