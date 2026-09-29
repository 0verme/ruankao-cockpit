---
content_version: offline-learning-unit/v0.1
path_id: system-architect-checkin
path_version: 1.0.0
item_id: checkin-079
order: 79
title: "结构化分析：DFD 模型与平衡规则"
source:
  date: "2026-09-01"
  file: "2026年09月/2026-09-01 结构化需求分析.md"
  prompt_sha256: bcbdacd3e9ba0cea1ba2498beda679f4aa5d1b0cafcfce3b544a24f40f1bf65c
mapping:
  status: exact
  confidence: high
  topic_ids:
    - SOFTWARE.ENGINEERING.ANALYSIS_DESIGN
generation:
  mode: offline-agent
  status: draft
review_status: unreviewed
---

# 结构化分析：DFD 模型与平衡规则

## 今天学会什么
- 按自顶向下、逐层分解描述结构化分析
- 列出 DFD 的四类元素与三项平衡要求
- 区分 DFD、流程图和活动图表达的关注点

## 先建立直觉

结构化分析从系统边界开始，把功能逐层分解，并用数据流图表达数据如何进入、加工、存储和输出。图的层次必须一致，避免数据凭空产生或消失。

## 核心知识

### 模型与过程

模型包括功能、数据、行为及数据字典，来源强调数据字典为核心。过程为绘制顶层上下文图、逐层分解、定义数据字典，并按需要绘制 ER 图、状态转换图。DFD 元素是数据流、加工、数据存储、外部实体。

### DFD 平衡

父子图输入/输出流需一致；每个加工至少有输入和输出；输出数据须来自输入或加工产生。常见错误包括黑洞、奇迹、灰洞，以及外部实体绕过加工直接访问数据存储。

### 图的区别

DFD 看数据处理/存储与系统功能；流程图看控制步骤、分支和循环；活动图看活动控制流及角色协作，也能表达分支、合并和同步。

## 一张脑图式结构

```text
顶层上下文图 → 下层 DFD → 数据字典
DFD：外部实体 → 数据流 → 加工 ↔ 数据存储
检查：父子平衡 / 加工输入输出 / 数据守恒
```

## 易混点 / 对比

DFD 关注数据如何被加工与存储；流程图关注控制步骤顺序；活动图关注活动间控制流与角色协作。

## 架构师视角

DFD 可用来澄清系统边界、功能范围与数据处理责任。父子图平衡和数据守恒帮助检查需求模型是否自洽；复杂图应逐层分解而不是堆入单张图。

## 软考关注

- 本仓库没有为该学习日细目关联章节级大纲或教材证据。
- Golden Set 主题级索引：`gs-comp-2025-h1-q06`。只表示相应 Topic 有索引样本，不证明本日子主题命中或考试频率。
- 不作“高频 / 必考 / 常考”结论。

## 记忆锚点

- 结构化分析：自顶向下、逐层分解、数据驱动
- 数据字典解释图中命名元素
- DFD 三项平衡规则
- 黑洞无输出、奇迹无输入、灰洞输入不足以产生输出

## 来源与证据

- `data/learning-paths/system-architect-checkin-v1.json`：`checkin-079` 的来源身份、知识点索引与 mapping。
- 用户提供的打卡归档：`2026年09月/2026-09-01 结构化需求分析.md`；本 Prompt 区块 SHA-256 记录于 frontmatter，原文未复制。
- `docs/learning-path/SYSTEM_ARCHITECT_CHECKIN_MAPPING_AUDIT.md`：来源映射审计；mapping 不改变 Path Item identity。
- `data/golden-set/`：关联样题索引 `gs-comp-2025-h1-q06`；不含题干、答案或解析。
