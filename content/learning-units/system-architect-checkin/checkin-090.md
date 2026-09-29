---
content_version: offline-learning-unit/v0.1
path_id: system-architect-checkin
path_version: 1.0.0
item_id: checkin-090
order: 90
title: "黑盒测试：等价类、边界与判定表"
source:
  date: "2026-09-12"
  file: "2026年09月/2026-09-12 黑盒测试.md"
  prompt_sha256: 359778497411f1e7769cac691120a7707e6f57be55cacbc71f2de2e8ecc0a2e6
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

# 黑盒测试：等价类、边界与判定表

## 今天学会什么
- 列出原始资料中的四类黑盒测试方法
- 识别每种方法的实施过程/案例内容当前缺失
- 保留黑盒方法与测试设计主题的边界

## 先建立直觉

黑盒测试方法这一日安排等价类、边界值、错误推断和判定表，但 Prompt 只给出标题，没有给出规则或样例。

## 核心知识

### 主题目录

等价类划分、边界值分析、错误推断、判定表驱动法；原始提纲为各项列出核心思想、实施过程或项目案例栏目，但没有正文。

### SOURCE_GAP

不能凭标题补出具体输入分组、测试点数量或判定表构造步骤；需补充可追踪教材/大纲证据。

**SOURCE_GAP：四种黑盒方法的定义、选点规则和项目案例均未在 Prompt 中提供。**

## 一张脑图式结构

```text
黑盒测试方法目录
├─ 等价类划分
├─ 边界值分析
├─ 错误推断
└─ 判定表驱动（规则与案例待补来源）
```

## 架构师视角

测试设计应根据需求输入和业务规则形成可解释用例。当前资料没有选点原则，不能用方法名称直接声称覆盖充分。

## 软考关注

- 本仓库没有为该学习日细目关联章节级大纲或教材证据。
- Golden Set 主题级索引：`gs-comp-2024-h2-q55`, `gs-comp-2025-h1-q23`, `gs-comp-2025-h1-q26`。只表示相应 Topic 有索引样本，不证明本日子主题命中或考试频率。
- 不作“高频 / 必考 / 常考”结论。

## 记忆锚点

- 四种方法名称按来源保留
- 方法具体选点规则未提供
- 不虚构案例
- SOURCE_GAP

## 来源与证据

- `data/learning-paths/system-architect-checkin-v1.json`：`checkin-090` 的来源身份、知识点索引与 mapping。
- 用户提供的打卡归档：`2026年09月/2026-09-12 黑盒测试.md`；本 Prompt 区块 SHA-256 记录于 frontmatter，原文未复制。
- `docs/learning-path/SYSTEM_ARCHITECT_CHECKIN_MAPPING_AUDIT.md`：来源映射审计；mapping 不改变 Path Item identity。
- `data/golden-set/`：关联样题索引 `gs-comp-2024-h2-q55`, `gs-comp-2025-h1-q23`, `gs-comp-2025-h1-q26`；不含题干、答案或解析。
