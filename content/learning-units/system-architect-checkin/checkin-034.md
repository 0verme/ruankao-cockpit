---
content_version: offline-learning-unit/v0.1
path_id: system-architect-checkin
path_version: 1.0.0
item_id: checkin-034
order: 34
title: "机器学习分类与 Transformer 主题索引"
source:
  date: "2026-07-11"
  file: "2026年07月/2026-07-11 机器学习.md"
  prompt_sha256: ba03378a7a1c9df634a9b8621018d88b77898707da48fa6f5908113ea11853d5
mapping:
  status: partial
  confidence: high
  topic_ids:
    - EMERGING.TECHNOLOGY.AI
generation:
  mode: offline-agent
  status: draft
review_status: source_gap
---

# 机器学习分类与 Transformer 主题索引

## 今天学会什么
- 列举来源中的机器学习类别
- 识别 Transformer 架构是本日另一主题
- 明确各学习类别及 Transformer 结构尚未有来源定义

## 先建立直觉

原始提纲只给出机器学习类别名称和 Transformer 标题，没有进一步定义、训练信号或架构部件。可以先保留学习路线索引，不把名称直接当成完整知识解释。

## 核心知识

### 来源列出的主题

机器学习类别：监督学习、无监督学习、半监督学习、强化学习、深度学习；另列 Transformer 架构。

### SOURCE_GAP

Prompt 没有说明每种学习方式的输入/反馈差异，也没有给出 Transformer 的结构或工作方式；当前不展开推测。

**SOURCE_GAP：学习类型定义、边界及 Transformer 架构说明未出现在来源内容中。**

## 一张脑图式结构

```text
机器学习
├─ 监督 / 无监督 / 半监督
├─ 强化学习
├─ 深度学习
└─ Transformer（具体结构待补证）
```

## 架构师视角

架构师的任务不是只列算法名，而是将问题、数据和约束映射到合适方法。当前来源不足以进行这种比较；在补齐定义前不提供模型选型建议。

## 软考关注

- 本仓库没有为该学习日细目关联章节级大纲或教材证据。
- Golden Set 主题级索引：`gs-comp-2025-h1-q20`, `gs-comp-2025-h1-q47`, `gs-comp-2025-h1-q62`。只表示相应 Topic 有索引样本，不证明本日子主题命中或考试频率。
- 不作“高频 / 必考 / 常考”结论。

## 记忆锚点

- 五类名称按来源保留
- Transformer 单独列为架构主题
- 不从名称推导训练过程或网络结构
- 本单元标记 SOURCE_GAP

## 来源与证据

- `data/learning-paths/system-architect-checkin-v1.json`：`checkin-034` 的来源身份、知识点索引与 mapping。
- 用户提供的打卡归档：`2026年07月/2026-07-11 机器学习.md`；本 Prompt 区块 SHA-256 记录于 frontmatter，原文未复制。
- `docs/learning-path/SYSTEM_ARCHITECT_CHECKIN_MAPPING_AUDIT.md`：来源映射审计；mapping 不改变 Path Item identity。
- `data/golden-set/`：关联样题索引 `gs-comp-2025-h1-q20`, `gs-comp-2025-h1-q47`, `gs-comp-2025-h1-q62`；不含题干、答案或解析。
