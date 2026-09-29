---
content_version: offline-learning-unit/v0.1
path_id: system-architect-checkin
path_version: 1.0.0
item_id: checkin-074
order: 74
title: "Lambda 与 Kappa 大数据架构"
source:
  date: "2026-08-24"
  file: "2026年08月/2026-08-24 大数据架构-架构模式.md"
  prompt_sha256: 53fd13fd880fa9f04d681ed126f19cfde370539cf9f15d84a650f84b25fd9c7e
mapping:
  status: exact
  confidence: high
  topic_ids:
    - DATA.BIGDATA.LAMBDA_KAPPA
generation:
  mode: offline-agent
  status: draft
review_status: source_gap
---

# Lambda 与 Kappa 大数据架构

## 今天学会什么
- 列出两种架构的组成层
- 比较来源记录的收益与代价
- 明确端到端数据流机制尚未有说明

## 先建立直觉

Lambda 和 Kappa 都是大数据处理架构主题，来源给出了层次组成及优缺点摘要。两者的具体处理链路在 Prompt 中没有展开。

## 核心知识

### Lambda

组成是批处理层、加速层、服务层。来源列出容错、复杂计算能力、准确性与低延迟平衡、可扩展等优点；代价包括代码维护、逻辑一致性和系统复杂度。

### Kappa

组成是流处理层、在线服务层。来源列出架构简洁、低延迟、实时性和维护成本优势；全量重算效率、复杂计算支持及对消息保留的依赖是代价。

### SOURCE_GAP

两种架构的数据流、重算方式与结果合并机制未提供，以上只按来源保留组成与评价。

**SOURCE_GAP：架构处理原理与批流结果合并机制在来源中没有展开。**

## 一张脑图式结构

```text
Lambda：批处理层 + 加速层 + 服务层
Kappa：流处理层 + 在线服务层
收益和代价按处理复杂度、延迟、维护与重算比较
```

## 易混点 / 对比

来源将 Lambda 描述为多层处理并强调复杂计算与维护成本；Kappa 层次更简洁、低延迟，但重算与复杂计算受限。机制细节仍需补证。

## 架构师视角

架构选择要权衡低延迟与计算复杂度、逻辑维护及历史重算能力。仅靠层名不足以建立实施方案，需补充数据回放和结果一致性证据。

## 软考关注

- 本仓库没有为该学习日细目关联章节级大纲或教材证据。
- 当前 Golden Set 未发现映射 Topic 的样题记录；不据此作频率判断。
- 不作“高频 / 必考 / 常考”结论。

## 记忆锚点

- Lambda 三层：批处理、加速、服务
- Kappa 两层：流处理、在线服务
- Lambda 维护与逻辑一致性成本
- Kappa 全量重算和消息保留受限

## 来源与证据

- `data/learning-paths/system-architect-checkin-v1.json`：`checkin-074` 的来源身份、知识点索引与 mapping。
- 用户提供的打卡归档：`2026年08月/2026-08-24 大数据架构-架构模式.md`；本 Prompt 区块 SHA-256 记录于 frontmatter，原文未复制。
- `docs/learning-path/SYSTEM_ARCHITECT_CHECKIN_MAPPING_AUDIT.md`：来源映射审计；mapping 不改变 Path Item identity。
