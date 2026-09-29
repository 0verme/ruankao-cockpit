---
content_version: offline-learning-unit/v0.1
path_id: system-architect-checkin
path_version: 1.0.0
item_id: checkin-037
order: 37
title: "智能体：ReAct 循环与组件边界"
source:
  date: "2026-07-14"
  file: "2026年07月/2026-07-14 智能体架构.md"
  prompt_sha256: 65dcbe82959be0153d02bd55d18e4d1d7f452b22741fc9223f40f9577ad6ae7d
mapping:
  status: split
  confidence: medium
  topic_ids:
    - EMERGING.TECHNOLOGY.AI
    - ARCH.SOA.SERVICE_MODEL
    - ARCH.CLOUD_NATIVE.EVENT_DRIVEN
generation:
  mode: offline-agent
  status: draft
review_status: source_gap
---

# 智能体：ReAct 循环与组件边界

## 今天学会什么
- 复述 ReAct 的思考—行动—观察迭代
- 列出 Prompt 中的智能体应用组成模块
- 识别实现方式、通信和网关部分尚缺少细节

## 先建立直觉

ReAct 描述的是模型在任务中根据中间结果继续行动的循环：先分析下一步，再执行工具或回答，观察结果后继续。复杂任务因此可以分步骤推进，但循环本身并不保证工具结果正确。

## 核心知识

### ReAct

Reasoning 分析当前情况并决定行动；Acting 执行工具调用或生成答案；Observation 接收工具结果；Agent 可据观察继续迭代直到任务完成。来源指出它适用于分解复杂问题、动态调整策略和多次工具调用。

### 架构组件与通信主题

提纲列出智能体应用、大模型、知识库、规划、记忆、调度、业务服务、评估等组件；并列 HTTP API、事件驱动两种智能体通信主题，以及大模型网关的问题、依赖倒置和流量治理主题。来源没有描述模块接口或治理规则。

### SOURCE_GAP

智能体定义、低代码/编程式实现差别、各模块职责、网关依赖倒置与流量治理均只有标题，需补充来源。

**SOURCE_GAP：除 ReAct 循环外，Agent 定义、模块职责、编排方式和网关设计只有标题或清单。**

## 一张脑图式结构

```text
Agent 循环：思考 → 行动/工具 → 观察 → 再决策
模块索引：模型 / 知识 / 规划 / 记忆 / 调度 / 服务 / 评估
边界与接口细节待补来源
```

## 架构师视角

把模型、工具、知识、业务服务和评估拆成明确模块有助于讨论边界；但当前提纲没有给出接口契约或失败策略。上线设计前需要分别定义依赖、权限、超时和验证责任，不能从组件名称直接推断实现。

## 软考关注

- 本仓库没有为该学习日细目关联章节级大纲或教材证据。
- Golden Set 主题级索引：`gs-comp-2025-h1-q20`, `gs-comp-2025-h1-q35`, `gs-comp-2025-h1-q47`。只表示相应 Topic 有索引样本，不证明本日子主题命中或考试频率。
- 不作“高频 / 必考 / 常考”结论。

## 记忆锚点

- ReAct：Reasoning → Acting → Observation → 迭代
- 组件清单不等于模块契约
- HTTP API 与事件驱动是待学习通信主题
- 除 ReAct 外多处为 SOURCE_GAP

## 来源与证据

- `data/learning-paths/system-architect-checkin-v1.json`：`checkin-037` 的来源身份、知识点索引与 mapping。
- 用户提供的打卡归档：`2026年07月/2026-07-14 智能体架构.md`；本 Prompt 区块 SHA-256 记录于 frontmatter，原文未复制。
- `docs/learning-path/SYSTEM_ARCHITECT_CHECKIN_MAPPING_AUDIT.md`：来源映射审计；mapping 不改变 Path Item identity。
- `data/golden-set/`：关联样题索引 `gs-comp-2025-h1-q20`, `gs-comp-2025-h1-q35`, `gs-comp-2025-h1-q47`；不含题干、答案或解析。
