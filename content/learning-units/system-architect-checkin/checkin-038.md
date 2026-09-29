---
content_version: offline-learning-unit/v0.1
path_id: system-architect-checkin
path_version: 1.0.0
item_id: checkin-038
order: 38
title: "知识图谱：构建、查询与存储"
source:
  date: "2026-07-15"
  file: "2026年07月/2026-07-15 知识图谱.md"
  prompt_sha256: 2b435a9cb9a13f719a3767eedbb3fbd2ff6cd9e0d63155abccf80d24117daff3
mapping:
  status: split
  confidence: high
  topic_ids:
    - DATA.BIGDATA.KNOWLEDGE_GRAPH
    - EMERGING.TECHNOLOGY.KNOWLEDGE_REPRESENTATION
generation:
  mode: offline-agent
  status: draft
review_status: source_gap
---

# 知识图谱：构建、查询与存储

## 今天学会什么
- 列出来源中的图谱核心概念
- 按采集到更新梳理构建流程
- 按理解问题到结果返回整理查询步骤

## 先建立直觉

本日把知识图谱拆成概念、构建、查询和存储几个环节。原始提纲给出了实体、关系、本体等名词以及流程顺序，但没有定义这些概念或介绍具体存储模型。

## 核心知识

### 概念目录

来源列出实体、关系、属性、本体和谓词逻辑表示法。具体语义、建模规则和场景边界未展开，因此不把术语名称扩展成正式定义。

### 构建与查询流程

构建步骤为数据采集与预处理、信息抽取、知识融合、知识表示、知识存储、知识更新。查询步骤为自然语言理解、实体识别与链接、关系/路径映射、查询生成、执行查询、返回结果。

### 存储

来源列出图形数据库与混合数据库两种存储层设计主题，但没有描述模式、查询语言或选择依据。

**SOURCE_GAP：核心概念定义、适用场景以及图/混合数据库设计比较未在来源中展开。**

## 一张脑图式结构

```text
构建：采集 → 抽取 → 融合 → 表示 → 存储 → 更新
查询：理解 → 实体链接 → 路径映射 → 生成查询 → 执行 → 返回
存储选择：图数据库 / 混合数据库（细节待补）
```

## 架构师视角

图谱系统的工作不止选数据库，还包含数据质量、实体关联、表示和更新流程。查询链路需要从用户意图映射到图中的实体关系；当前来源没有给出具体模型，因此不对存储方案做选型判断。

## 软考关注

- 本仓库没有为该学习日细目关联章节级大纲或教材证据。
- Golden Set 主题级索引：`gs-case-2025-h1-2-q3`, `gs-case-2025-h1-2-q1`。只表示相应 Topic 有索引样本，不证明本日子主题命中或考试频率。
- 不作“高频 / 必考 / 常考”结论。

## 记忆锚点

- 实体、关系、属性、本体、谓词逻辑是来源列出的概念名
- 构建有六步，从采集到更新
- 查询从语言理解到结果返回
- 图/混合数据库的差异为 SOURCE_GAP

## 来源与证据

- `data/learning-paths/system-architect-checkin-v1.json`：`checkin-038` 的来源身份、知识点索引与 mapping。
- 用户提供的打卡归档：`2026年07月/2026-07-15 知识图谱.md`；本 Prompt 区块 SHA-256 记录于 frontmatter，原文未复制。
- `docs/learning-path/SYSTEM_ARCHITECT_CHECKIN_MAPPING_AUDIT.md`：来源映射审计；mapping 不改变 Path Item identity。
- `data/golden-set/`：关联样题索引 `gs-case-2025-h1-2-q3`, `gs-case-2025-h1-2-q1`；不含题干、答案或解析。
