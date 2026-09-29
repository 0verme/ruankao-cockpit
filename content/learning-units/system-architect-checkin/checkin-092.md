---
content_version: offline-learning-unit/v0.1
path_id: system-architect-checkin
path_version: 1.0.0
item_id: checkin-092
order: 92
title: "白盒测试：逻辑覆盖主题"
source:
  date: "2026-09-14"
  file: "2026年09月/2026-09-14 白盒测试.md"
  prompt_sha256: 491da99c0c36c99ce9c2d78ea7d5a7693543837ca0cfe7236d60028f8eaa3d68
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

# 白盒测试：逻辑覆盖主题

## 今天学会什么
- 列出来源中的白盒测试覆盖标准
- 区分语句、判定、条件和复合覆盖名称
- 识别本日定义与覆盖强度比较缺少来源

## 先建立直觉

白盒测试以程序内部逻辑作为测试设计主题。原始知识点列出了覆盖类别，但没有说明各标准要求执行哪些路径或如何确定目标。

## 核心知识

### 覆盖目录

逻辑覆盖、循环覆盖、基本路径测试；逻辑覆盖细分语句、判定、条件、判定/条件、条件组合、修改条件判断覆盖。

### 来源异常与缺口

文件主题为白盒测试，但 Prompt 顶部标题误写静态测试；映射审计已记录该不一致。各覆盖标准定义、强弱关系和设计步骤均未给出。

**SOURCE_GAP：白盒覆盖标准仅列名称，缺少判定条件与强度比较；Prompt 标题与文件主题不一致。**

## 一张脑图式结构

```text
白盒测试
├─ 逻辑覆盖：语句 / 判定 / 条件 / 判定条件
│            条件组合 / 修改条件判断
├─ 循环覆盖
└─ 基本路径测试（具体判据待补）
```

## 架构师视角

覆盖目标需要与代码逻辑和风险相匹配；如果没有标准定义，单报覆盖名称无法说明测试充分性。补充证据前不对覆盖强度排序。

## 软考关注

- 本仓库没有为该学习日细目关联章节级大纲或教材证据。
- Golden Set 主题级索引：`gs-comp-2024-h2-q55`, `gs-comp-2025-h1-q23`, `gs-comp-2025-h1-q26`。只表示相应 Topic 有索引样本，不证明本日子主题命中或考试频率。
- 不作“高频 / 必考 / 常考”结论。

## 记忆锚点

- 文件/知识点为白盒测试，Prompt 标题误写静态测试
- 覆盖分为逻辑、循环、基本路径主题
- 六种逻辑覆盖名称来自来源
- 具体判据为 SOURCE_GAP

## 来源与证据

- `data/learning-paths/system-architect-checkin-v1.json`：`checkin-092` 的来源身份、知识点索引与 mapping。
- 用户提供的打卡归档：`2026年09月/2026-09-14 白盒测试.md`；本 Prompt 区块 SHA-256 记录于 frontmatter，原文未复制。
- `docs/learning-path/SYSTEM_ARCHITECT_CHECKIN_MAPPING_AUDIT.md`：来源映射审计；mapping 不改变 Path Item identity。
- `data/golden-set/`：关联样题索引 `gs-comp-2024-h2-q55`, `gs-comp-2025-h1-q23`, `gs-comp-2025-h1-q26`；不含题干、答案或解析。
