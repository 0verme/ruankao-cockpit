---
content_version: offline-learning-unit/v0.1
path_id: system-architect-checkin
path_version: 1.0.0
item_id: checkin-072
order: 72
title: "Redis 缓存故障：击穿、穿透、雪崩与大 Key"
source:
  date: "2026-08-22"
  file: "2026年08月/2026-08-22 Redis-常见问题及解决方案.md"
  prompt_sha256: e3cc7e084c7165923f77e6bdcbf41cd7a8db790708694e6a44b8ac8b900882b2
mapping:
  status: merge
  confidence: high
  topic_ids:
    - DATA.CACHE.CACHE_FAILURE
generation:
  mode: offline-agent
  status: draft
review_status: source_gap
---

# Redis 缓存故障：击穿、穿透、雪崩与大 Key

## 今天学会什么
- 区分来源列出的缓存故障主题
- 将来源给出的应对手段映射到相应故障类别
- 识别每种手段的触发条件尚未在来源中解释

## 先建立直觉

缓存问题可以按请求是否集中到单个热点、缓存是否命中或大量键是否同时失效来组织。原始提纲给出了问题名和一些处理手段，但概念定义没有正文。

## 核心知识

### 故障与措施索引

击穿：分散过期、热点键不过期、逻辑过期、串行重建。穿透：参数校验、缓存空对象、布隆过滤器。雪崩：错开过期、高可用集群、多级缓存、限流/降级/熔断、监控告警。

### 其他问题

冷启动列缓存预热。BigKey 危害列命令处理与网络阻塞、数据倾斜、主从复制延迟；处理主题包括拆分键、选结构、压缩、惰性删除。

### SOURCE_GAP

定义、布隆过滤器误判率、逻辑过期和串行重建细节未说明，不能把清单当作完整方案。

**SOURCE_GAP：故障定义和措施的适用条件/机制未完整提供。**

## 一张脑图式结构

```text
故障分类
├─ 单热点失效：击穿 → 控制重建/过期
├─ 缓存无结果：穿透 → 校验/空对象/过滤器
├─ 大量同时失效：雪崩 → 分散/高可用/限流降级
├─ 冷启动：预热
└─ BigKey：拆分/结构选择/压缩/惰性删除
```

## 架构师视角

故障处置应先辨认负载形态，再选控制重建、过滤、限流或拆分等方向。监控告警需要覆盖缓存失效和复制延迟；具体参数及误判权衡待补来源。

## 软考关注

- 本仓库没有为该学习日细目关联章节级大纲或教材证据。
- Golden Set 主题级索引：`gs-case-2025-h2-3-q3`, `gs-case-2020-h2-4-q3`。只表示相应 Topic 有索引样本，不证明本日子主题命中或考试频率。
- 不作“高频 / 必考 / 常考”结论。

## 记忆锚点

- 击穿、穿透、雪崩不是同一问题
- 冷启动关注预热
- BigKey 可能导致阻塞、倾斜和复制延迟
- 解决措施是来源主题清单，不等于配置方案

## 来源与证据

- `data/learning-paths/system-architect-checkin-v1.json`：`checkin-072` 的来源身份、知识点索引与 mapping。
- 用户提供的打卡归档：`2026年08月/2026-08-22 Redis-常见问题及解决方案.md`；本 Prompt 区块 SHA-256 记录于 frontmatter，原文未复制。
- `docs/learning-path/SYSTEM_ARCHITECT_CHECKIN_MAPPING_AUDIT.md`：来源映射审计；mapping 不改变 Path Item identity。
- `data/golden-set/`：关联样题索引 `gs-case-2025-h2-3-q3`, `gs-case-2020-h2-4-q3`；不含题干、答案或解析。
