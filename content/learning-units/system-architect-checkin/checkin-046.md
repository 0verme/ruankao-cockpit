---
content_version: offline-learning-unit/v0.1
path_id: system-architect-checkin
path_version: 1.0.0
item_id: checkin-046
order: 46
title: "锁、死锁与锁优化主题索引"
source:
  date: "2026-07-23"
  file: "2026年07月/2026-07-23 锁.md"
  prompt_sha256: d7b31f1745cceff6b51f85e265c3dccf5dbc7c072feeda0b9571b69d0249ded7
mapping:
  status: split
  confidence: medium
  topic_ids:
    - SYSTEM.COMPUTER.OPERATING_SYSTEMS
    - DATA.DATABASE.TRANSACTION
    - QUALITY.ATTRIBUTES.PERFORMANCE
generation:
  mode: offline-agent
  status: draft
review_status: source_gap
---

# 锁、死锁与锁优化主题索引

## 今天学会什么
- 整理来源列出的锁类型与作用范围
- 列出死锁处理和锁优化的主题
- 识别当前来源没有提供的定义、条件和策略

## 先建立直觉

锁用于协调对共享资源的访问；本日 Prompt 列出了互斥/读写、悲观/乐观、单机/分布式、表/行等分类，以及死锁治理和优化主题，但没有具体解释。

## 核心知识

### 来源明确的目录

分类轴包括实现机制、竞争策略和作用范围；死锁部分列概念、必要条件、预防、避免、检测与恢复；优化部分列减少持有时间、降低粒度、读写锁替代互斥锁、乐观锁替代悲观锁。

### SOURCE_GAP

锁与临界区定义、死锁必要条件及三种处理方式都没有正文；目录只能作为后续学习索引，不能据此推导适用条件。

**SOURCE_GAP：锁/临界区和死锁的必要条件及解决方式只有标题，没有定义与说明。**

## 一张脑图式结构

```text
锁主题
├─ 分类：实现 / 竞争 / 作用范围
├─ 死锁：预防 / 避免 / 检测与恢复
└─ 优化：持有时间 / 粒度 / 锁类型（内容待补证）
```

## 架构师视角

锁的粒度与竞争策略会影响并发和正确性，但当前材料不足以判断具体优化。先补充资源访问语义、事务边界和死锁规则，再据此评估替代方案。

## 软考关注

- 本仓库没有为该学习日细目关联章节级大纲或教材证据。
- Golden Set 主题级索引：`gs-comp-2023-h2-q03`, `gs-comp-2025-h1-q09`, `gs-comp-2025-h1-q13`。只表示相应 Topic 有索引样本，不证明本日子主题命中或考试频率。
- 不作“高频 / 必考 / 常考”结论。

## 记忆锚点

- 锁分类有三个维度
- 死锁治理列出预防、避免、检测恢复
- 优化主题列出范围和锁类型调整
- 关键定义为 SOURCE_GAP

## 来源与证据

- `data/learning-paths/system-architect-checkin-v1.json`：`checkin-046` 的来源身份、知识点索引与 mapping。
- 用户提供的打卡归档：`2026年07月/2026-07-23 锁.md`；本 Prompt 区块 SHA-256 记录于 frontmatter，原文未复制。
- `docs/learning-path/SYSTEM_ARCHITECT_CHECKIN_MAPPING_AUDIT.md`：来源映射审计；mapping 不改变 Path Item identity。
- `data/golden-set/`：关联样题索引 `gs-comp-2023-h2-q03`, `gs-comp-2025-h1-q09`, `gs-comp-2025-h1-q13`；不含题干、答案或解析。
