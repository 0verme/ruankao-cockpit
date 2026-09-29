---
content_version: offline-learning-unit/v0.1
path_id: system-architect-checkin
path_version: 1.0.0
item_id: checkin-033
order: 33
title: "人工智能：分类与技术目录"
source:
  date: "2026-07-10"
  file: "2026年07月/2026-07-10 人工智能.md"
  prompt_sha256: 339081e100fcc5e594f0cefa7596c4bdadfe48f2b80b97ae0cbe932bdb22676d
mapping:
  status: exact
  confidence: high
  topic_ids:
    - EMERGING.TECHNOLOGY.AI
generation:
  mode: offline-agent
  status: draft
review_status: source_gap
---

# 人工智能：分类与技术目录

## 今天学会什么
- 识别来源中的弱人工智能与强人工智能分类
- 列出 Prompt 提及的人工智能关键技术
- 区分目录索引与具备定义、比较依据的学习材料

## 先建立直觉

这份打卡把人工智能拆成概念、分类和关键技术三个部分，但只有分类和技术名称有明确列举；概念定义、分类判据和各技术作用没有展开。

## 核心知识

### 分类与技术名称

来源列出弱人工智能、强人工智能；关键技术名称包括自然语言处理、计算机视觉、知识图谱、机器学习、人机交互、虚拟现实/增强现实。

### SOURCE_GAP

Prompt 没有解释人工智能的概念边界、弱/强分类判据及各项技术的机制或关系。本单元不以常识百科补齐。

**SOURCE_GAP：概念定义、弱/强分类判据及技术之间关系均未在 Prompt 中说明。**

## 一张脑图式结构

```text
人工智能主题索引
├─ 分类：弱 / 强（定义和判据待补）
└─ 技术：NLP / CV / KG / ML / HCI / VR-AR
```

## 架构师视角

架构师需要知道技术目录与系统需求的关联，但仅有名称不足以作技术选型。应先补充定义和可验证来源，再比较具体能力、约束与系统边界。

## 软考关注

- 本仓库没有为该学习日细目关联章节级大纲或教材证据。
- Golden Set 主题级索引：`gs-comp-2025-h1-q20`, `gs-comp-2025-h1-q47`, `gs-comp-2025-h1-q62`。只表示相应 Topic 有索引样本，不证明本日子主题命中或考试频率。
- 不作“高频 / 必考 / 常考”结论。

## 记忆锚点

- 分类名称：弱人工智能、强人工智能
- 技术目录：NLP、CV、KG、ML、HCI、VR/AR
- 来源未说明定义和判据，保留 SOURCE_GAP

## 来源与证据

- `data/learning-paths/system-architect-checkin-v1.json`：`checkin-033` 的来源身份、知识点索引与 mapping。
- 用户提供的打卡归档：`2026年07月/2026-07-10 人工智能.md`；本 Prompt 区块 SHA-256 记录于 frontmatter，原文未复制。
- `docs/learning-path/SYSTEM_ARCHITECT_CHECKIN_MAPPING_AUDIT.md`：来源映射审计；mapping 不改变 Path Item identity。
- `data/golden-set/`：关联样题索引 `gs-comp-2025-h1-q20`, `gs-comp-2025-h1-q47`, `gs-comp-2025-h1-q62`；不含题干、答案或解析。
