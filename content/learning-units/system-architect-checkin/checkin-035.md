---
content_version: offline-learning-unit/v0.1
path_id: system-architect-checkin
path_version: 1.0.0
item_id: checkin-035
order: 35
title: "大模型应用开发：概念与选型索引"
source:
  date: "2026-07-12"
  file: "2026年07月/2026-07-12 大模型应用开发.md"
  prompt_sha256: 7f6f3afe54c193e42a5091b5de9c83de9e234ab80e796a7eb9f8f89d60554393
mapping:
  status: partial
  confidence: medium
  topic_ids:
    - EMERGING.TECHNOLOGY.AI
generation:
  mode: offline-agent
  status: draft
review_status: source_gap
---

# 大模型应用开发：概念与选型索引

## 今天学会什么
- 整理来源列出的大模型应用开发术语
- 识别来源提出的三组技术选型对比
- 区分主题目录与已经有证据支持的定义

## 先建立直觉

本日覆盖的术语横跨模型训练、推理、工具调用和应用编排。原 Prompt 大多只有名词标题，若逐项写成定义会超出来源；因此这里只建立索引并明确待补证范围。

## 核心知识

### 术语目录

提纲列出大模型、多模态、深度思考模式、提示词、MoE、预训练、微调、智能体、模型蒸馏、模型压缩、Function Calling、MCP、Skill、模型幻觉、RAG、拟合。它们是不同层面的主题，当前来源没有解释边界。

### 选型问题

来源列出本地部署 vs 公有云、预训练 vs 微调、全量微调 vs PEFT 三组对比标题，但没有给出比较维度或结论。不能将单一方案写成通用推荐。

### SOURCE_GAP

需为具体术语与选型比较补充可追踪资料后，再形成定义、机制和 trade-off。

**SOURCE_GAP：术语多数只有标题；三组选型对比没有给出证据或判断标准。**

## 一张脑图式结构

```text
大模型应用知识域
├─ 模型：预训练 / 微调 / 蒸馏 / 压缩 / MoE
├─ 应用：提示词 / RAG / Agent / Function Calling / MCP / Skill
├─ 风险：幻觉 / 拟合（定义待补）
└─ 选型：部署方式、训练方式（比较依据待补）
```

## 架构师视角

大模型应用涉及模型能力、部署、工具边界和知识来源等不同决策面。不能把这些术语当作同一层概念，也不能在缺少负载、安全与成本证据时做部署/微调结论。

## 软考关注

- 本仓库没有为该学习日细目关联章节级大纲或教材证据。
- Golden Set 主题级索引：`gs-comp-2025-h1-q20`, `gs-comp-2025-h1-q47`, `gs-comp-2025-h1-q62`。只表示相应 Topic 有索引样本，不证明本日子主题命中或考试频率。
- 不作“高频 / 必考 / 常考”结论。

## 记忆锚点

- 训练与推理部署是不同决策
- 应用编排术语需要分别定义
- 本地/云、预训练/微调、全量/PEFT 是提纲中的对比轴
- 来源不足，保留 SOURCE_GAP

## 来源与证据

- `data/learning-paths/system-architect-checkin-v1.json`：`checkin-035` 的来源身份、知识点索引与 mapping。
- 用户提供的打卡归档：`2026年07月/2026-07-12 大模型应用开发.md`；本 Prompt 区块 SHA-256 记录于 frontmatter，原文未复制。
- `docs/learning-path/SYSTEM_ARCHITECT_CHECKIN_MAPPING_AUDIT.md`：来源映射审计；mapping 不改变 Path Item identity。
- `data/golden-set/`：关联样题索引 `gs-comp-2025-h1-q20`, `gs-comp-2025-h1-q47`, `gs-comp-2025-h1-q62`；不含题干、答案或解析。
