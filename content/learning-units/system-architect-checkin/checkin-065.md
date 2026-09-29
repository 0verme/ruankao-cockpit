---
content_version: offline-learning-unit/v0.1
path_id: system-architect-checkin
path_version: 1.0.0
item_id: checkin-065
order: 65
title: "消息系统：丢失、积压、顺序与重复"
source:
  date: "2026-08-15"
  file: "2026年08月/2026-08-15 消息中间件-常见问题及解决方案.md"
  prompt_sha256: 58b81ef7662316321d5ba057ece6800483680ff41090e6d5b4e2ce6e3a9b4a51
mapping:
  status: split
  confidence: medium
  topic_ids:
    - ARCH.SOA.SERVICE_BUS
    - DATA.DISTRIBUTED.CONSISTENCY
    - RELIABILITY.SOFTWARE.FAULT_TOLERANCE
generation:
  mode: offline-agent
  status: draft
review_status: source_gap
---

# 消息系统：丢失、积压、顺序与重复

## 今天学会什么
- 列出来源关注的消息可靠性问题
- 梳理发送确认、持久化、消费位移及去重等主题
- 识别具体保障强度需要结合中间件来源核验

## 先建立直觉

消息系统故障常出现在生产、存储、消费和业务事务的交界处。原始提纲列出问题类别和处理手段，但没有指定中间件、配置或完整保证。

## 核心知识

### 问题清单

消息丢失、积压、消费乱序、重复消费，以及消息发送与数据库事务原子性。

### 处理主题

提纲列生产者确认、持久化、副本写入、手动提交消费位移；优化消费逻辑或扩消费者；全局/局部有序；数据库唯一键、乐观锁、状态机、去重表；本地事件表、事务消息、本地消息表加 CDC。

### SOURCE_GAP

这些是解决策略名称，具体语义、失败窗口和适用产品未说明。不能将单一机制描述成 exactly-once 保证。

**SOURCE_GAP：所列处理方式没有机制细节、事务边界和具体中间件保证。**

## 一张脑图式结构

```text
生产 → 持久化/确认 → 消费位移 → 业务落库
风险：丢失 / 积压 / 乱序 / 重复 / 消息-数据库原子性
措施需按链路阶段匹配并验证
```

## 架构师视角

可靠消息处理要检查消息写入、位移确认和业务副作用是否一致；重试可能重复执行，扩消费者也受分区/顺序约束。当前来源只列出措施，不给保证强度。

## 软考关注

- 本仓库没有为该学习日细目关联章节级大纲或教材证据。
- Golden Set 主题级索引：`gs-comp-2024-h2-q64`, `gs-comp-2025-h1-q08`, `gs-comp-2026-h1-q34`。只表示相应 Topic 有索引样本，不证明本日子主题命中或考试频率。
- 不作“高频 / 必考 / 常考”结论。

## 记忆锚点

- 按生产、存储、消费、业务事务定位风险
- 顺序可能区分全局与局部
- 去重与消息事务是不同问题
- 不声称 exactly-once

## 来源与证据

- `data/learning-paths/system-architect-checkin-v1.json`：`checkin-065` 的来源身份、知识点索引与 mapping。
- 用户提供的打卡归档：`2026年08月/2026-08-15 消息中间件-常见问题及解决方案.md`；本 Prompt 区块 SHA-256 记录于 frontmatter，原文未复制。
- `docs/learning-path/SYSTEM_ARCHITECT_CHECKIN_MAPPING_AUDIT.md`：来源映射审计；mapping 不改变 Path Item identity。
- `data/golden-set/`：关联样题索引 `gs-comp-2024-h2-q64`, `gs-comp-2025-h1-q08`, `gs-comp-2026-h1-q34`；不含题干、答案或解析。
