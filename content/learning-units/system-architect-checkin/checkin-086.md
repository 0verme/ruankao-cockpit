---
content_version: offline-learning-unit/v0.1
path_id: system-architect-checkin
path_version: 1.0.0
item_id: checkin-086
order: 86
title: "系统设计、业务流程与工作流管理"
source:
  date: "2026-09-08"
  file: "2026年09月/2026-09-08 系统设计.md"
  prompt_sha256: 5a8a70b5cf6b1ee316a823316d78d03a96e96215df980549dd70f732505e9263
mapping:
  status: split
  confidence: high
  topic_ids:
    - SOFTWARE.ENGINEERING.ANALYSIS_DESIGN
    - SOFTWARE.MODELING.BUSINESS_PROCESS
generation:
  mode: offline-agent
  status: draft
review_status: unreviewed
---

# 系统设计、业务流程与工作流管理

## 今天学会什么
- 区分概要设计和详细设计
- 说出用户界面设计三项原则
- 梳理 WFMS 参考模型六模块

## 先建立直觉

系统设计把功能需求变成实施蓝图：概要设计分配模块和调用关系，详细设计把任务落实到具体技术和处理方法。业务流程则关注输入如何经过活动转为输出。

## 核心知识

### 设计层次

概要设计将功能分配给模块并形成系统结构；详细设计把总任务拆成具体任务并选择实现手段。用户界面设计原则为用户控制、减轻记忆负担、保持一致。

### 业务流程与 WFMS

业务流程由相互作用的活动把输入变成输出。工作流参考模型包含执行服务、工作流引擎、流程定义工具、客户端应用、调用应用、管理监控工具；分别负责流程实例管理执行、提供运行环境、定义流程、面向用户调用、被流程调用、监控和维护数据。

## 一张脑图式结构

```text
需求 → 概要设计（模块/调用） → 详细设计（具体处理）
业务流程：输入资源 → 活动及交互 → 输出/价值
WFMS：定义 → 引擎执行 → 客户端/调用应用 + 监控
```

## 架构师视角

设计时需把功能分配与流程运行责任说清楚。WFMS 不是单一引擎，还包含定义、调用和监控环节；架构师应明确业务逻辑由哪部分负责。

## 软考关注

- 本仓库没有为该学习日细目关联章节级大纲或教材证据。
- Golden Set 主题级索引：`gs-comp-2025-h1-q06`, `gs-comp-2025-h1-q38`, `gs-comp-2025-h1-q70`。只表示相应 Topic 有索引样本，不证明本日子主题命中或考试频率。
- 不作“高频 / 必考 / 常考”结论。

## 记忆锚点

- 概要设计分配功能并形成结构
- 详细设计选择具体处理手段
- 界面原则：控制、减轻记忆、保持一致
- WFMS 六模块分别覆盖定义、执行、调用和监控

## 来源与证据

- `data/learning-paths/system-architect-checkin-v1.json`：`checkin-086` 的来源身份、知识点索引与 mapping。
- 用户提供的打卡归档：`2026年09月/2026-09-08 系统设计.md`；本 Prompt 区块 SHA-256 记录于 frontmatter，原文未复制。
- `docs/learning-path/SYSTEM_ARCHITECT_CHECKIN_MAPPING_AUDIT.md`：来源映射审计；mapping 不改变 Path Item identity。
- `data/golden-set/`：关联样题索引 `gs-comp-2025-h1-q06`, `gs-comp-2025-h1-q38`, `gs-comp-2025-h1-q70`；不含题干、答案或解析。
