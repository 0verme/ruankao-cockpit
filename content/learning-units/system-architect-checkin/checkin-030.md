---
content_version: offline-learning-unit/v0.1
path_id: system-architect-checkin
path_version: 1.0.0
item_id: checkin-030
order: 30
title: "容灾设计：RPO、RTO 与恢复路径"
source:
  date: "2026-07-07"
  file: "2026年07月/2026-07-07 容灾设计.md"
  prompt_sha256: 6830160da5dfa2938815eea70d90d9b2e19f6028725d613303f391f4cfb43808
mapping:
  status: split
  confidence: high
  topic_ids:
    - QUALITY.ATTRIBUTES.AVAILABILITY
    - RELIABILITY.SOFTWARE.FAULT_TOLERANCE
    - DATA.DISTRIBUTED.REPLICATION_PARTITIONING
generation:
  mode: offline-agent
  status: draft
review_status: source_gap
---

# 容灾设计：RPO、RTO 与恢复路径

## 今天学会什么
- 区分 RPO 的可接受数据丢失时间与 RTO 的恢复时长
- 区分数据容灾与应用容灾
- 梳理备份、日志、复制和多中心方案的关系

## 先建立直觉

灾难恢复要回答两个不同问题：故障后可回到多早的数据状态，以及业务最多能中断多久。先明确这两个目标，才能讨论备份频率、复制方式和备用站点。

## 核心知识

### 目标与类型

RPO 表示可接受的最大数据丢失量，以时间点衡量；RTO 表示从故障发生到业务恢复至可接受状态的最长时间。数据容灾关注数据不丢失或损坏，应用容灾在备用站点准备应用系统并在故障时切换。

### 备份与恢复

来源列出冷备、热备、全量、增量、差量及日志备份。其恢复策略示例是最新全量备份 + 最新差量备份 + 差量之后的增量备份 + 日志记录；执行恢复需要按备份依赖顺序组合。

### 复制与站点

提纲列出同步/异步复制、同城双活、两地三中心、三地五中心、单元化架构等战术名称，但未给出拓扑、切换条件或一致性边界，不能仅凭名称推断 RPO/RTO。

**SOURCE_GAP：多中心拓扑、复制模式差异和切换机制仅列标题，缺少具体定义与适用条件。**

## 一张脑图式结构

```text
灾难恢复目标
├─ RPO：可接受的数据恢复点/丢失时间
└─ RTO：可接受的业务恢复时长
方案层次：备份与日志 → 数据复制 → 备用站点/多中心（拓扑细节待补）
```

## 易混点 / 对比

RPO 关注恢复到哪个数据时间点；RTO 关注业务中断多久。数据容灾与应用容灾关注的恢复对象也不同。

## 架构师视角

先由业务确认数据损失和中断容忍度，再验证备份链是否可恢复、备用应用是否可切换。复制和多中心设计涉及一致性及故障切换，但来源没有提供细节，须补充可追踪材料后再做方案比较。

## 软考关注

- 本仓库没有为该学习日细目关联章节级大纲或教材证据。
- Golden Set 主题级索引：`gs-comp-2025-h1-q08`, `gs-comp-2026-h1-q34`, `gs-case-2024-h2-1-q2`。只表示相应 Topic 有索引样本，不证明本日子主题命中或考试频率。
- 不作“高频 / 必考 / 常考”结论。

## 记忆锚点

- RPO 看数据时间点
- RTO 看业务恢复时长
- 数据容灾保数据，应用容灾准备可切换系统
- 备份链：全量/差量/增量/日志
- 多中心切换语义为 SOURCE_GAP

## 来源与证据

- `data/learning-paths/system-architect-checkin-v1.json`：`checkin-030` 的来源身份、知识点索引与 mapping。
- 用户提供的打卡归档：`2026年07月/2026-07-07 容灾设计.md`；本 Prompt 区块 SHA-256 记录于 frontmatter，原文未复制。
- `docs/learning-path/SYSTEM_ARCHITECT_CHECKIN_MAPPING_AUDIT.md`：来源映射审计；mapping 不改变 Path Item identity。
- `data/golden-set/`：关联样题索引 `gs-comp-2025-h1-q08`, `gs-comp-2026-h1-q34`, `gs-case-2024-h2-1-q2`；不含题干、答案或解析。
