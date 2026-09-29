---
content_version: offline-learning-unit/v0.1
path_id: system-architect-checkin
path_version: 1.0.0
item_id: checkin-053
order: 53
title: "重试策略：条件、退避与终止"
source:
  date: "2026-07-30"
  file: "2026年07月/2026-07-30 重试策略.md"
  prompt_sha256: c9436608d4abfb7f74c9e0f919e0a2e9a05e9acd34307d4ae3b360cde21c537a
mapping:
  status: partial
  confidence: high
  topic_ids:
    - RELIABILITY.SOFTWARE.FAULT_TOLERANCE
generation:
  mode: offline-agent
  status: draft
review_status: unreviewed
---

# 重试策略：条件、退避与终止

## 今天学会什么
- 识别重试前需要检查的三个条件
- 比较立即重试、固定间隔和指数退避
- 说明必须设置终止条件以避免无界重复请求

## 先建立直觉

重试针对可能自行恢复的短暂失败，但并非所有失败都值得重复执行。重试会再产生请求，因此需要先确认操作可安全重复、故障类型暂时性以及尝试次数有上限。

## 核心知识

### 前置条件

原始提纲明确列出幂等性、区分临时故障和永久故障、必须有终止条件。它们分别约束重复执行的副作用、判断重试价值及停止边界。

### 节奏

立即重试不等待；固定间隔按相同时间间距再试；指数退避逐步拉长等待时间。Prompt 只列策略名称，没有给参数、随机抖动或错误码分类规则。

## 一张脑图式结构

```text
请求失败
├─ 是否可安全重复？（幂等）
├─ 是否可能暂时恢复？（区分临时/永久）
├─ 是否未达终止条件？
└─ 重试节奏：立即 / 固定间隔 / 指数退避
```

## 易混点 / 对比

立即、固定间隔、指数退避是节奏策略，不是失败分类。重试前先满足来源列出的安全条件，再确定停止规则。

## 架构师视角

重试会放大流量并可能重复副作用。服务边界应定义哪些错误可重试、幂等保障如何实现及何时停止；本来源没有提供具体参数，不虚构次数或间隔。

## 软考关注

- 本仓库没有为该学习日细目关联章节级大纲或教材证据。
- Golden Set 主题级索引：`gs-comp-2025-h1-q08`, `gs-comp-2026-h1-q34`, `gs-case-2024-h2-1-q2`。只表示相应 Topic 有索引样本，不证明本日子主题命中或考试频率。
- 不作“高频 / 必考 / 常考”结论。

## 记忆锚点

- 幂等性是重复执行前提之一
- 区分临时故障和永久故障
- 必须有终止条件
- 节奏三类：立即、固定、指数退避

## 来源与证据

- `data/learning-paths/system-architect-checkin-v1.json`：`checkin-053` 的来源身份、知识点索引与 mapping。
- 用户提供的打卡归档：`2026年07月/2026-07-30 重试策略.md`；本 Prompt 区块 SHA-256 记录于 frontmatter，原文未复制。
- `docs/learning-path/SYSTEM_ARCHITECT_CHECKIN_MAPPING_AUDIT.md`：来源映射审计；mapping 不改变 Path Item identity。
- `data/golden-set/`：关联样题索引 `gs-comp-2025-h1-q08`, `gs-comp-2026-h1-q34`, `gs-case-2024-h2-1-q2`；不含题干、答案或解析。
