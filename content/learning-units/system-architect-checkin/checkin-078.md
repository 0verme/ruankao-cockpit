---
content_version: offline-learning-unit/v0.1
path_id: system-architect-checkin
path_version: 1.0.0
item_id: checkin-078
order: 78
title: "CAP、BASE 与分布式事务方案索引"
source:
  date: "2026-08-28"
  file: "2026年08月/2026-08-28 分布式事务.md"
  prompt_sha256: 2b7cb9f2f899182c8f171115322041226c111bb08681a0b45c4a4ee1495ada06
mapping:
  status: split
  confidence: high
  topic_ids:
    - DATA.DISTRIBUTED.CONSISTENCY
    - DATA.DATABASE.TRANSACTION
    - ARCH.SOA.SERVICE_BUS
generation:
  mode: offline-agent
  status: draft
review_status: source_gap
---

# CAP、BASE 与分布式事务方案索引

## 今天学会什么
- 列出 Prompt 规划的理论与事务方案
- 识别两阶段提交、TCC、Saga 等比较栏目
- 明确本日没有给出理论定义和方案权衡依据

## 先建立直觉

跨多个节点更新数据时，需要处理可用性、状态一致性和失败恢复。原始提纲列出 CAP、BASE 及多种事务方案，但没有说明理论或协议过程。

## 核心知识

### 主题目录

CAP 理论、BASE 理论；2PC、TCC、Saga、基于消息中间件的最终一致性、最大努力通知。每种方案原本计划讨论原理、优缺点，但内容为空。

### SOURCE_GAP

不能只凭缩写推断参与者状态、补偿动作、阻塞行为或一致性保证；这些需要明确来源。

**SOURCE_GAP：CAP/BASE 定义及五种分布式事务方案的原理与优缺点都缺失。**

## 一张脑图式结构

```text
分布式事务
├─ 理论索引：CAP / BASE
└─ 方案索引：2PC / TCC / Saga / 消息最终一致 / 最大努力通知
协议细节与保证待补来源
```

## 架构师视角

事务方案要与业务补偿能力、失败时可见状态和跨服务参与范围匹配。当前材料不支持方案优劣或一致性承诺，不能用模式名替代故障流程设计。

## 软考关注

- 本仓库没有为该学习日细目关联章节级大纲或教材证据。
- Golden Set 主题级索引：`gs-comp-2024-h2-q64`, `gs-case-2024-h1-3-q1`, `gs-case-2024-h2-2-q3`。只表示相应 Topic 有索引样本，不证明本日子主题命中或考试频率。
- 不作“高频 / 必考 / 常考”结论。

## 记忆锚点

- 两类理论：CAP、BASE
- 方案：2PC、TCC、Saga、消息最终一致、最大努力通知
- 缩写不等于完整协议
- SOURCE_GAP

## 来源与证据

- `data/learning-paths/system-architect-checkin-v1.json`：`checkin-078` 的来源身份、知识点索引与 mapping。
- 用户提供的打卡归档：`2026年08月/2026-08-28 分布式事务.md`；本 Prompt 区块 SHA-256 记录于 frontmatter，原文未复制。
- `docs/learning-path/SYSTEM_ARCHITECT_CHECKIN_MAPPING_AUDIT.md`：来源映射审计；mapping 不改变 Path Item identity。
- `data/golden-set/`：关联样题索引 `gs-comp-2024-h2-q64`, `gs-case-2024-h1-3-q1`, `gs-case-2024-h2-2-q3`；不含题干、答案或解析。
