---
content_version: offline-learning-unit/v0.1
path_id: system-architect-checkin
path_version: 1.0.0
item_id: checkin-066
order: 66
title: "Redis 数据类型主题索引"
source:
  date: "2026-08-16"
  file: "2026年08月/2026-08-16 Redis-数据类型.md"
  prompt_sha256: 7a6cd87d93b331b81a1dbe750cf0b09011a1d778c5b0413c41bdf5a6141772aa
mapping:
  status: unmapped
  confidence: low
  topic_ids: []
generation:
  mode: offline-agent
  status: draft
review_status: source_gap
---

# Redis 数据类型主题索引

## 今天学会什么
- 整理来源列出的 Redis 数据类型名称
- 确认每种类型的特点和场景尚未提供
- 为后续按访问模式选择结构保留目录

## 先建立直觉

本日计划按数据类型讲特点和典型场景，但 Prompt 只有类型标题。没有特性和场景证据时，不应把常见用法当作本日已整理内容。

## 核心知识

### 类型目录

String、Hash、List、Set、SortedSet、Bitmap、Geo、HyperLogLog、Stream。

### SOURCE_GAP

各类型操作特征、复杂度、存储限制和典型应用场景均未给出。该项在 Learning Path 中为 UNMAPPED；topic_ids 保持空，不创造 Redis Topic。

**SOURCE_GAP：原始提纲只有数据类型名称，特点和场景栏位无内容。**

## 一张脑图式结构

```text
Redis 数据类型索引
String / Hash / List / Set / SortedSet
Bitmap / Geo / HyperLogLog / Stream
特点与场景待补来源
```

## 架构师视角

数据结构选型依赖读写模式、容量与精度等要求；当前来源不足以提供选择建议。保留 UNMAPPED 以维护 Taxonomy 边界。

## 软考关注

- 本仓库没有为该学习日细目关联章节级大纲或教材证据。
- 本项 `UNMAPPED` 且无 topic_ids；未找到可关联的 Topic 样题证据，不猜测考试归属。
- 不作“高频 / 必考 / 常考”结论。

## 记忆锚点

- 九种类型按原始提纲保留
- 未提供特点和典型场景
- UNMAPPED 保持空 topic_ids
- SOURCE_GAP

## 来源与证据

- `data/learning-paths/system-architect-checkin-v1.json`：`checkin-066` 的来源身份、知识点索引与 mapping。
- 用户提供的打卡归档：`2026年08月/2026-08-16 Redis-数据类型.md`；本 Prompt 区块 SHA-256 记录于 frontmatter，原文未复制。
- `docs/learning-path/SYSTEM_ARCHITECT_CHECKIN_MAPPING_AUDIT.md`：来源映射审计；mapping 不改变 Path Item identity。
