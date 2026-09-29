---
content_version: offline-learning-unit/v0.1
path_id: system-architect-checkin
path_version: 1.0.0
item_id: checkin-032
order: 32
title: "可观测性：指标、日志与链路追踪"
source:
  date: "2026-07-09"
  file: "2026年07月/2026-07-09 可观测性设计.md"
  prompt_sha256: 99f9064b3b592822aa60959e51a852b540e2c80bbe101e9bdab67d55a1de73f6
mapping:
  status: unmapped
  confidence: low
  topic_ids: []
generation:
  mode: offline-agent
  status: draft
review_status: source_gap
---

# 可观测性：指标、日志与链路追踪

## 今天学会什么
- 识别来源列出的三大可观测性支柱
- 区分 Counter、Gauge、Histogram、Summary 这四类指标名称
- 知道当前资料未说明的工具职责与指标语义需要补证

## 先建立直觉

可观测性关注从系统输出了解内部运行状态。原始 Prompt 列出指标、日志、链路追踪及一组工具名称，但没有给出三类数据的定义、采集方式或工具职责。

## 核心知识

### 来源列出的目录

三大支柱为指标、日志、链路追踪；指标类型名称包括 Counter、Gauge、Histogram、Summary。工具清单包括 Prometheus、Grafana、AlertManager、ELK Stack、Jaeger、SkyWalking、OpenTelemetry。

### SOURCE_GAP

Prompt 没有解释四类指标的数值语义，也没有说明日志字段、Trace/Span 关系或所列工具分工。本单元只保留目录索引，不按工具名称推断功能。

**SOURCE_GAP：三类支柱定义、四种指标语义及工具职责在来源中只有标题/名称，没有说明。**

## 一张脑图式结构

```text
可观测性（待补定义）
├─ Metrics：Counter / Gauge / Histogram / Summary
├─ Logs
├─ Traces
└─ 工具索引：Prometheus / Grafana / AlertManager / ELK / Jaeger / SkyWalking / OpenTelemetry
```

## 架构师视角

架构设计需要把可观测性作为跨组件的数据产出与诊断问题处理，但当前来源不足以制定指标标签、日志字段或追踪传播规范。补充证据前不把具体工具清单当成完整方案。

## 软考关注

- 本仓库没有为该学习日细目关联章节级大纲或教材证据。
- 本项 `UNMAPPED` 且无 topic_ids；未找到可关联的 Topic 样题证据，不猜测考试归属。
- 不作“高频 / 必考 / 常考”结论。

## 记忆锚点

- 三大支柱：指标、日志、链路追踪
- 指标列出 Counter、Gauge、Histogram、Summary
- 工具名不等于职责说明
- 本单元为 SOURCE_GAP

## 来源与证据

- `data/learning-paths/system-architect-checkin-v1.json`：`checkin-032` 的来源身份、知识点索引与 mapping。
- 用户提供的打卡归档：`2026年07月/2026-07-09 可观测性设计.md`；本 Prompt 区块 SHA-256 记录于 frontmatter，原文未复制。
- `docs/learning-path/SYSTEM_ARCHITECT_CHECKIN_MAPPING_AUDIT.md`：来源映射审计；mapping 不改变 Path Item identity。
