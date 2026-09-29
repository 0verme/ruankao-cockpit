---
content_version: offline-learning-unit/v0.1
path_id: system-architect-checkin
path_version: 1.0.0
item_id: checkin-102
order: 102
title: "反规范化：冗余与查询性能权衡"
source:
  date: "2026-09-24"
  file: "2026年09月/2026-09-24 反规范化设计.md"
  prompt_sha256: d073af3de8e3449c03c4d1f7397697e4025b0b2f345a1e3e8efb2d772c479739
mapping:
  status: split
  confidence: high
  topic_ids:
    - DATA.DATABASE.NORMALIZATION
    - QUALITY.ATTRIBUTES.PERFORMANCE
generation:
  mode: offline-agent
  status: draft
review_status: source_gap
---

# 反规范化：冗余与查询性能权衡

## 今天学会什么
- 说明来源给出的反规范化收益与代价
- 列出增加列、派生列、组表和分割等方法名称
- 把读性能收益与数据冗余/写入成本联系起来

## 先建立直觉

反规范化有意增加冗余或调整表结构，让查询少做连接或计算；这样可能更快，但更新时需要维护重复数据。

## 核心知识

### 收益与成本

来源指出可提高查询性能、降低查询复杂度；代价是引入冗余、存储成本增加、写操作性能降低。

### 方法目录

增加冗余列、增加派生列、重新组表、水平分割、垂直分割、预计算。原始资料没有逐项解释具体实施规则。

**SOURCE_GAP：各反规范化方法只有名称，没有实施模式、同步维护策略或适用边界。**

## 一张脑图式结构

```text
查询瓶颈 → 反规范化
├─ 冗余列/派生列/预计算
├─ 重新组表
└─ 水平/垂直分割
读取简单/更快 ↔ 数据冗余与写入维护成本
```

## 易混点 / 对比

规范化倾向减少冗余；反规范化以可控冗余换查询效率。具体方法与同步策略需结合数据更新频率验证。

## 架构师视角

反规范化要有明确查询目标和冗余维护策略。若没有明确读写瓶颈，仅增加副本字段会扩大一致性责任；来源未提供分表细节，不作实现步骤建议。

## 软考关注

- 本仓库没有为该学习日细目关联章节级大纲或教材证据。
- Golden Set 主题级索引：`gs-comp-2023-h2-q35`, `gs-comp-2025-h1-q34`, `gs-comp-2025-h2-q09`。只表示相应 Topic 有索引样本，不证明本日子主题命中或考试频率。
- 不作“高频 / 必考 / 常考”结论。

## 记忆锚点

- 目标是改善查询性能/复杂度
- 代价为冗余、存储、写性能
- 方法名称六项按来源列出
- 以读写权衡而非覆盖率决定

## 来源与证据

- `data/learning-paths/system-architect-checkin-v1.json`：`checkin-102` 的来源身份、知识点索引与 mapping。
- 用户提供的打卡归档：`2026年09月/2026-09-24 反规范化设计.md`；本 Prompt 区块 SHA-256 记录于 frontmatter，原文未复制。
- `docs/learning-path/SYSTEM_ARCHITECT_CHECKIN_MAPPING_AUDIT.md`：来源映射审计；mapping 不改变 Path Item identity。
- `data/golden-set/`：关联样题索引 `gs-comp-2023-h2-q35`, `gs-comp-2025-h1-q34`, `gs-comp-2025-h2-q09`；不含题干、答案或解析。
