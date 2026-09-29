---
content_version: offline-learning-unit/v0.1
path_id: system-architect-checkin
path_version: 1.0.0
item_id: checkin-107
order: 107
title: "NoSQL 数据库：类型与选型目录"
source:
  date: "2026-09-30"
  file: "2026年09月/2026-09-30 NoSQL数据库.md"
  prompt_sha256: 9160464b1dab12053b96307c2523eac057dbf21499f8a3582fc908c0ec7ae93d
mapping:
  status: exact
  confidence: high
  topic_ids:
    - DATA.DATABASE.NOSQL
generation:
  mode: offline-agent
  status: draft
review_status: source_gap
---

# NoSQL 数据库：类型与选型目录

## 今天学会什么
- 列出来源提出的关系数据库挑战
- 整理 NoSQL 类型分类
- 明确类型特征、场景和代表产品需要补充来源

## 先建立直觉

NoSQL 主题关注关系数据库面对可用性、性能、扩展和数据结构灵活性时的挑战；来源要求比较多种存储类型，但没有给定义。

## 核心知识

### 来源列出的挑战

可用性差、性能瓶颈、扩展困难、数据结构不灵活。

### 类型索引

Key-Value、文档、列式、图、全文搜索、时序、向量数据库；原始提纲要求每类整理特点、场景和代表，但均无正文。

**SOURCE_GAP：NoSQL 定义、关系型对比和七类数据库特性/场景均未展开。**

## 一张脑图式结构

```text
NoSQL 分类索引
├─ Key-Value / 文档 / 列式 / 图
├─ 全文搜索 / 时序 / 向量
特性、场景、代表与模型比较待补证
```

## 架构师视角

数据模型应由访问模式、事务和查询目标驱动。仅凭 NoSQL 标签无法决定存储产品；需要补充一致性、扩展和数据模型来源后再选型。

## 软考关注

- 本仓库没有为该学习日细目关联章节级大纲或教材证据。
- Golden Set 主题级索引：`gs-comp-2023-h2-q38`, `gs-case-2025-h1-2-q3`, `gs-case-2024-h1-5-q2`。只表示相应 Topic 有索引样本，不证明本日子主题命中或考试频率。
- 不作“高频 / 必考 / 常考”结论。

## 记忆锚点

- 关系型挑战四项来自来源
- NoSQL 类型七类按原始提纲列出
- 分类名称不等于产品选择
- SOURCE_GAP

## 来源与证据

- `data/learning-paths/system-architect-checkin-v1.json`：`checkin-107` 的来源身份、知识点索引与 mapping。
- 用户提供的打卡归档：`2026年09月/2026-09-30 NoSQL数据库.md`；本 Prompt 区块 SHA-256 记录于 frontmatter，原文未复制。
- `docs/learning-path/SYSTEM_ARCHITECT_CHECKIN_MAPPING_AUDIT.md`：来源映射审计；mapping 不改变 Path Item identity。
- `data/golden-set/`：关联样题索引 `gs-comp-2023-h2-q38`, `gs-case-2025-h1-2-q3`, `gs-case-2024-h1-5-q2`；不含题干、答案或解析。
