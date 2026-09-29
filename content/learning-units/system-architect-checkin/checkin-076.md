---
content_version: offline-learning-unit/v0.1
path_id: system-architect-checkin
path_version: 1.0.0
item_id: checkin-076
order: 76
title: "需求工程：开发、基线与管理"
source:
  date: "2026-08-26"
  file: "2026年08月/2026-08-26 软件工程-需求工程-概述.md"
  prompt_sha256: 1cb08e80c6a651ff3edcb55126b7bf386aaa479672b3672dcf1c8a6a16395f38
mapping:
  status: exact
  confidence: high
  topic_ids:
    - SOFTWARE.ENGINEERING.REQUIREMENTS
generation:
  mode: offline-agent
  status: draft
review_status: source_gap
---

# 需求工程：开发、基线与管理

## 今天学会什么
- 整理需求工程从开发到管理的主题结构
- 区分需求开发与需求管理所含活动
- 明确本日来源没有给出术语定义和流程细节

## 先建立直觉

需求工程的提纲覆盖获取、分析、定义、验证，也覆盖基线、变更、跟踪和版本管理。前一组形成需求，后一组维护需求在项目中的状态与变化。

## 核心知识

### 目录结构

需求基线包括概念、特征和重要性；需求开发包括获取、分析、定义、验证；需求管理包括变更控制、需求跟踪、状态跟踪、版本控制。

### SOURCE_GAP

原始 Prompt 仅列标题，没有定义基线、说明活动输入输出或需求开发/管理之间的过程约束。

**SOURCE_GAP：需求基线及需求工程活动均只有标题，没有定义或流程描述。**

## 一张脑图式结构

```text
需求工程
├─ 建立需求：获取 → 分析 → 定义 → 验证
├─ 稳定基准：需求基线（定义待补）
└─ 控制变化：变更 / 跟踪 / 状态 / 版本
```

## 架构师视角

需求边界和变更记录会影响架构决策的来源与有效性。需求验证和基线治理应有明确证据链，但当前来源不足以给出流程规则。

## 软考关注

- 本仓库没有为该学习日细目关联章节级大纲或教材证据。
- Golden Set 主题级索引：`gs-comp-2025-h1-q67`。只表示相应 Topic 有索引样本，不证明本日子主题命中或考试频率。
- 不作“高频 / 必考 / 常考”结论。

## 记忆锚点

- 开发：获取、分析、定义、验证
- 管理：变更、跟踪、状态、版本
- 需求基线内容尚未解释
- mapping EXACT 不代表材料完整

## 来源与证据

- `data/learning-paths/system-architect-checkin-v1.json`：`checkin-076` 的来源身份、知识点索引与 mapping。
- 用户提供的打卡归档：`2026年08月/2026-08-26 软件工程-需求工程-概述.md`；本 Prompt 区块 SHA-256 记录于 frontmatter，原文未复制。
- `docs/learning-path/SYSTEM_ARCHITECT_CHECKIN_MAPPING_AUDIT.md`：来源映射审计；mapping 不改变 Path Item identity。
- `data/golden-set/`：关联样题索引 `gs-comp-2025-h1-q67`；不含题干、答案或解析。
