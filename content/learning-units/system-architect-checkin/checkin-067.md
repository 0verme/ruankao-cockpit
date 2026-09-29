---
content_version: offline-learning-unit/v0.1
path_id: system-architect-checkin
path_version: 1.0.0
item_id: checkin-067
order: 67
title: "Redis 持久化：RDB、AOF 与混合模式"
source:
  date: "2026-08-17"
  file: "2026年08月/2026-08-17 Redis-持久化.md"
  prompt_sha256: 3a0cad21174a69717406155b05cac8db590160a452216eca830a4110e9d6a7b3
mapping:
  status: partial
  confidence: high
  topic_ids:
    - DATA.CACHE.CACHE_PERSISTENCE
generation:
  mode: offline-agent
  status: draft
review_status: source_gap
---

# Redis 持久化：RDB、AOF 与混合模式

## 今天学会什么
- 识别来源列出的三种 Redis 持久化主题
- 整理 RDB/AOF 的优缺点与重写主题
- 明确机制与刷盘策略需补充来源

## 先建立直觉

持久化决定内存状态如何以可恢复形式保留。原始提纲将 RDB、AOF、AOF 重写、刷盘策略和混合持久化列为学习范围，但没有描述机制。

## 核心知识

### 主题目录

RDB 与 AOF 各自的核心思想、优缺点；AOF 重写和刷盘策略；混合持久化。

### SOURCE_GAP

未说明快照、追加日志、重写或持久化频率的行为和数据丢失边界，不推断恢复点或性能差异。

**SOURCE_GAP：各持久化机制只有栏目标题，没有实现及恢复语义。**

## 一张脑图式结构

```text
Redis 持久化
├─ RDB：思想/优缺点待补
├─ AOF：思想/重写/刷盘策略待补
└─ 混合持久化：机制待补
```

## 架构师视角

持久化方案需要结合可接受数据损失、恢复时间和写入性能评估；本来源缺少实现细节，不能给出 RDB/AOF 的优劣结论。

## 软考关注

- 本仓库没有为该学习日细目关联章节级大纲或教材证据。
- Golden Set 主题级索引：`gs-case-2025-h1-4-q3`, `gs-case-2020-h2-4-q2`, `gs-case-2025-h1-4-q1`。只表示相应 Topic 有索引样本，不证明本日子主题命中或考试频率。
- 不作“高频 / 必考 / 常考”结论。

## 记忆锚点

- RDB、AOF、混合持久化是三个主题
- AOF 重写和刷盘策略单列
- 恢复语义为 SOURCE_GAP

## 来源与证据

- `data/learning-paths/system-architect-checkin-v1.json`：`checkin-067` 的来源身份、知识点索引与 mapping。
- 用户提供的打卡归档：`2026年08月/2026-08-17 Redis-持久化.md`；本 Prompt 区块 SHA-256 记录于 frontmatter，原文未复制。
- `docs/learning-path/SYSTEM_ARCHITECT_CHECKIN_MAPPING_AUDIT.md`：来源映射审计；mapping 不改变 Path Item identity。
- `data/golden-set/`：关联样题索引 `gs-case-2025-h1-4-q3`, `gs-case-2020-h2-4-q2`, `gs-case-2025-h1-4-q1`；不含题干、答案或解析。
