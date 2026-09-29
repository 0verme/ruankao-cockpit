---
content_version: offline-learning-unit/v0.1
path_id: system-architect-checkin
path_version: 1.0.0
item_id: checkin-040
order: 40
title: "数据挖掘与 OLAP：发现与汇总"
source:
  date: "2026-07-17"
  file: "2026年07月/2026-07-17 数据挖掘.md"
  prompt_sha256: 1370d62dd60bd3a7f15a73c6652859d9d5815fe55ca779defce8a2cfb8ff58c3
mapping:
  status: unmapped
  confidence: low
  topic_ids: []
generation:
  mode: offline-agent
  status: draft
review_status: unreviewed
---

# 数据挖掘与 OLAP：发现与汇总

## 今天学会什么
- 区分 OLAP 的已定义多维汇总与数据挖掘的模式发现
- 说明关联、序列、分类、聚类、预测和时间序列方法的基本差异
- 识别监督与无监督任务边界

## 先建立直觉

OLAP 用已知维度快速观察汇总数据；数据挖掘则尝试从数据中发现事先未明确的模式或预测关系。前者回答预先设定的分析问题，后者可能产出模型或规律。

## 核心知识

### 方法分类

关联分析寻找变量间有意义的关联；序列分析进一步考虑事件先后顺序；分类使用已标记类别样本预测离散标签；聚类没有预设标签，按对象相似性形成簇；数值预测根据历史输入和输出建模预测新数值；时间序列专门处理按时间排列的数据并利用其历史变化结构。

### 输出与用途

来源强调数据挖掘不是简单查询已知汇总，而是发现潜在规律或预测。分类/数值预测依赖已知标签或目标值；聚类寻找未标注对象间结构。

## 一张脑图式结构

```text
数据分析
├─ 预先定义问题 → OLAP：多维汇总/钻取
└─ 发现未知模式 → 数据挖掘
   ├─ 关联 / 序列（是否关注时间先后）
   ├─ 分类（有标签，离散类别）/ 预测（有数值目标）
   ├─ 聚类（无标签，按相似性分组）
   └─ 时间序列（按时间排序的数据）
```

## 易混点 / 对比

关联分析关注共同出现关系，序列分析还保留先后顺序；分类和数值预测使用已知目标，聚类不预设类别；OLAP 汇总已定义问题，数据挖掘寻找未知模式。

## 架构师视角

架构师需要先问业务要的是已知指标的切片汇总，还是从数据中发现模式/预测结果。不同目标决定数据准备、标注和分析过程；不能把一次 OLAP 查询描述成模型发现。

## 软考关注

- 本仓库没有为该学习日细目关联章节级大纲或教材证据。
- 本项 `UNMAPPED` 且无 topic_ids；未找到可关联的 Topic 样题证据，不猜测考试归属。
- 不作“高频 / 必考 / 常考”结论。

## 记忆锚点

- OLAP：已定义维度上的快速汇总与钻取
- 数据挖掘：未知模式或预测
- 序列比关联多关注事件先后
- 分类有离散标签，聚类无预设标签
- 时间序列保留时间排列

## 来源与证据

- `data/learning-paths/system-architect-checkin-v1.json`：`checkin-040` 的来源身份、知识点索引与 mapping。
- 用户提供的打卡归档：`2026年07月/2026-07-17 数据挖掘.md`；本 Prompt 区块 SHA-256 记录于 frontmatter，原文未复制。
- `docs/learning-path/SYSTEM_ARCHITECT_CHECKIN_MAPPING_AUDIT.md`：来源映射审计；mapping 不改变 Path Item identity。
