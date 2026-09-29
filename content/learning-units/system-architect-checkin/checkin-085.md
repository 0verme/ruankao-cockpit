---
content_version: offline-learning-unit/v0.1
path_id: system-architect-checkin
path_version: 1.0.0
item_id: checkin-085
order: 85
title: "需求验证：正确、完整、一致与可行"
source:
  date: "2026-09-07"
  file: "2026年09月/2026-09-07 需求验证.md"
  prompt_sha256: ee07c9c87dada1d022112e6dca662c59c15d3b6f4d9d8b5578366659146f8e93
mapping:
  status: partial
  confidence: high
  topic_ids:
    - SOFTWARE.ENGINEERING.REQUIREMENTS
generation:
  mode: offline-agent
  status: draft
review_status: unreviewed
---

# 需求验证：正确、完整、一致与可行

## 今天学会什么
- 说明需求验证在开发前确认利益相关者真实意图
- 列出需求验证的主要质量维度
- 区分评审与需求测试

## 先建立直觉

需求验证问的是“准备做的是否正确”，不是等系统写完才问软件能否运行。越早发现需求理解问题，越能避免把错误目标带入设计和测试。

## 核心知识

### 验证维度

来源列出正确性、完整性、一致性、可行性和确定性：反映真实意图、覆盖必要信息、避免文档冲突、符合技术/时间/成本/法律约束、且每条只有一种解释。

### 评审

干系人共同检查规格说明，记录问题、决定与责任人，修改后再次确认；经关键干系人确认的文档成为基线。

### 需求测试

通过可运行模型、原型、模拟或场景推演，在系统构建前动态验证复杂逻辑、交互或性能要求。

## 一张脑图式结构

```text
需求规格
├─ 检查：正确 / 完整 / 一致 / 可行 / 确定
├─ 评审：共同审查 → 问题清单 → 修改确认
└─ 测试：模型/原型/模拟/场景推演
```

## 易混点 / 对比

需求评审审查文档并形成共识；需求测试通过模型、原型或场景推演动态验证关键需求。

## 架构师视角

架构师参与评审时应检查需求是否包含影响结构的非功能约束、是否可实现且无歧义。需求验证结果为后续架构决策和测试提供共同基准。

## 软考关注

- 本仓库没有为该学习日细目关联章节级大纲或教材证据。
- Golden Set 主题级索引：`gs-comp-2025-h1-q67`。只表示相应 Topic 有索引样本，不证明本日子主题命中或考试频率。
- 不作“高频 / 必考 / 常考”结论。

## 记忆锚点

- 验证问做正确的事
- 五维：正确、完整、一致、可行、确定
- 评审形成问题跟踪与确认基线
- 需求测试在构建前用模型/原型/模拟验证

## 来源与证据

- `data/learning-paths/system-architect-checkin-v1.json`：`checkin-085` 的来源身份、知识点索引与 mapping。
- 用户提供的打卡归档：`2026年09月/2026-09-07 需求验证.md`；本 Prompt 区块 SHA-256 记录于 frontmatter，原文未复制。
- `docs/learning-path/SYSTEM_ARCHITECT_CHECKIN_MAPPING_AUDIT.md`：来源映射审计；mapping 不改变 Path Item identity。
- `data/golden-set/`：关联样题索引 `gs-comp-2025-h1-q67`；不含题干、答案或解析。
