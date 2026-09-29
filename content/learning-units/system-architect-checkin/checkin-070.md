---
content_version: offline-learning-unit/v0.1
path_id: system-architect-checkin
path_version: 1.0.0
item_id: checkin-070
order: 70
title: "Redis 集群：主从、哨兵与 Cluster"
source:
  date: "2026-08-20"
  file: "2026年08月/2026-08-20 Redis-集群架构.md"
  prompt_sha256: c199f1faac2e882a8e13d2a950f14d517fbe9f00dd5506ac4ec4b20ddb36a044
mapping:
  status: split
  confidence: high
  topic_ids:
    - DATA.CACHE.CACHE_PERSISTENCE
    - DATA.DISTRIBUTED.REPLICATION_PARTITIONING
generation:
  mode: offline-agent
  status: draft
review_status: source_gap
---

# Redis 集群：主从、哨兵与 Cluster

## 今天学会什么
- 识别三类 Redis 集群主题
- 列出来源希望比较的架构、原理、优缺点和适用场景
- 避免凭模式名称推导故障转移或分片语义

## 先建立直觉

主从、哨兵与 Redis Cluster 是来源列出的三类集群方案。本日应比较结构和故障处理，但原始提纲仅提供比较栏目。

## 核心知识

### 方案目录

主从复制包含全量/增量同步主题；哨兵集群与 Redis Cluster 分别要求学习组成、原理、优缺点和适用场景。

### SOURCE_GAP

Prompt 没有描述复制、故障检测、选主、分片和路由行为，也没有给适用条件。

**SOURCE_GAP：三种集群的架构细节和恢复/分片语义均只有标题。**

## 一张脑图式结构

```text
Redis 部署主题
├─ 主从复制：全量 / 增量同步
├─ 哨兵集群：组成与切换待补
└─ Redis Cluster：组成与分片路由待补
```

## 架构师视角

高可用与数据分布是不同问题，集群模式需按故障恢复、一致性与容量目标评估。当前来源不足以比较三个方案，避免生成未经证实的优缺点表。

## 软考关注

- 本仓库没有为该学习日细目关联章节级大纲或教材证据。
- Golden Set 主题级索引：`gs-case-2025-h1-4-q3`, `gs-case-2020-h2-4-q2`, `gs-case-2024-h1-5-q3`。只表示相应 Topic 有索引样本，不证明本日子主题命中或考试频率。
- 不作“高频 / 必考 / 常考”结论。

## 记忆锚点

- 主从、哨兵、Cluster 三类名称
- 全量与增量同步属于主从主题
- 切换与分片语义为 SOURCE_GAP

## 来源与证据

- `data/learning-paths/system-architect-checkin-v1.json`：`checkin-070` 的来源身份、知识点索引与 mapping。
- 用户提供的打卡归档：`2026年08月/2026-08-20 Redis-集群架构.md`；本 Prompt 区块 SHA-256 记录于 frontmatter，原文未复制。
- `docs/learning-path/SYSTEM_ARCHITECT_CHECKIN_MAPPING_AUDIT.md`：来源映射审计；mapping 不改变 Path Item identity。
- `data/golden-set/`：关联样题索引 `gs-case-2025-h1-4-q3`, `gs-case-2020-h2-4-q2`, `gs-case-2024-h1-5-q3`；不含题干、答案或解析。
