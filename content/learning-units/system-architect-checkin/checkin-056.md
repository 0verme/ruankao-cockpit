---
content_version: offline-learning-unit/v0.1
path_id: system-architect-checkin
path_version: 1.0.0
item_id: checkin-056
order: 56
title: "DDD 战略设计：子域与上下文映射"
source:
  date: "2026-08-05"
  file: "2026年08月/2026-08-05 领域驱动设计-战略设计.md"
  prompt_sha256: dd73add37617700269f3bb02c9607821aad8fd47689ef6bf4b87867fd9ee274b
mapping:
  status: unmapped
  confidence: low
  topic_ids: []
generation:
  mode: offline-agent
  status: draft
review_status: source_gap
---

# DDD 战略设计：子域与上下文映射

## 今天学会什么
- 说明战略设计把问题域拆成可管理部分
- 区分来源列出的上下文映射关系
- 识别子域分类与事件风暴细节仍待来源补齐

## 先建立直觉

战略设计先划定领域边界，让团队在各自上下文中使用含义明确的语言，再确定上下文之间如何协作或隔离。它关注的是边界与关系，而不是实体字段。

## 核心知识

### 领域与上下文

来源指出可将问题域拆成子域和限界上下文，以便独立分析、设计、开发和测试；每个上下文有自己的通用语言，避免概念和规则理解偏差。核心域、支撑域、通用域只列名称，没有定义。

### 上下文映射

共享内核共享模型/代码；客户—供应商表示下游依赖上游；伙伴关系要求团队紧密协调；遵奉者完全采用上游模型和接口；防腐层在边界转换模型；开放主机服务提供标准协议接口；发布语言用于上下文间信息交换，常与开放主机服务配合。

### SOURCE_GAP

事件风暴概念和工作过程未提供；不同子域分类也只有标题。

**SOURCE_GAP：核心/支撑/通用子域的定义及事件风暴流程在来源中没有正文。**

## 一张脑图式结构

```text
问题域 → 子域 / 限界上下文
├─ 各上下文维护边界内通用语言
└─ 上下文关系：共享内核 / 客户供应商 / 伙伴 / 遵奉者
   └─ 隔离或开放：防腐层 / 开放主机服务 / 发布语言
```

## 架构师视角

上下文边界决定模型和团队间的依赖方式。选择伙伴协作还是防腐层隔离，会改变变更协调与模型转换责任；先识别上游/下游关系，再明确接口和语言，避免边界隐式耦合。

## 软考关注

- 本仓库没有为该学习日细目关联章节级大纲或教材证据。
- 本项 `UNMAPPED` 且无 topic_ids；未找到可关联的 Topic 样题证据，不猜测考试归属。
- 不作“高频 / 必考 / 常考”结论。

## 记忆锚点

- 战略设计拆问题域
- 每个上下文有边界内的通用语言
- 防腐层隔离并转换上游模型
- 共享内核/伙伴/供应商等关系不能混淆
- 事件风暴流程为 SOURCE_GAP

## 来源与证据

- `data/learning-paths/system-architect-checkin-v1.json`：`checkin-056` 的来源身份、知识点索引与 mapping。
- 用户提供的打卡归档：`2026年08月/2026-08-05 领域驱动设计-战略设计.md`；本 Prompt 区块 SHA-256 记录于 frontmatter，原文未复制。
- `docs/learning-path/SYSTEM_ARCHITECT_CHECKIN_MAPPING_AUDIT.md`：来源映射审计；mapping 不改变 Path Item identity。
