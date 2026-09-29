---
content_version: offline-learning-unit/v0.1
path_id: system-architect-checkin
path_version: 1.0.0
item_id: checkin-094
order: 94
title: "集成测试：策略与集成方向"
source:
  date: "2026-09-16"
  file: "2026年09月/2026-09-16 集成测试.md"
  prompt_sha256: e6f9951e1909fb462a88e89554f984fe8c56725bb79353469086fce0044c4bd9
mapping:
  status: merge
  confidence: high
  topic_ids:
    - SOFTWARE.ENGINEERING.TESTING
generation:
  mode: offline-agent
  status: draft
review_status: source_gap
---

# 集成测试：策略与集成方向

## 今天学会什么
- 列出集成测试工作内容
- 区分一次性集成与增量集成主题
- 整理自顶向下、自底向上和三明治集成方法

## 先建立直觉

单元通过验证后，集成测试关注模块组合后能否协同工作。本日列出集成策略与方向，但原始 Prompt 没有解释各方法步骤和替代模块。

## 核心知识

### 测试工作

来源列功能、性能、安全性、可靠性测试。

### 策略与方法

策略包括一次性集成和增量集成；方法包括自顶向下、自底向上和三明治集成。对应过程、桩/驱动配置、优缺点及适用条件没有给出。

**SOURCE_GAP：集成策略与方向仅列标题，实施顺序及桩/驱动规则没有来源支持。**

## 一张脑图式结构

```text
模块单测 → 集成测试
├─ 策略：一次性 / 增量
└─ 方向：自顶向下 / 自底向上 / 三明治（步骤待补）
```

## 架构师视角

集成顺序会影响接口问题发现时间和测试支撑工作量。选择方法前需要补齐依赖结构及测试替代组件规则；当前来源仅有方法目录。

## 软考关注

- 本仓库没有为该学习日细目关联章节级大纲或教材证据。
- Golden Set 主题级索引：`gs-comp-2024-h2-q55`, `gs-comp-2025-h1-q23`, `gs-comp-2025-h1-q26`。只表示相应 Topic 有索引样本，不证明本日子主题命中或考试频率。
- 不作“高频 / 必考 / 常考”结论。

## 记忆锚点

- 工作内容含功能、性能、安全、可靠性
- 一次性与增量是策略分类
- 自顶向下/自底向上/三明治是集成方向
- 实现细节为 SOURCE_GAP

## 来源与证据

- `data/learning-paths/system-architect-checkin-v1.json`：`checkin-094` 的来源身份、知识点索引与 mapping。
- 用户提供的打卡归档：`2026年09月/2026-09-16 集成测试.md`；本 Prompt 区块 SHA-256 记录于 frontmatter，原文未复制。
- `docs/learning-path/SYSTEM_ARCHITECT_CHECKIN_MAPPING_AUDIT.md`：来源映射审计；mapping 不改变 Path Item identity。
- `data/golden-set/`：关联样题索引 `gs-comp-2024-h2-q55`, `gs-comp-2025-h1-q23`, `gs-comp-2025-h1-q26`；不含题干、答案或解析。
