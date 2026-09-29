---
content_version: offline-learning-unit/v0.1
path_id: system-architect-checkin
path_version: 1.0.0
item_id: checkin-043
order: 43
title: "边云协同：资源、数据与服务分工"
source:
  date: "2026-07-20"
  file: "2026年07月/2026-07-20 边云协同.md"
  prompt_sha256: a2bb96508c01417483210cd8f9813f68d338bee489ca2f4a518da76016531c1c
mapping:
  status: split
  confidence: medium
  topic_ids:
    - EMERGING.TECHNOLOGY.EDGE
    - EMERGING.TECHNOLOGY.CLOUD_COMPUTING
generation:
  mode: offline-agent
  status: draft
review_status: unreviewed
---

# 边云协同：资源、数据与服务分工

## 今天学会什么
- 说明边缘与云各自承担的典型工作
- 区分资源、数据、智能、应用、业务和服务协同
- 沿数据与模型反馈关系画出协作闭环

## 先建立直觉

边云协同不是把全部工作放在边缘或云，而是按实时性、范围和资源特点分工：边缘处理现场、短周期任务，云端承担全局管理、长期分析和集中训练，再把策略或模型下发。

## 核心知识

### 六类协同

资源协同：边缘本地管理资源，同时接受云端统一纳管和策略。数据协同：边缘采集、过滤和初步分析，云端持久保存并做深度分析。智能协同：云端训练模型，下发到边缘推理，难判样本可反馈形成迭代。

### 应用与业务

应用管理协同覆盖应用打包/版本分发与边缘节点启停、监控、升级、恢复。业务管理协同把云边模块编排成端到端流程，云管理业务规则，边缘执行本地模块。服务协同则按实时性、设备交互和数据量决定 SaaS 能力部署位置，并对外呈现为统一服务。

## 一张脑图式结构

```text
云端：全局资源管理 / 长周期分析 / 集中训练 / 应用与业务编排
  ↕ 策略、数据、模型和版本同步
边缘：现场采集与粗加工 / 实时决策 / 模型推理 / 本地应用执行
  └─ 难判样本与运行数据反馈云端，支持后续迭代
```

## 易混点 / 对比

资源协同管理算力等基础设施；数据协同管理数据生命周期；智能协同围绕云训练与边缘推理；应用/业务/服务协同分别关注软件生命周期、流程编排和服务能力部署。

## 架构师视角

关键是将功能按实时性、全局视角、数据量和现场依赖拆分，再定义云边之间同步什么、何时同步。边缘自治与云端统一治理之间有控制边界；来源提到的城市智慧旅游只作为案例标签，不虚构具体部署。

## 软考关注

- 本仓库没有为该学习日细目关联章节级大纲或教材证据。
- Golden Set 主题级索引：`gs-comp-2024-h1-q65`, `gs-comp-2025-h1-q48`。只表示相应 Topic 有索引样本，不证明本日子主题命中或考试频率。
- 不作“高频 / 必考 / 常考”结论。

## 记忆锚点

- 边缘负责现场和实时，云端负责全局和长周期
- 数据：边缘采集/粗加工，云端存储/深加工
- 智能：云训练、边缘推理、反馈迭代
- 应用管理、业务编排、服务部署是不同协同层

## 来源与证据

- `data/learning-paths/system-architect-checkin-v1.json`：`checkin-043` 的来源身份、知识点索引与 mapping。
- 用户提供的打卡归档：`2026年07月/2026-07-20 边云协同.md`；本 Prompt 区块 SHA-256 记录于 frontmatter，原文未复制。
- `docs/learning-path/SYSTEM_ARCHITECT_CHECKIN_MAPPING_AUDIT.md`：来源映射审计；mapping 不改变 Path Item identity。
- `data/golden-set/`：关联样题索引 `gs-comp-2024-h1-q65`, `gs-comp-2025-h1-q48`；不含题干、答案或解析。
