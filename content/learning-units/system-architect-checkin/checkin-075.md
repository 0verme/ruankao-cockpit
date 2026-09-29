---
content_version: offline-learning-unit/v0.1
path_id: system-architect-checkin
path_version: 1.0.0
item_id: checkin-075
order: 75
title: "湖仓一体：存储与计算层主题"
source:
  date: "2026-08-25"
  file: "2026年08月/2026-08-25 大数据架构-湖仓一体架构.md"
  prompt_sha256: 79cf0297a300aa8e57c56ffc10ca04f7090dece9762b6f210ebfc61c0936156c
mapping:
  status: unmapped
  confidence: low
  topic_ids: []
generation:
  mode: offline-agent
  status: draft
review_status: source_gap
---

# 湖仓一体：存储与计算层主题

## 今天学会什么
- 识别数据湖、数据仓库与湖仓一体三个主题
- 列出来源明确的湖仓一体层次
- 明确核心思想及优缺点缺少支持

## 先建立直觉

本日把数据湖、数据仓库和湖仓一体放在同一学习单元中，但两种基础形态的定义与比较没有正文；湖仓一体只给出层次清单的一部分。

## 核心知识

### 来源列出的结构

湖仓一体层次包括数据源、数据接入、数据存储、多引擎计算、数据服务。数据存储提及统一存储、开放表格式与事务、元数据管理；计算层列离线、实时、交互/即席查询和模型训练。

### SOURCE_GAP

数据湖和数据仓库的核心思想、优缺点及湖仓一体如何整合二者，均无正文依据。

**SOURCE_GAP：湖、仓概念与湖仓一体原则/优势没有解释。**

## 一张脑图式结构

```text
数据源 → 接入 → 统一存储/表格式/元数据
→ 多引擎计算（离线/实时/查询/训练） → 数据服务
```

## 架构师视角

架构师需要评估存储格式、事务、元数据和多引擎共享问题，但来源未说明其一致性和治理机制。保留层次索引，不将“湖仓一体”当作自动兼具所有优势的保证。

## 软考关注

- 本仓库没有为该学习日细目关联章节级大纲或教材证据。
- 本项 `UNMAPPED` 且无 topic_ids；未找到可关联的 Topic 样题证据，不猜测考试归属。
- 不作“高频 / 必考 / 常考”结论。

## 记忆锚点

- 五层：数据源、接入、存储、计算、服务
- 存储关注统一存储、开放表格式/事务、元数据
- 计算层列多种引擎用途
- 湖与仓定义为 SOURCE_GAP

## 来源与证据

- `data/learning-paths/system-architect-checkin-v1.json`：`checkin-075` 的来源身份、知识点索引与 mapping。
- 用户提供的打卡归档：`2026年08月/2026-08-25 大数据架构-湖仓一体架构.md`；本 Prompt 区块 SHA-256 记录于 frontmatter，原文未复制。
- `docs/learning-path/SYSTEM_ARCHITECT_CHECKIN_MAPPING_AUDIT.md`：来源映射审计；mapping 不改变 Path Item identity。
