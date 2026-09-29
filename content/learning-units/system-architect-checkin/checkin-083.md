---
content_version: offline-learning-unit/v0.1
path_id: system-architect-checkin
path_version: 1.0.0
item_id: checkin-083
order: 83
title: "UML 静态图：从结构到部署"
source:
  date: "2026-09-05"
  file: "2026年09月/2026-09-05 面向对象分析.md"
  prompt_sha256: b12a37773940ba97a20cd44b522502d524c93660f549a7f3d457e147ca9540a1
mapping:
  status: merge
  confidence: high
  topic_ids:
    - SOFTWARE.MODELING.UML
generation:
  mode: offline-agent
  status: draft
review_status: unreviewed
---

# UML 静态图：从结构到部署

## 今天学会什么
- 按静态图用途区分用例、类、对象图
- 区分构件、部署、包与组合结构图所表达的结构
- 为 UML 图选择正确的描述对象

## 先建立直觉

静态图回答系统由什么组成、元素如何组织，以及软件怎样映射到物理环境。不同图的抽象层次不同，不能只凭“都是结构图”互换。

## 核心知识

### 功能和逻辑结构

用例图从用户视角表示参与者与功能；类图表示类、属性、方法和关系；对象图是某一时刻对象及关系的实例快照。

### 实现和运行结构

构件图表示物理软件模块及依赖；部署图表示软件构件映射到硬件/网络；包图组织模型并展示包依赖；组合结构图进一步描述复杂类或构件内部组成与接口。

## 一张脑图式结构

```text
需求：用例图
逻辑：类图 → 对象图（具体时刻快照）
实现：包图 / 构件图 / 组合结构图
物理：部署图
```

## 易混点 / 对比

类图表达抽象类型结构，对象图呈现具体实例状态；构件图关注软件模块，部署图关注物理节点及映射。

## 架构师视角

用图时先明确沟通问题：讨论业务功能、类结构、代码模块还是物理拓扑。选择正确视图能让决策在合适抽象层上被审阅。

## 软考关注

- 本仓库没有为该学习日细目关联章节级大纲或教材证据。
- Golden Set 主题级索引：`gs-comp-2024-h2-q29`, `gs-comp-2025-h1-q24`, `gs-comp-2025-h1-q58`。只表示相应 Topic 有索引样本，不证明本日子主题命中或考试频率。
- 不作“高频 / 必考 / 常考”结论。

## 记忆锚点

- 用例图看用户功能
- 类图抽象、对象图实例快照
- 构件图看软件模块，部署图看物理映射
- 包图组织模型，组合结构图看内部构造

## 来源与证据

- `data/learning-paths/system-architect-checkin-v1.json`：`checkin-083` 的来源身份、知识点索引与 mapping。
- 用户提供的打卡归档：`2026年09月/2026-09-05 面向对象分析.md`；本 Prompt 区块 SHA-256 记录于 frontmatter，原文未复制。
- `docs/learning-path/SYSTEM_ARCHITECT_CHECKIN_MAPPING_AUDIT.md`：来源映射审计；mapping 不改变 Path Item identity。
- `data/golden-set/`：关联样题索引 `gs-comp-2024-h2-q29`, `gs-comp-2025-h1-q24`, `gs-comp-2025-h1-q58`；不含题干、答案或解析。
