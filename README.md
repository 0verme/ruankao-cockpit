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
Review Model / Evidence v0.1 ✅
Mastery / Review Policy v0.1 ✅ 已实现（mastered = 达到当前 Review Policy 阈值）
Mastery / Review      ✅ Phase 4 Gate PASS（P4.1～P4.9）
Adaptive Planner      ⏳ Phase 5（Issue #13；Product Validation #16 的 Today MVP 已实现 review + new_learning；Rolling / 完整 policy 待完成）
30-Day Plan           ⏳
Cockpit UI            ⏳
```

当前仓库已完成 Taxonomy / Progress / Phase 4 Review replay，并有显式输入的 deterministic Today Planner MVP：消费 ProgressState 与 MasteryReviewState，使用 `PlannerOutput.days[0]` 生成 review + new_learning task、解释与 unmet demand。MVP 不重算 mastery / due，不消费 DRAFT 课程正文，不做 Rolling 7-Day 策略；完整 Phase 5 policy、30 天计划实例化、task execution 和 UI 仍未实现，Phase 5 Gate 未通过。`mastered` 仅表示达到当前 Review Policy 的 mastery 阈值，不是对真实掌握程度的绝对断言。

## 文档入口

- [内容源审计](docs/CONTENT_SOURCE_AUDIT.md)
- [30 天课程草案](docs/30_DAY_CURRICULUM_DRAFT.md)
- [当前架构方向](docs/architecture/README.md)
- [Taxonomy 边界](taxonomy/README.md)
- [Golden Set 策略](data/golden-set/README.md)
- [Phase 2 Golden Set 扩量验证报告](docs/GOLDEN_SET_EXPANSION_VALIDATION.md)
- [Progress Model v0.1 / Replay 边界](engine/progress/README.md)
- [Progress Model v0.1 验证报告](docs/PROGRESS_MODEL_V01_VALIDATION.md)
- [Phase 4 Gate 验证报告](docs/PHASE4_VALIDATION_REPORT.md)
- [Review Model v0.1](docs/review/REVIEW_MODEL_V01.md)
- [Review Evidence v0.1](docs/review/REVIEW_EVIDENCE_V01.md)
- [Mastery / Review Policy 文档索引](docs/review/README.md)
- [Progress / Adaptive Engine 边界](engine/rules/README.md)
- [Planner 输入、用户配置与输出契约（P5.1–P5.3）](docs/planner/README.md)
- [Today Planner MVP engine](engine/planner/README.md)
- [Cockpit UI / UX Blueprint（规划，未实现）](docs/ui/README.md)

## 开发边界

本阶段不实现 UI、数据库或 API。当前增加的 `engine/planner/` 是标准库 Today-only deterministic replay；它复用 Planner Input / Output 与 ExplainTrace、不改 Progress / Review state，不消费 `exam_date`，也不声明完整 P5.4/P5.5 或 Rolling policy 已冻结。详细的版权、数据边界、测试优先级和领域约束见 [AGENTS.md](AGENTS.md)。

Cockpit UI 目前只有**规划文档**（[`docs/ui/`](docs/ui/README.md)）：信息架构、页面地图、Domain → UI 映射、UI Read Model consumer contract、Design Direction 与组件边界已冻结为可审计文档，但仍**没有**前端工程、API、数据库或账号系统。P4.5 已解锁 Mastery / Review 的 domain consumer；Today Planner engine 已有首个可执行 MVP，前端实现仍按 [`docs/ui/README.md`](docs/ui/README.md) 的 Gate 状态表推进。
