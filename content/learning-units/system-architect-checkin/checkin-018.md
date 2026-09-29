---
content_version: offline-learning-unit/v0.1
path_id: system-architect-checkin
path_version: 1.0.0
item_id: checkin-018
order: 18
title: SAAM、ATAM 与 CBAM
source:
  date: "2026-06-25"
  file: "2026年06月/2026-06-25.md"
  prompt_sha256: ee62e6edbbdf29ba0891391674e63e530bcafc08d6240179019a2e1a27a3716b
mapping:
  status: split
  confidence: high
  topic_ids:
    - QUALITY.EVALUATION.ATAM
    - QUALITY.EVALUATION.TRADEOFF
generation:
  mode: offline-agent
  status: draft
review_status: unreviewed
---

# SAAM、ATAM 与 CBAM

## 今天学会什么
- 按输入与步骤概述 SAAM 的场景分析过程。
- 说明 ATAM 关注多种质量属性及其折中，并梳理四阶段过程。
- 解释 CBAM 如何在 ATAM 结果上比较架构策略的成本与收益。

## 先建立直觉

SAAM 和 ATAM 用场景及质量属性来检查架构；CBAM 再把决策的成本收益纳入讨论。三者不是同名评估法：CBAM 使用 ATAM 的评估结果继续分析投资回报。

## 核心知识

### SAAM：以场景评估架构
来源称 SAAM 是较早形成文档并广泛应用的非功能质量属性分析方法，最初用于可修改性，也可用于可移植性、可扩充性等。输入为问题描述、需求声明和架构描述；步骤依次是场景开发、架构描述、单个场景评估、场景交互评估、总体评估。

### ATAM：分析质量属性与折中
ATAM 在 SAAM 基础上发展，来源列举性能、可用性、安全性、可修改性。活动包括收集场景和需求、架构视图与场景实现、构造并分析属性模型、折中。流程分介绍和描述、调查分析、测试、报告；调查分析阶段产生质量属性效用树，树中排列属性、场景及重要度和实现难易度优先级。

### CBAM：把成本收益加进决策
CBAM 在 ATAM 结束时开始，使用 ATAM 评估结果，分析架构决策的成本和收益，协助干系人按投资回报选择策略。

## 一张脑图式结构
```text
SAAM：场景开发 → 架构描述 → 单场景 → 场景交互 → 总体评估
   ↓ 发展
ATAM：介绍描述 → 调查分析/效用树 → 测试 → 报告
   ↓ 使用评估结果
CBAM：策略成本 + 收益 → 投资回报取舍
```

## 易混点 / 对比
- SAAM 和 ATAM 都使用架构与场景；ATAM 明确扩展到多质量属性及折中分析。
- CBAM 不是替代 ATAM；来源说它在 ATAM 结束时开始并使用其结果。
- 本单元映射至评估与权衡两个 Topic，但仍然是一个学习项。

## 架构师视角
先识别质量目标和场景，再比较架构策略，最后把成本收益放入选择过程，可使决策说明不止停留在“某方案满足某属性”。应保留场景与权重依据；来源未提供具体项目案例，因此不虚构 ROI 数字。

## 软考关注
仓库未把本单元细目绑定到大纲条目或直接样题；不作考试频率结论。

## 记忆锚点
- SAAM：场景开发、单场景、场景交互、总体评估。
- ATAM：属性效用树与折中，最后报告。
- CBAM：用 ATAM 结果分析成本、收益与 ROI。

## 来源与证据
- `data/learning-paths/system-architect-checkin-v1.json`：`checkin-018` 的知识点索引、两个 Topic IDs 与 SPLIT mapping。
- 用户提供的打卡归档：`2026年06月/2026-06-25.md`；Prompt 区块 SHA-256 见 frontmatter。
- `docs/learning-path/SYSTEM_ARCHITECT_CHECKIN_MAPPING_AUDIT.md`：该项跨架构评估和效用权衡的映射理由。
