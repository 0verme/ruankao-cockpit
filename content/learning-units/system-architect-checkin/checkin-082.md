---
content_version: offline-learning-unit/v0.1
path_id: system-architect-checkin
path_version: 1.0.0
item_id: checkin-082
order: 82
title: "用例模型与分析类关系"
source:
  date: "2026-09-04"
  file: "2026年09月/2026-09-04 面向对象分析.md"
  prompt_sha256: b4c2c4ffa76652e81b0954dd3cd71e1ff9a56725cefd780107d7ff5c8afe10ea
mapping:
  status: split
  confidence: high
  topic_ids:
    - SOFTWARE.ENGINEERING.ANALYSIS_DESIGN
    - SOFTWARE.MODELING.UML
generation:
  mode: offline-agent
  status: draft
review_status: unreviewed
---

# 用例模型与分析类关系

## 今天学会什么
- 说明用例模型从用户视角表达系统功能
- 区分包含、扩展、泛化及参与者泛化
- 辨认关联、依赖、泛化、实现、聚合和组合

## 先建立直觉

用例描述外部参与者希望系统提供什么；分析模型进一步说明系统结构以及对象如何协作。两者连接需求表达与后续设计。

## 核心知识

### 用例模型

用例图由参与者、用例和关联组成，另有用例规约。它用于划定边界、捕获功能需求、沟通共识并驱动后续分析/测试。包含提取共享行为；扩展在条件下增加可选行为；泛化抽取共同结构。

### 分析模型

静态模型描述类、属性、方法和类关系；动态模型描述对象协作。关系包括关联、临时使用依赖、一般/特殊泛化、接口实现、可独立部分的聚合、生命周期依附更强的组合。来源给出关系强弱顺序：实现/泛化 > 组合 > 聚合 > 关联 > 依赖。

## 一张脑图式结构

```text
需求视角：参与者 → 用例图/规约 → 系统边界与功能
分析视角：静态类关系 + 动态对象协作
```

## 易混点 / 对比

用例的包含关系复用公共行为；扩展是条件触发的可选行为；泛化抽取共同结构。聚合中的部分可独立存在，组合中的部分不能独立存在（按来源描述）。

## 架构师视角

用例边界帮助架构师识别系统责任；分析类关系说明结构约束。把用户目标与内部对象模型分开表达，可避免用实现细节替代业务需求。

## 软考关注

- 本仓库没有为该学习日细目关联章节级大纲或教材证据。
- Golden Set 主题级索引：`gs-comp-2024-h2-q29`, `gs-comp-2025-h1-q06`, `gs-comp-2025-h1-q24`。只表示相应 Topic 有索引样本，不证明本日子主题命中或考试频率。
- 不作“高频 / 必考 / 常考”结论。

## 记忆锚点

- 用例图：参与者、用例、关联
- 包含共享，扩展可选，泛化抽象共性
- 静态模型看结构，动态模型看协作
- 聚合与组合的部分生命周期边界不同

## 来源与证据

- `data/learning-paths/system-architect-checkin-v1.json`：`checkin-082` 的来源身份、知识点索引与 mapping。
- 用户提供的打卡归档：`2026年09月/2026-09-04 面向对象分析.md`；本 Prompt 区块 SHA-256 记录于 frontmatter，原文未复制。
- `docs/learning-path/SYSTEM_ARCHITECT_CHECKIN_MAPPING_AUDIT.md`：来源映射审计；mapping 不改变 Path Item identity。
- `data/golden-set/`：关联样题索引 `gs-comp-2024-h2-q29`, `gs-comp-2025-h1-q06`, `gs-comp-2025-h1-q24`；不含题干、答案或解析。
