---
content_version: offline-learning-unit/v0.1
path_id: system-architect-checkin
path_version: 1.0.0
item_id: checkin-101
order: 101
title: "数据库索引：类型与设计原则"
source:
  date: "2026-09-23"
  file: "2026年09月/2026-09-23 数据库索引.md"
  prompt_sha256: 38cdd6f658605dccc60431b9eab83a25ecd3a85dbdff1aea1ff292cd86ee13c6
mapping:
  status: partial
  confidence: high
  topic_ids:
    - DATA.DATABASE.RELATIONAL
generation:
  mode: offline-agent
  status: draft
review_status: source_gap
---

# 数据库索引：类型与设计原则

## 今天学会什么
- 归纳索引查询收益与写入/存储代价
- 区分来源列出的索引分类轴
- 复述来源给出的索引建立原则

## 先建立直觉

索引帮助查询更快定位数据，但需要额外存储并在写入时维护。索引设计应围绕查询条件和区分度，而不是越多越好。

## 核心知识

### 类型

来源列聚簇/非聚簇、单列/联合、非唯一/唯一三组分类。概念定义未在 Prompt 展开。

### 取舍与原则

索引可提高查询速度；代价是额外存储、写性能下降和维护成本增加。来源建议为常用查询条件列及区分度高列建索引，避免对索引列做函数计算，控制数量，并遵循最左匹配原则。

**SOURCE_GAP：索引概念及分类精确定义未提供；最左匹配原则的适用索引结构需要来源补充。**

## 一张脑图式结构

```text
查询模式
├─ 常用条件/高区分度 → 考虑索引
├─ 联合索引：留意最左匹配（细节待补）
└─ 查询收益 ↔ 存储、写性能、维护成本
```

## 架构师视角

索引是访问路径设计的一部分，应结合查询谓词与写入量评估。增加索引可以改善读取，也会增加维护负担；具体选择需结合数据库实现和执行计划。

## 软考关注

- 本仓库没有为该学习日细目关联章节级大纲或教材证据。
- Golden Set 主题级索引：`gs-comp-2025-h2-q08`, `gs-comp-2025-h1-q07`, `gs-comp-2025-h1-q33`。只表示相应 Topic 有索引样本，不证明本日子主题命中或考试频率。
- 不作“高频 / 必考 / 常考”结论。

## 记忆锚点

- 索引提高查询速度
- 代价：空间、写入、维护
- 分类轴：聚簇/非聚簇、单/联合、唯一/非唯一
- 索引不是越多越好

## 来源与证据

- `data/learning-paths/system-architect-checkin-v1.json`：`checkin-101` 的来源身份、知识点索引与 mapping。
- 用户提供的打卡归档：`2026年09月/2026-09-23 数据库索引.md`；本 Prompt 区块 SHA-256 记录于 frontmatter，原文未复制。
- `docs/learning-path/SYSTEM_ARCHITECT_CHECKIN_MAPPING_AUDIT.md`：来源映射审计；mapping 不改变 Path Item identity。
- `data/golden-set/`：关联样题索引 `gs-comp-2025-h2-q08`, `gs-comp-2025-h1-q07`, `gs-comp-2025-h1-q33`；不含题干、答案或解析。
