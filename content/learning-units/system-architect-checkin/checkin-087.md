---
content_version: offline-learning-unit/v0.1
path_id: system-architect-checkin
path_version: 1.0.0
item_id: checkin-087
order: 87
title: "结构化设计：耦合与内聚"
source:
  date: "2026-09-09"
  file: "2026年09月/2026-09-09 结构化设计.md"
  prompt_sha256: 3988581736577fa6855fac575f325220537aff5fec13bb067e35023e86b8d349
mapping:
  status: partial
  confidence: high
  topic_ids:
    - SOFTWARE.ENGINEERING.ANALYSIS_DESIGN
generation:
  mode: offline-agent
  status: draft
review_status: unreviewed
---

# 结构化设计：耦合与内聚

## 今天学会什么
- 列出模块设计的规模、扇入扇出、深度宽度和耦合内聚关注点
- 按来源顺序识别耦合类型
- 按来源顺序识别内聚类型

## 先建立直觉

模块化设计既看模块内部是否围绕同一职责协作，也看模块之间依赖有多紧。来源给出了耦合从低到高、内聚从高到低的分类序列。

## 核心知识

### 模块原则

大小适中、扇入扇出合理、深度宽度适当、高内聚低耦合。耦合表示模块间联系程度；内聚表示模块内部成分间联系程度。

### 耦合（低到高）

非直接、数据、标记、控制、外部、公共、内容耦合。数据耦合传简单参数，标记耦合传记录结构，控制耦合传控制信息；公共/内容耦合共享公共环境或直接触及内部实现。

### 内聚（高到低）

功能、顺序、通信、过程、瞬时、逻辑、偶然内聚。分类表示模块内各部分协作关系逐步变弱；来源将功能内聚列为高端、偶然内聚列为低端。

## 一张脑图式结构

```text
模块质量
├─ 模块内：内聚（功能 → … → 偶然）
└─ 模块间：耦合（非直接 → 数据 → 标记 → 控制 → 外部 → 公共 → 内容）
```

## 易混点 / 对比

耦合看模块之间联系，内聚看模块内部联系；记忆顺序时分别按来源的低到高/高到低方向。

## 架构师视角

架构划分要控制跨模块依赖，同时让每个模块内部围绕一致职责组织。耦合/内聚分类可帮助解释结构质量，但实际判断仍需看真实调用与数据边界。

## 软考关注

- 本仓库没有为该学习日细目关联章节级大纲或教材证据。
- Golden Set 主题级索引：`gs-comp-2025-h1-q06`。只表示相应 Topic 有索引样本，不证明本日子主题命中或考试频率。
- 不作“高频 / 必考 / 常考”结论。

## 记忆锚点

- 耦合：模块之间
- 内聚：模块内部
- 耦合从低到高以内容耦合为高端
- 内聚从高到低以功能内聚为高端

## 来源与证据

- `data/learning-paths/system-architect-checkin-v1.json`：`checkin-087` 的来源身份、知识点索引与 mapping。
- 用户提供的打卡归档：`2026年09月/2026-09-09 结构化设计.md`；本 Prompt 区块 SHA-256 记录于 frontmatter，原文未复制。
- `docs/learning-path/SYSTEM_ARCHITECT_CHECKIN_MAPPING_AUDIT.md`：来源映射审计；mapping 不改变 Path Item identity。
- `data/golden-set/`：关联样题索引 `gs-comp-2025-h1-q06`；不含题干、答案或解析。
