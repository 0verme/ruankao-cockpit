---
content_version: offline-learning-unit/v0.1
path_id: system-architect-checkin
path_version: 1.0.0
item_id: checkin-097
order: 97
title: "可靠性测试、混沌与故障恢复"
source:
  date: "2026-09-19"
  file: "2026年09月/2026-09-19 可靠性测试.md"
  prompt_sha256: de18f5403928f13d9bb18117d02165ea19f0ff0cfa13db39b40f86254c8d9578
mapping:
  status: split
  confidence: high
  topic_ids:
    - SOFTWARE.ENGINEERING.TESTING
    - RELIABILITY.SOFTWARE.EVALUATION
generation:
  mode: offline-agent
  status: draft
review_status: source_gap
---

# 可靠性测试、混沌与故障恢复

## 今天学会什么
- 识别可靠性测试关注的系统属性
- 列出来源提出的故障注入及恢复测试主题
- 明确混沌工程和故障注入方法尚未定义

## 先建立直觉

可靠性测试要在运行和故障条件下检查系统是否能保持或恢复可接受服务。原始 Prompt 只列出测试类型，没有说明执行方案。

## 核心知识

### 工作目录

可靠性测试概念与作用、混沌工程、故障注入技术；工作内容包括稳定性、数据一致性、容错性、备份与恢复测试。

### SOURCE_GAP

没有给出故障模型、注入范围、停止条件或恢复验收标准，因此不编造实验步骤。

**SOURCE_GAP：可靠性测试和混沌/故障注入仅有标题，执行边界与验收标准缺失。**

## 一张脑图式结构

```text
可靠性测试
├─ 稳定性
├─ 数据一致性
├─ 容错性
└─ 备份与恢复
混沌/故障注入：方法及安全边界待补来源
```

## 架构师视角

故障实验会影响真实服务，需先限定环境、故障范围和回滚/停止条件。当前来源不足以制定安全实验方案；保留测试方向而不生成操作指南。

## 软考关注

- 本仓库没有为该学习日细目关联章节级大纲或教材证据。
- Golden Set 主题级索引：`gs-comp-2024-h2-q55`, `gs-comp-2025-h1-q23`, `gs-comp-2025-h1-q26`。只表示相应 Topic 有索引样本，不证明本日子主题命中或考试频率。
- 不作“高频 / 必考 / 常考”结论。

## 记忆锚点

- 测试范围：稳定、一致、容错、备份恢复
- 混沌工程与故障注入是来源主题
- 故障实验需明确安全边界
- SOURCE_GAP

## 来源与证据

- `data/learning-paths/system-architect-checkin-v1.json`：`checkin-097` 的来源身份、知识点索引与 mapping。
- 用户提供的打卡归档：`2026年09月/2026-09-19 可靠性测试.md`；本 Prompt 区块 SHA-256 记录于 frontmatter，原文未复制。
- `docs/learning-path/SYSTEM_ARCHITECT_CHECKIN_MAPPING_AUDIT.md`：来源映射审计；mapping 不改变 Path Item identity。
- `data/golden-set/`：关联样题索引 `gs-comp-2024-h2-q55`, `gs-comp-2025-h1-q23`, `gs-comp-2025-h1-q26`；不含题干、答案或解析。
