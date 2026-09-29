---
content_version: offline-learning-unit/v0.1
path_id: system-architect-checkin
path_version: 1.0.0
item_id: checkin-084
order: 84
title: "UML 动态图与 4+1 视图"
source:
  date: "2026-09-06"
  file: "2026年09月/2026-09-06 面向对象分析.md"
  prompt_sha256: ce3b254c824863da8bea3f3a48682a5eccf97d81c722e1be287faf415499f455
mapping:
  status: split
  confidence: high
  topic_ids:
    - SOFTWARE.MODELING.UML
    - ARCH.FOUNDATION.VIEWS
generation:
  mode: offline-agent
  status: draft
review_status: unreviewed
---

# UML 动态图与 4+1 视图

## 今天学会什么
- 区分活动、顺序、通信和状态图的核心关注点
- 识别顺序图消息与组合片段
- 将 UML 图放入 4+1 架构视图

## 先建立直觉

动态图描述系统运行时如何工作：可以看业务活动流、对象按时间交互，或单个对象的状态变化。4+1 视图则把这些图按架构沟通目的分配。

## 核心知识

### 动态 UML 图

活动图描述流程控制与并发；顺序图以时间顺序展示对象消息，有同步/返回/异步消息及 alt、opt、loop、break、par、critical 等组合片段；通信图关注对象链接而非时间排序；状态图描述对象状态及事件触发转换。

### 4+1

逻辑视图看功能与对象结构；进程视图看并发、运行时交互和性能；开发视图看模块组织；部署视图看物理拓扑；场景/用例视图表达用户需求并验证其他视图。

## 一张脑图式结构

```text
动态图：活动流 / 消息时间线 / 对象连接 / 状态转换
4+1：场景 + 逻辑 + 进程 + 开发 + 部署
```

## 易混点 / 对比

活动图看活动与控制流；顺序图看对象消息的时间顺序；通信图看对象连接组织；状态图看单个对象生命周期中的状态变化。

## 架构师视角

架构师要用多视图说明结构、运行和部署，并用场景检验不同视图是否共同满足需求。一个图不能同时承担所有沟通目的。

## 软考关注

- 本仓库没有为该学习日细目关联章节级大纲或教材证据。
- Golden Set 主题级索引：`gs-comp-2024-h2-q29`, `gs-comp-2025-h1-q16`, `gs-comp-2025-h1-q17`。只表示相应 Topic 有索引样本，不证明本日子主题命中或考试频率。
- 不作“高频 / 必考 / 常考”结论。

## 记忆锚点

- 活动图看活动控制流与并发
- 顺序图看时间次序，通信图看链接组织
- 状态图看对象状态与转换事件
- 4+1 的场景视图连接用户需求与其他视图

## 来源与证据

- `data/learning-paths/system-architect-checkin-v1.json`：`checkin-084` 的来源身份、知识点索引与 mapping。
- 用户提供的打卡归档：`2026年09月/2026-09-06 面向对象分析.md`；本 Prompt 区块 SHA-256 记录于 frontmatter，原文未复制。
- `docs/learning-path/SYSTEM_ARCHITECT_CHECKIN_MAPPING_AUDIT.md`：来源映射审计；mapping 不改变 Path Item identity。
- `data/golden-set/`：关联样题索引 `gs-comp-2024-h2-q29`, `gs-comp-2025-h1-q16`, `gs-comp-2025-h1-q17`；不含题干、答案或解析。
