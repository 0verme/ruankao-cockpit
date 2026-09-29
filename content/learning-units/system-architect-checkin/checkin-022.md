---
content_version: offline-learning-unit/v0.1
path_id: system-architect-checkin
path_version: 1.0.0
item_id: checkin-022
order: 22
title: "扩展、动静分离与读写分离"
source:
  date: "2026-06-29"
  file: "2026年06月/2026-06-29.md"
  prompt_sha256: 06ba3e46a72afb20e78a9c465b9753e53ce3c4346a9629fc5bd994a66b6fa5be
mapping:
  status: split
  confidence: high
  topic_ids:
    - QUALITY.ATTRIBUTES.PERFORMANCE
    - QUALITY.ATTRIBUTES.SCALABILITY
generation:
  mode: offline-agent
  status: draft
review_status: source_gap
---

# 扩展、动静分离与读写分离

## 今天学会什么
- 识别来源列出的四种性能设计主题
- 区分已有来源支持的内容与缺失的原理/利弊说明

## 先建立直觉

本日把性能设计从单机战术推进到扩展和读写路径的组织方式。原始 Prompt 只有四个主题标题及优缺点标题，没有给出定义、机制或案例，因此不能把常见解释伪装成该来源已支持的内容。

## 核心知识

### 来源明确的范围

提纲列出垂直扩展、水平扩展、动静分离、读写分离四项，并为每项留有核心思想、优点、缺点栏位；这些栏位均无正文。Learning Path mapping 说明该项跨可伸缩性与性能主题，但不补足上述知识定义。

### SOURCE_GAP

四种方式的边界、实现机制、适用条件和代价均需补充可追踪来源后再解释。当前只保留主题索引，避免按名词推断适用性。

**SOURCE_GAP：原始 Prompt 仅列四个标题及空白优缺点栏位，没有提供可复述的定义、机制或权衡依据。**

## 一张脑图式结构

```text
性能设计
├─ 扩展：垂直 / 水平（细节待补证）
└─ 数据路径：动静分离 / 读写分离（细节待补证）
```

## 架构师视角

扩展策略和读写路径会影响系统容量及数据一致性，但该日来源没有提供任何方案依据。做架构判断前先补齐来源，不能仅凭术语作选型。

## 软考关注

- 本仓库没有为该学习日细目关联章节级大纲或教材证据。
- Golden Set 主题级索引：`gs-comp-2025-h2-q09`, `gs-case-2020-h2-1-q1`, `gs-case-2020-h2-4-q3`。只表示相应 Topic 有索引样本，不证明本日子主题命中或考试频率。
- 不作“高频 / 必考 / 常考”结论。

## 记忆锚点

- 四个主题：垂直扩展、水平扩展、动静分离、读写分离
- 来源未给出各自机制或优缺点
- SOURCE_GAP 保留，不推断适用场景

## 来源与证据

- `data/learning-paths/system-architect-checkin-v1.json`：`checkin-022` 的来源身份、知识点索引与 mapping。
- 用户提供的打卡归档：`2026年06月/2026-06-29.md`；本 Prompt 区块 SHA-256 记录于 frontmatter，原文未复制。
- `docs/learning-path/SYSTEM_ARCHITECT_CHECKIN_MAPPING_AUDIT.md`：来源映射审计；mapping 不改变 Path Item identity。
- `data/golden-set/`：关联样题索引 `gs-comp-2025-h2-q09`, `gs-case-2020-h2-1-q1`, `gs-case-2020-h2-4-q3`；不含题干、答案或解析。
