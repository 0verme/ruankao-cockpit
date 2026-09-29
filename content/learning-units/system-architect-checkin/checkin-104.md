---
content_version: offline-learning-unit/v0.1
path_id: system-architect-checkin
path_version: 1.0.0
item_id: checkin-104
order: 104
title: "数据库事务：ACID、并发异常与隔离级别"
source:
  date: "2026-09-26"
  file: "2026年09月/2026-09-26 数据库事务.md"
  prompt_sha256: b00cdc021f71996dc5ef1f923892b2a06a08e8f57967ee624bfad24f27d08f30
mapping:
  status: merge
  confidence: high
  topic_ids:
    - DATA.DATABASE.TRANSACTION
generation:
  mode: offline-agent
  status: draft
review_status: source_gap
---

# 数据库事务：ACID、并发异常与隔离级别

## 今天学会什么
- 识别事务的四个 ACID 特性
- 列出脏读、不可重复读和幻读三类冲突
- 按来源列出四种隔离级别

## 先建立直觉

事务把一组数据库操作作为需要协调的工作单元；并发访问可能引入读写异常，因此需要隔离级别来表达允许的并发行为。当前 Prompt 只列出这些概念名称。

## 核心知识

### 主题目录

事务特性：原子性、一致性、隔离性、持久性；并发冲突：脏读、不可重复读、幻读；隔离级别：读未提交、读已提交、可重复读、串行化。

### SOURCE_GAP

事务定义、ACID 含义、异常例子及隔离级别对应关系未在原始材料中解释，不补写现象或保证矩阵。

**SOURCE_GAP：事务属性、并发异常及隔离级别只有标题，没有语义说明或数据库实现边界。**

## 一张脑图式结构

```text
事务
├─ 属性：A / C / I / D
├─ 并发异常：脏读 / 不可重复读 / 幻读
└─ 隔离级别：未提交 / 已提交 / 可重复读 / 串行化
对应关系待补证
```

## 架构师视角

事务隔离会影响并发控制、正确性和吞吐；选级别必须理解业务可接受的异常及数据库实现。当前来源不足以支撑具体数据库的行为结论。

## 软考关注

- 本仓库没有为该学习日细目关联章节级大纲或教材证据。
- Golden Set 主题级索引：`gs-case-2024-h1-3-q1`, `gs-case-2024-h2-2-q3`, `gs-case-2024-h1-3-q2`。只表示相应 Topic 有索引样本，不证明本日子主题命中或考试频率。
- 不作“高频 / 必考 / 常考”结论。

## 记忆锚点

- ACID 四项
- 三类并发异常名称
- 四种隔离级别名称
- 异常—级别矩阵为 SOURCE_GAP

## 来源与证据

- `data/learning-paths/system-architect-checkin-v1.json`：`checkin-104` 的来源身份、知识点索引与 mapping。
- 用户提供的打卡归档：`2026年09月/2026-09-26 数据库事务.md`；本 Prompt 区块 SHA-256 记录于 frontmatter，原文未复制。
- `docs/learning-path/SYSTEM_ARCHITECT_CHECKIN_MAPPING_AUDIT.md`：来源映射审计；mapping 不改变 Path Item identity。
- `data/golden-set/`：关联样题索引 `gs-case-2024-h1-3-q1`, `gs-case-2024-h2-2-q3`, `gs-case-2024-h1-3-q2`；不含题干、答案或解析。
