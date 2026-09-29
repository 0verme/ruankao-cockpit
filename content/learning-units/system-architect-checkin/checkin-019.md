---
content_version: offline-learning-unit/v0.1
path_id: system-architect-checkin
path_version: 1.0.0
item_id: checkin-019
order: 19
title: 性能指标、并发、并行与池化
source:
  date: "2026-06-26"
  file: "2026年06月/2026-06-26.md"
  prompt_sha256: 5b2fef31814aa6e22a80293e4d040194c52a2b69d94193f22f1551b16ba41bb7
mapping:
  status: partial
  confidence: high
  topic_ids:
    - QUALITY.ATTRIBUTES.PERFORMANCE
generation:
  mode: offline-agent
  status: draft
review_status: source_gap
---

# 性能指标、并发、并行与池化

## 今天学会什么
- 识别来源列出的性能衡量指标。
- 识别本日提纲涉及的并发、并行、池化与享元主题。
- 明确当前来源没有给出哪些定义与区别，避免混淆为已验证结论。

## 先建立直觉

性能不能只用“快”描述。来源列出响应时间、响应时间百分位值、吞吐量、资源利用率和错误率作为衡量维度；它们分别从时延、尾部表现、处理量、资源消耗和失败情况观察系统。

## 核心知识

本单元提纲还列出并发战术、并行战术、并发与并行的区别、池化思想和享元设计模式。但这些小节只有标题，没有提供概念定义、项目案例或区分规则。为避免用未引用的常识替代来源，正文只确认它们属于本单元待学习的主题，不擅自解释其实现细节。

**SOURCE_GAP：**需要可追踪来源补充并发/并行定义与区别、池化原理、享元关系和性能优化案例。

## 一张脑图式结构
```text
性能观察
├─ 响应时间 / 百分位响应时间
├─ 吞吐量
├─ 资源利用率
└─ 错误率

设计主题（来源只给标题，待补证）
├─ 并发
├─ 并行
└─ 池化 / 享元
```

## 易混点 / 对比
来源仅提出“并发和并行的区别”，没有给出解释依据；本单元不自行比较。响应时间百分位值也不等于平均响应时间，当前提纲列出两者为不同指标，但未指定统计口径。

## 架构师视角
性能优化要先确定观察指标，再讨论具体战术；若只看平均响应时间，可能漏掉来源单独列出的百分位表现或错误率。选择并发、并行或池化前，需要补齐其定义、约束和适用条件，不能以名词直接推导收益。

## 软考关注
仓库没有本单元细目的大纲段落或直接样题证据；不作频率结论。

## 记忆锚点
- 五类指标：时延、百分位时延、吞吐、资源、错误。
- 并发/并行/池化/享元是提纲主题，不代表细节已经有证据。
- SOURCE_GAP 未补齐前，不给出具体优化结论。

## 来源与证据
- `data/learning-paths/system-architect-checkin-v1.json`：`checkin-019` 的指标与主题索引、PARTIAL mapping。
- 用户提供的打卡归档：`2026年06月/2026-06-26.md`；Prompt 区块 SHA-256 见 frontmatter。
- `docs/learning-path/SYSTEM_ARCHITECT_CHECKIN_MAPPING_AUDIT.md`：本项属于性能 Topic 的部分覆盖。
