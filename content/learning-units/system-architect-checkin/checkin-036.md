---
content_version: offline-learning-unit/v0.1
path_id: system-architect-checkin
path_version: 1.0.0
item_id: checkin-036
order: 36
title: "检索增强生成：索引、检索与生成"
source:
  date: "2026-07-13"
  file: "2026年07月/2026-07-13 检索增强生成-RAG.md"
  prompt_sha256: 76d6a82cbc0e65fc5afd287979e14292bc41527edd998de4f1aa7e2049b819ac
mapping:
  status: partial
  confidence: high
  topic_ids:
    - EMERGING.TECHNOLOGY.AI
generation:
  mode: offline-agent
  status: draft
review_status: unreviewed
---

# 检索增强生成：索引、检索与生成

## 今天学会什么
- 说出 RAG 试图弥补的两类大模型限制
- 按索引、检索、增强、生成梳理工作流
- 识别 RAG 架构中的知识库、检索、重排和生成模块

## 先建立直觉

当模型知识有时效或缺少垂直领域材料时，RAG 在回答时从外部资料中检索相关片段，再把片段与问题一起交给模型生成。它把资料检索加入生成流程，但并不自动保证答案正确。

## 核心知识

### 组件

来源列出索引模块、知识库、检索模块、重排序模块、生成模块，并举向量数据库、图数据库和其他数据源作为知识存储选项。

### 工作流程

索引阶段把上传资料分块并嵌入写入向量库；收到查询后，将查询向量化并检索 top-k 片段，可结合关键词混合检索及重排序；增强阶段把检索内容与原查询组合为上下文；生成阶段由大模型依据上下文组织回答。

### 边界

Prompt 提到预训练、微调、RAG 的比较标题但没有展开比较条件；本单元只解释有明确流程支持的 RAG 部分。检索到材料不代表材料正确或覆盖完整。

## 一张脑图式结构

```text
资料 → 分块/嵌入 → 索引与知识库
用户问题 → 检索（可混合） → 重排序 → 相关片段
                         ↓
                  问题 + 上下文 → 生成回答
```

## 易混点 / 对比

预训练、微调与 RAG 在来源中只作为比较主题；有证据支持的 RAG 机制是推理时检索外部资料并增强上下文。不能据此推导三者成本或效果排序。

## 架构师视角

RAG 的效果依赖资料更新、分块、检索、重排和生成上下文的链路质量。架构师需分别验证数据源、检索召回和答案依据；仅接入向量数据库不等于完成知识治理。

## 软考关注

- 本仓库没有为该学习日细目关联章节级大纲或教材证据。
- Golden Set 主题级索引：`gs-comp-2025-h1-q20`, `gs-comp-2025-h1-q47`, `gs-comp-2025-h1-q62`。只表示相应 Topic 有索引样本，不证明本日子主题命中或考试频率。
- 不作“高频 / 必考 / 常考”结论。

## 记忆锚点

- 问题：知识时效与垂直领域知识不足
- 流程：索引—检索—增强—生成
- 检索支持向量和关键词混合，可能再重排
- 检索命中不自动保证事实正确

## 来源与证据

- `data/learning-paths/system-architect-checkin-v1.json`：`checkin-036` 的来源身份、知识点索引与 mapping。
- 用户提供的打卡归档：`2026年07月/2026-07-13 检索增强生成-RAG.md`；本 Prompt 区块 SHA-256 记录于 frontmatter，原文未复制。
- `docs/learning-path/SYSTEM_ARCHITECT_CHECKIN_MAPPING_AUDIT.md`：来源映射审计；mapping 不改变 Path Item identity。
- `data/golden-set/`：关联样题索引 `gs-comp-2025-h1-q20`, `gs-comp-2025-h1-q47`, `gs-comp-2025-h1-q62`；不含题干、答案或解析。
