---
content_version: offline-learning-unit/v0.1
path_id: system-architect-checkin
path_version: 1.0.0
item_id: checkin-064
order: 64
title: "Kafka 架构组件索引"
source:
  date: "2026-08-14"
  file: "2026年08月/2026-08-14 消息中间件-kafka.md"
  prompt_sha256: d94b950fce31034aa2db06988dfcf5d146b65adcf7d48dcf610954c87a119065
mapping:
  status: partial
  confidence: high
  topic_ids:
    - ARCH.SOA.SERVICE_BUS
generation:
  mode: offline-agent
  status: draft
review_status: source_gap
---

# Kafka 架构组件索引

## 今天学会什么
- 列出 Kafka 提纲中的生产、存储和消费组件
- 识别主题、分片、副本与消费者组等结构名称
- 保留 KRaft/ZooKeeper 及组件关系的来源缺口

## 先建立直觉

Kafka 本日提供了一张组件清单：生产者写入，Broker、主题、分片、副本和消费者相关对象构成架构讨论范围；但资料没有解释它们的职责或关系。

## 核心知识

### 结构名称

生产者、Broker、主题、分片、副本、消费者、消费者组，以及 KRaft/ZooKeeper。

### SOURCE_GAP

Prompt 没有给出消息如何路由、分片和副本如何协作、消费者组如何分配工作，也未解释 KRaft 与 ZooKeeper 的关系。

**SOURCE_GAP：组件名称没有行为定义、数据流或模式比较。**

## 一张脑图式结构

```text
Producer → Topic / Partition / Replica（经 Broker）→ Consumer / Consumer Group
集群元数据协调：KRaft / ZooKeeper（差异待补来源）
```

## 架构师视角

组件清单有助于规划后续学习，但不能据此推断吞吐、顺序或容错语义。设计前需要补充对应版本的 Kafka 文档与仓库可追踪证据。

## 软考关注

- 本仓库没有为该学习日细目关联章节级大纲或教材证据。
- Golden Set 主题级索引：`gs-comp-2024-h2-q64`。只表示相应 Topic 有索引样本，不证明本日子主题命中或考试频率。
- 不作“高频 / 必考 / 常考”结论。

## 记忆锚点

- Kafka 组件按生产、存储、消费整理
- Topic/Partition/Replica 是提纲结构名
- KRaft/ZooKeeper 差异为 SOURCE_GAP

## 来源与证据

- `data/learning-paths/system-architect-checkin-v1.json`：`checkin-064` 的来源身份、知识点索引与 mapping。
- 用户提供的打卡归档：`2026年08月/2026-08-14 消息中间件-kafka.md`；本 Prompt 区块 SHA-256 记录于 frontmatter，原文未复制。
- `docs/learning-path/SYSTEM_ARCHITECT_CHECKIN_MAPPING_AUDIT.md`：来源映射审计；mapping 不改变 Path Item identity。
- `data/golden-set/`：关联样题索引 `gs-comp-2024-h2-q64`；不含题干、答案或解析。
