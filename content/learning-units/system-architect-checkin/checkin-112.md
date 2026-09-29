---
content_version: offline-learning-unit/v0.1
path_id: system-architect-checkin
path_version: 1.0.0
item_id: checkin-112
order: 112
title: "分片系统常见问题：事务与跨分片查询"
source:
  date: "2026-10-05"
  file: "2026年10月/2026-10-05.md"
  prompt_sha256: 0f442178e924a47a6203ff56d0d69bc588e2fbb5ab5b85e8a3af7cd99999fc48
mapping:
  status: split
  confidence: medium
  topic_ids:
    - DATA.DISTRIBUTED.REPLICATION_PARTITIONING
    - DATA.DISTRIBUTED.CONSISTENCY
    - DATA.DATABASE.TRANSACTION
generation:
  mode: offline-agent
  status: draft
review_status: source_gap
---

# 分片系统常见问题：事务与跨分片查询

## 今天学会什么
- 识别来源列出的分片后两类查询/事务问题
- 整理 XA、Seata AT、广播表等方案名称
- 明确各方案流程与适用边界需补充来源

## 先建立直觉

分片将数据分到不同位置后，原本单库内的事务或查询可能跨越多个分片。原始提纲列出若干处理方向，但没有定义协议或实现流程。

## 核心知识

### 分布式事务

来源列问题描述及 XA 事务、Seata AT 模式。

### 跨分片查询

列广播表、冗余字段、搜索引擎；非分片键查询列索引表、冗余表、搜索引擎。

### SOURCE_GAP

各方案如何协调、同步更新、处理失败或保证结果一致均未说明；不能将清单视为可直接实施的设计。

**SOURCE_GAP：事务协议和跨分片查询方案只有名称/标题，没有机制、权衡或场景。**

## 一张脑图式结构

```text
分片场景问题
├─ 跨分片事务：XA / Seata AT（流程待补）
├─ 跨分片查询：广播表 / 冗余字段 / 搜索引擎
└─ 非分片键查询：索引表 / 冗余表 / 搜索引擎
```

## 架构师视角

分片提高分布能力的同时会扩大事务与查询范围。架构师要明确一致性、数据冗余和查询代价；当前来源没有方案细节，不能只按名词选型。

## 软考关注

- 本仓库没有为该学习日细目关联章节级大纲或教材证据。
- Golden Set 主题级索引：`gs-case-2024-h1-3-q1`, `gs-case-2024-h2-2-q3`, `gs-case-2025-h1-4-q3`。只表示相应 Topic 有索引样本，不证明本日子主题命中或考试频率。
- 不作“高频 / 必考 / 常考”结论。

## 记忆锚点

- 事务问题列 XA、Seata AT
- 跨分片查询有广播/冗余/搜索索引
- 非分片键查询另列索引表/冗余表
- 实现语义是 SOURCE_GAP

## 来源与证据

- `data/learning-paths/system-architect-checkin-v1.json`：`checkin-112` 的来源身份、知识点索引与 mapping。
- 用户提供的打卡归档：`2026年10月/2026-10-05.md`；本 Prompt 区块 SHA-256 记录于 frontmatter，原文未复制。
- `docs/learning-path/SYSTEM_ARCHITECT_CHECKIN_MAPPING_AUDIT.md`：来源映射审计；mapping 不改变 Path Item identity。
- `data/golden-set/`：关联样题索引 `gs-case-2024-h1-3-q1`, `gs-case-2024-h2-2-q3`, `gs-case-2025-h1-4-q3`；不含题干、答案或解析。
