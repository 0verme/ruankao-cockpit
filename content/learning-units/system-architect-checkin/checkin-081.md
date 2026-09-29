---
content_version: offline-learning-unit/v0.1
path_id: system-architect-checkin
path_version: 1.0.0
item_id: checkin-081
order: 81
title: "面向对象分析：对象模型与基本概念"
source:
  date: "2026-09-03"
  file: "2026年09月/2026-09-03 面向对象分析.md"
  prompt_sha256: 7e87cd2dc78e968246fac0f40156459b5ac6714cf0bc8f33b4d4a6b7cfad0bfa
mapping:
  status: partial
  confidence: high
  topic_ids:
    - SOFTWARE.ENGINEERING.ANALYSIS_DESIGN
generation:
  mode: offline-agent
  status: draft
review_status: unreviewed
---

# 面向对象分析：对象模型与基本概念

## 今天学会什么
- 说明 OOA 如何从问题域对象组织需求模型
- 区分类、对象、属性、方法、消息和接口
- 识别用例模型与分析模型的组成

## 先建立直觉

面向对象分析以问题域中的事物、属性、行为和关系描述系统应该做什么，模型不直接规定技术实现。

## 核心知识

### 对象和类

对象有标识、状态和行为；类是对具有相同属性和行为对象的抽象。属性表达状态，方法表达行为；消息让对象协作，接口声明对外提供的操作。

### 基本机制

封装把数据和操作组织在一起并通过接口交互；继承基于已有类扩展；多态使同一操作在不同对象上有不同表现。重写改变继承方法，重载使用不同参数列表提供同名方法。

### 模型

OO 模型包含用例模型和分析模型；分析模型分静态与动态。

## 一张脑图式结构

```text
问题域 → 对象/类 → 属性与方法
├─ 静态：结构与关系
├─ 动态：对象协作
└─ 用例：外部参与者与系统功能
```

## 架构师视角

先把业务概念表达成独立于技术的模型，再讨论实现结构；封装、接口和对象关系帮助控制变化边界，但模型仍需由真实需求校验。

## 软考关注

- 本仓库没有为该学习日细目关联章节级大纲或教材证据。
- Golden Set 主题级索引：`gs-comp-2025-h1-q06`。只表示相应 Topic 有索引样本，不证明本日子主题命中或考试频率。
- 不作“高频 / 必考 / 常考”结论。

## 记忆锚点

- 对象有标识、状态、行为
- 类是对象的抽象模板
- 封装/继承/多态是基本机制
- 重写改行为，重载改参数列表

## 来源与证据

- `data/learning-paths/system-architect-checkin-v1.json`：`checkin-081` 的来源身份、知识点索引与 mapping。
- 用户提供的打卡归档：`2026年09月/2026-09-03 面向对象分析.md`；本 Prompt 区块 SHA-256 记录于 frontmatter，原文未复制。
- `docs/learning-path/SYSTEM_ARCHITECT_CHECKIN_MAPPING_AUDIT.md`：来源映射审计；mapping 不改变 Path Item identity。
- `data/golden-set/`：关联样题索引 `gs-comp-2025-h1-q06`；不含题干、答案或解析。
