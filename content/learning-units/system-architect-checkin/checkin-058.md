---
content_version: offline-learning-unit/v0.1
path_id: system-architect-checkin
path_version: 1.0.0
item_id: checkin-058
order: 58
title: "DDD 架构模式：层次、六边形与事件模式"
source:
  date: "2026-08-08"
  file: "2026年08月/2026-08-08 领域驱动设计-架构模式.md"
  prompt_sha256: e6e773cab91f8a9e4b0230350e02e73981c921944068ba49d61ae9a5ea951171
mapping:
  status: split
  confidence: medium
  topic_ids:
    - ARCH.FOUNDATION.STYLES
    - ARCH.LAYERED.LAYERS
    - ARCH.CLOUD_NATIVE.EVENT_DRIVEN
generation:
  mode: offline-agent
  status: draft
review_status: source_gap
---

# DDD 架构模式：层次、六边形与事件模式

## 今天学会什么
- 列出来源中的分层架构层次
- 识别六边形、洋葱、事件溯源与 CQRS 主题
- 说明只有层次名称有依据的内容不延伸成完整模式定义

## 先建立直觉

架构模式影响领域逻辑与接口、基础设施之间的组织方式。本日提纲对分层架构给出层名称，对其他模式主要只列标题，因此需要按证据深浅区别整理。

## 核心知识

### 分层架构

来源列出领域层、应用层、用户接口层、基础设施层，并提到依赖倒置与仓储设计模式；没有进一步说明依赖方向和各层职责。

### 其他模式索引

六边形架构、洋葱架构、事件溯源和 CQRS 均只有名称及“核心思想”标题，没有正文定义。

**SOURCE_GAP：分层职责与依赖规则不完整；六边形、洋葱、事件溯源和 CQRS 只有标题。**

## 一张脑图式结构

```text
领域模型相关架构模式
├─ 分层：领域 / 应用 / 用户接口 / 基础设施
│  └─ 依赖倒置、仓储（细节待补）
└─ 六边形 / 洋葱 / 事件溯源 / CQRS（定义待补）
```

## 架构师视角

选择架构模式需要解释依赖方向、领域逻辑边界和数据读写路径。当前资料只提供名称与分层名录，不足以比较模式或声称一种更适合 DDD；后续应按来源补齐。

## 软考关注

- 本仓库没有为该学习日细目关联章节级大纲或教材证据。
- Golden Set 主题级索引：`gs-comp-2025-h2-q01`, `gs-comp-2024-h2-q37`, `gs-comp-2025-h1-q57`。只表示相应 Topic 有索引样本，不证明本日子主题命中或考试频率。
- 不作“高频 / 必考 / 常考”结论。

## 记忆锚点

- 分层四部分：领域、应用、用户接口、基础设施
- 依赖倒置和仓储是提纲主题
- 其他模式只有名称
- 未补证前不做模式优劣比较

## 来源与证据

- `data/learning-paths/system-architect-checkin-v1.json`：`checkin-058` 的来源身份、知识点索引与 mapping。
- 用户提供的打卡归档：`2026年08月/2026-08-08 领域驱动设计-架构模式.md`；本 Prompt 区块 SHA-256 记录于 frontmatter，原文未复制。
- `docs/learning-path/SYSTEM_ARCHITECT_CHECKIN_MAPPING_AUDIT.md`：来源映射审计；mapping 不改变 Path Item identity。
- `data/golden-set/`：关联样题索引 `gs-comp-2025-h2-q01`, `gs-comp-2024-h2-q37`, `gs-comp-2025-h1-q57`；不含题干、答案或解析。
