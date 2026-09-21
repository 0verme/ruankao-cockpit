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
Mastery / Review      ⏳
Adaptive Planner      ⏳
30-Day Plan           ⏳
Cockpit UI            ⏳
```

当前仓库已完成 Taxonomy v0.1、Case Capability v0.1、Golden Set 数据契约和 Phase 2 扩量验证（100 道综合题、48 道案例子问题），并已建立 Progress Event v0.1、基础 ProgressState 和 deterministic replay。ProgressState 始终由事件重建；尚未实现 Mastery / Review Scheduling、Adaptive Planner、30 天计划实例化或 UI。

## 文档入口

- [内容源审计](docs/CONTENT_SOURCE_AUDIT.md)
- [30 天课程草案](docs/30_DAY_CURRICULUM_DRAFT.md)
- [当前架构方向](docs/architecture/README.md)
- [Taxonomy 边界](taxonomy/README.md)
- [Golden Set 策略](data/golden-set/README.md)
- [Phase 2 Golden Set 扩量验证报告](docs/GOLDEN_SET_EXPANSION_VALIDATION.md)
- [Progress Model v0.1 / Replay 边界](engine/progress/README.md)
- [Progress Model v0.1 验证报告](docs/PROGRESS_MODEL_V01_VALIDATION.md)
- [Progress / Adaptive Engine 边界](engine/rules/README.md)

## 开发边界

本阶段不初始化前端技术栈、数据库、API 或未来的 Mastery / Planner；当前只实现标准库 Progress Event / Replay 基础。详细的版权、数据边界、测试优先级和领域约束见 [AGENTS.md](AGENTS.md)。
