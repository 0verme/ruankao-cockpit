---
content_version: offline-learning-unit/v0.1
path_id: system-architect-checkin
path_version: 1.0.0
item_id: checkin-091
order: 91
title: "静态测试与质量左移主题索引"
source:
  date: "2026-09-13"
  file: "2026年09月/2026-09-13 静态测试.md"
  prompt_sha256: b463a2d07191be5ae20d2a5ed2a8d395f7b3112b5dea33d6dbeb0e14bcf6785b
mapping:
  status: merge
  confidence: high
  topic_ids:
    - SOFTWARE.ENGINEERING.TESTING
generation:
  mode: offline-agent
  status: draft
review_status: source_gap
---

# 静态测试与质量左移主题索引

## 今天学会什么
- 列出来源中的静态测试方法
- 整理评审、代码分析和工具主题
- 明确具体检查对象与工具用途需补充来源

## 先建立直觉

静态测试部分列桌前检查、走查、审查与静态代码分析，并把它和测试/质量左移联系起来；本 Prompt 没有解释流程和工具。

## 核心知识

### 来源列出的活动

桌前检查、代码走查、代码审查、静态代码质量分析；还要求整理常见工具及用途，但未给工具名称。

### SOURCE_GAP

静态测试定义、评审过程、分析规则、工具与用途表均缺少内容。

**SOURCE_GAP：静态测试流程、对象和工具名单在原始资料中为空。**

## 一张脑图式结构

```text
质量左移
├─ 桌前检查
├─ 代码走查/审查
└─ 静态代码质量分析 → 工具表（来源缺失）
```

## 架构师视角

早期检查活动可能进入需求、设计和代码流程，但工具选择需要明确语言、规则和误报处理。本来源没有提供工具用途，不列未经审计的工具建议。

## 软考关注

- 本仓库没有为该学习日细目关联章节级大纲或教材证据。
- Golden Set 主题级索引：`gs-comp-2024-h2-q55`, `gs-comp-2025-h1-q23`, `gs-comp-2025-h1-q26`。只表示相应 Topic 有索引样本，不证明本日子主题命中或考试频率。
- 不作“高频 / 必考 / 常考”结论。

## 记忆锚点

- 静态活动列四类
- 质量左移是主题标签
- 工具名称和用途未提供
- SOURCE_GAP

## 来源与证据

- `data/learning-paths/system-architect-checkin-v1.json`：`checkin-091` 的来源身份、知识点索引与 mapping。
- 用户提供的打卡归档：`2026年09月/2026-09-13 静态测试.md`；本 Prompt 区块 SHA-256 记录于 frontmatter，原文未复制。
- `docs/learning-path/SYSTEM_ARCHITECT_CHECKIN_MAPPING_AUDIT.md`：来源映射审计；mapping 不改变 Path Item identity。
- `data/golden-set/`：关联样题索引 `gs-comp-2024-h2-q55`, `gs-comp-2025-h1-q23`, `gs-comp-2025-h1-q26`；不含题干、答案或解析。
