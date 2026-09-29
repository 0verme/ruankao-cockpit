---
content_version: offline-learning-unit/v0.1
path_id: system-architect-checkin
path_version: 1.0.0
item_id: checkin-093
order: 93
title: "单元测试、覆盖标准与外部依赖"
source:
  date: "2026-09-15"
  file: "2026年09月/2026-09-15 单元测试.md"
  prompt_sha256: ae87f535827e1245435b836d379775da38d15436ea57a7d07f75da2c2019d4a6
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

# 单元测试、覆盖标准与外部依赖

## 今天学会什么
- 说明单元测试的早期反馈和重构安全网价值
- 整理覆盖标准与自动化测试主题
- 识别外部依赖替身的细节需要补充来源

## 先建立直觉

单元测试聚焦较小测试对象，来源强调尽早发现缺陷，并为修改和重构提供安全网。测试选择还需要说明覆盖目标和外部依赖如何处理。

## 核心知识

### 作用与方法

来源列出尽早发现缺陷、降低修复成本、支持修改和重构、提升可维护性。方法包括黑盒/白盒；覆盖标准有逻辑、循环、基本路径及多种逻辑覆盖。

### 自动化与依赖

Prompt 列自动化单元测试、内存数据库、Mock 技术处理外部依赖等主题，但没有说明工具、替身边界或适用条件。

**SOURCE_GAP：自动化实现和内存数据库/Mock 的选择细节没有在来源中展开。**

## 一张脑图式结构

```text
代码单元 → 自动化验证
├─ 目标：早发现缺陷、支持重构
├─ 覆盖：逻辑 / 循环 / 基本路径
└─ 外部依赖：内存数据库 / Mock（规则待补证）
```

## 架构师视角

单元测试为局部修改提供反馈，但外部依赖替代方式影响测试真实性与隔离程度。应明确测试边界和依赖责任；来源未提供具体策略，不做工具推荐。

## 软考关注

- 本仓库没有为该学习日细目关联章节级大纲或教材证据。
- Golden Set 主题级索引：`gs-comp-2024-h2-q55`, `gs-comp-2025-h1-q23`, `gs-comp-2025-h1-q26`。只表示相应 Topic 有索引样本，不证明本日子主题命中或考试频率。
- 不作“高频 / 必考 / 常考”结论。

## 记忆锚点

- 早发现缺陷、降低修复成本
- 为修改/重构提供安全网
- 覆盖标准名称需结合定义
- 内存数据库与 Mock 细节为 SOURCE_GAP

## 来源与证据

- `data/learning-paths/system-architect-checkin-v1.json`：`checkin-093` 的来源身份、知识点索引与 mapping。
- 用户提供的打卡归档：`2026年09月/2026-09-15 单元测试.md`；本 Prompt 区块 SHA-256 记录于 frontmatter，原文未复制。
- `docs/learning-path/SYSTEM_ARCHITECT_CHECKIN_MAPPING_AUDIT.md`：来源映射审计；mapping 不改变 Path Item identity。
- `data/golden-set/`：关联样题索引 `gs-comp-2024-h2-q55`, `gs-comp-2025-h1-q23`, `gs-comp-2025-h1-q26`；不含题干、答案或解析。
