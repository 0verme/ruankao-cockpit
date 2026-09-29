---
content_version: offline-learning-unit/v0.1
path_id: system-architect-checkin
path_version: 1.0.0
item_id: checkin-071
order: 71
title: "缓存更新模式：旁路、穿透、写回与 CDC"
source:
  date: "2026-08-21"
  file: "2026年08月/2026-08-21 Redis-缓存更新模式.md"
  prompt_sha256: cc4018fbc102e41d3e1d5b5c718624d2c0c48623d94af40a5949d78105d084bb
mapping:
  status: partial
  confidence: high
  topic_ids:
    - DATA.CACHE.CACHE_ASIDE
generation:
  mode: offline-agent
  status: draft
review_status: source_gap
---

# 缓存更新模式：旁路、穿透、写回与 CDC

## 今天学会什么
- 列出来源中的四种缓存更新模式
- 识别每种模式需要比较的优缺点和场景
- 明确读写顺序及一致性权衡仍需来源支持

## 先建立直觉

缓存更新涉及数据由谁读写、何时回写，以及数据库变化如何到达缓存。不同模式改变一致性与性能责任，但 Prompt 只列出模式名。

## 核心知识

### 模式索引

旁路缓存、读/写穿透、写回、CDC + 异步更新；原始提纲为每类列出核心思想、优缺点和适用场景栏目。

### SOURCE_GAP

没有说明读写顺序、失效策略、失败补偿或异步延迟边界，不把模式名称扩展成实现建议。

**SOURCE_GAP：四种缓存更新模式没有机制、顺序与适用条件说明。**

## 一张脑图式结构

```text
数据源 ↔ 缓存
├─ 旁路
├─ 读/写穿透
├─ 写回
└─ CDC 异步更新（流程与一致性边界待补）
```

## 架构师视角

缓存写入与数据库状态可能短暂不一致，更新模式要明确数据权威、同步方向和失败恢复。当前资料不足以说明每种模式的行为，选型前需补证。

## 软考关注

- 本仓库没有为该学习日细目关联章节级大纲或教材证据。
- Golden Set 主题级索引：`gs-case-2024-h2-2-q1`, `gs-case-2024-h2-2-q3`, `gs-case-2025-h2-3-q3`。只表示相应 Topic 有索引样本，不证明本日子主题命中或考试频率。
- 不作“高频 / 必考 / 常考”结论。

## 记忆锚点

- 旁路、穿透、写回、CDC 异步更新四类
- 模式差异要看读写责任和更新顺序
- 来源未给一致性边界
- SOURCE_GAP

## 来源与证据

- `data/learning-paths/system-architect-checkin-v1.json`：`checkin-071` 的来源身份、知识点索引与 mapping。
- 用户提供的打卡归档：`2026年08月/2026-08-21 Redis-缓存更新模式.md`；本 Prompt 区块 SHA-256 记录于 frontmatter，原文未复制。
- `docs/learning-path/SYSTEM_ARCHITECT_CHECKIN_MAPPING_AUDIT.md`：来源映射审计；mapping 不改变 Path Item identity。
- `data/golden-set/`：关联样题索引 `gs-case-2024-h2-2-q1`, `gs-case-2024-h2-2-q3`, `gs-case-2025-h2-3-q3`；不含题干、答案或解析。
