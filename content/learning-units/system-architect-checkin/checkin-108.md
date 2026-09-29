---
content_version: offline-learning-unit/v0.1
path_id: system-architect-checkin
path_version: 1.0.0
item_id: checkin-108
order: 108
title: "数据仓库：特征、OLAP 操作与分层"
source:
  date: "2026-10-01"
  file: "2026年10月/2026-10-01.md"
  prompt_sha256: aedcd7688e32bd3bc3ccfb1e7ef832f0782d3ecf3eeeedcdb1ea5d6350e4c258
mapping:
  status: unmapped
  confidence: low
  topic_ids: []
generation:
  mode: offline-agent
  status: draft
review_status: unreviewed
---

# 数据仓库：特征、OLAP 操作与分层

## 今天学会什么
- 说出数据仓库的四项来源定义特征
- 区分钻取、切片、切块和旋转
- 按 ODS、DWD、DWS、ADS 梳理数据加工层次

## 先建立直觉

数据仓库将异构业务数据整合成支持决策分析的数据集合；从源数据搬运、清洗规范，到聚合和面向应用服务，逐层形成可分析结果。

## 核心知识

### 定义特征

面向主题、集成、相对稳定、反映历史变化。集成过程统一命名、单位和编码并处理冲突；仓库保留历史演变以支持趋势分析。

### OLAP 操作

钻取改变维度层级，可上钻汇总或下钻细节；切片固定一个维度成员；切块在多个维度选范围；旋转改变维度排列以切换展示角度。

### 分层

ODS 接近源系统，负责同步/缓冲；DWD 清洗、规范、脱敏并开展维度建模；DWS 按主题维度聚合提高查询效率；ADS 面向应用提供高度聚合指标。

## 一张脑图式结构

```text
业务源 → ODS（同步/缓冲） → DWD（清洗/明细/建模）
→ DWS（主题聚合） → ADS（应用指标/报表）
OLAP：钻取层级 / 切片固定维度 / 切块多维范围 / 旋转视角
```

## 易混点 / 对比

切片固定一个维度成员形成子集；切块同时限制多个维度；钻取改变层级；旋转改变展示位置而不改变数据本身。

## 架构师视角

分层把源数据接入、明细治理、汇总和应用服务拆开，便于定位数据责任与查询需求。架构设计需要保持口径和历史语义连贯；本单元只按来源概述，不扩展具体仓库产品。

## 软考关注

- 本仓库没有为该学习日细目关联章节级大纲或教材证据。
- 本项 `UNMAPPED` 且无 topic_ids；未找到可关联的 Topic 样题证据，不猜测考试归属。
- 不作“高频 / 必考 / 常考”结论。

## 记忆锚点

- 数据仓库：主题、集成、稳定、历史变化
- ODS 接近源，DWD 清洗建模，DWS 聚合，ADS 服务
- 切片固定一个维度，切块选择多维范围
- 旋转改视角，不改数据

## 来源与证据

- `data/learning-paths/system-architect-checkin-v1.json`：`checkin-108` 的来源身份、知识点索引与 mapping。
- 用户提供的打卡归档：`2026年10月/2026-10-01.md`；本 Prompt 区块 SHA-256 记录于 frontmatter，原文未复制。
- `docs/learning-path/SYSTEM_ARCHITECT_CHECKIN_MAPPING_AUDIT.md`：来源映射审计；mapping 不改变 Path Item identity。
