---
content_version: offline-learning-unit/v0.1
path_id: system-architect-checkin
path_version: 1.0.0
item_id: checkin-052
order: 52
title: "限流：算法、范围与超限处置"
source:
  date: "2026-07-29"
  file: "2026年07月/2026-07-29 限流.md"
  prompt_sha256: 5e881676a0644f6b89e7fecd4faeaecbd9c57e55a2dd9635881b322c4cefd26e
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

# 限流：算法、范围与超限处置

## 今天学会什么
- 列出来源中的四种限流算法
- 区分单实例与集群限流主题
- 说明超限请求可被丢弃、排队或降级

## 先建立直觉

限流是在系统处理能力有限时控制进入的请求量。它既包含如何计算请求速率，也包含限制作用于单个实例还是集群，以及超限后如何处置。

## 核心知识

### 来源列出的算法

固定时间窗口、滑动时间窗口、令牌桶和漏桶。Prompt 没有给出窗口边界、令牌生成、队列或突发流量处理细节。

### 范围和处置

来源区分单实例与集群限流，并列请求维度和三种超限处理：直接抛弃、排队等待、降级方案；限流维度只有标题，没有具体字段。

**SOURCE_GAP：四种算法的状态更新/边界语义及限流维度在来源中未说明。**

## 一张脑图式结构

```text
请求流量 → 限流器
├─ 算法：固定窗口 / 滑动窗口 / 令牌桶 / 漏桶
├─ 范围：单实例 / 集群
└─ 超限：丢弃 / 排队 / 降级
```

## 架构师视角

限流要和系统容量、请求优先级及集群协调范围一起设计。超限策略影响用户体验和资源占用；当前来源未说明各算法细节，实际选型需补充实现及一致性证据。

## 软考关注

- 本仓库没有为该学习日细目关联章节级大纲或教材证据。
- Golden Set 主题级索引：`gs-comp-2025-h2-q09`, `gs-case-2020-h2-1-q1`, `gs-case-2020-h2-4-q3`。只表示相应 Topic 有索引样本，不证明本日子主题命中或考试频率。
- 不作“高频 / 必考 / 常考”结论。

## 记忆锚点

- 算法四项：固定/滑动窗口、令牌桶、漏桶
- 范围：单实例与集群
- 处置：丢弃、排队、降级
- 限流维度与算法语义为 SOURCE_GAP

## 来源与证据

- `data/learning-paths/system-architect-checkin-v1.json`：`checkin-052` 的来源身份、知识点索引与 mapping。
- 用户提供的打卡归档：`2026年07月/2026-07-29 限流.md`；本 Prompt 区块 SHA-256 记录于 frontmatter，原文未复制。
- `docs/learning-path/SYSTEM_ARCHITECT_CHECKIN_MAPPING_AUDIT.md`：来源映射审计；mapping 不改变 Path Item identity。
- `data/golden-set/`：关联样题索引 `gs-comp-2025-h2-q09`, `gs-case-2020-h2-1-q1`, `gs-case-2020-h2-4-q3`；不含题干、答案或解析。
