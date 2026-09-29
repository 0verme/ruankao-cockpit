---
content_version: offline-learning-unit/v0.1
path_id: system-architect-checkin
path_version: 1.0.0
item_id: checkin-103
order: 103
title: "数据库视图、触发器、锁与存储过程"
source:
  date: "2026-09-25"
  file: "2026年09月/2026-09-25 视图-触发器-锁-存储过程.md"
  prompt_sha256: 216624b8e1b992f5ba264303d17e81a07cfe84cb5747d2a3d110b6025155ddc8
mapping:
  status: split
  confidence: medium
  topic_ids:
    - DATA.DATABASE.RELATIONAL
    - DATA.DATABASE.TRANSACTION
generation:
  mode: offline-agent
  status: draft
review_status: source_gap
---

# 数据库视图、触发器、锁与存储过程

## 今天学会什么
- 说明视图、触发器和存储过程的来源定义
- 区分 BEFORE 与 AFTER 触发时机
- 识别表/行/共享/排它锁的具体语义未展开

## 先建立直觉

数据库对象既可提供逻辑访问层，也可在数据事件发生时自动执行逻辑；存储过程则把预定义 SQL 与控制流程保存在数据库中。锁主题在原提纲中仅列名称。

## 核心知识

### 视图与触发器

视图是由预定义查询定义的虚拟表，不直接存储数据；可简化查询、支持权限控制和逻辑独立性。触发器与表事件关联并自动执行；BEFORE 在操作前运行，AFTER 在操作完成后运行。

### 存储过程与锁

存储过程是预编译并存储的一组 SQL，可有参数和控制流；来源列性能、封装和减少网络开销等优点，也列移植、调试测试和服务器负担等代价。锁只列表/行、共享/排它类型，缺少语义。

**SOURCE_GAP：四种锁类型和并发/事务边界在来源中仅列名称。**

## 一张脑图式结构

```text
数据库对象
├─ 视图：查询定义的虚拟表
├─ 触发器：事件触发（BEFORE / AFTER）
├─ 存储过程：存储 SQL 与流程
└─ 锁：表/行、共享/排它（细节待补）
```

## 架构师视角

视图可形成逻辑访问面，触发器会把行为绑定到数据操作，存储过程则把逻辑放入数据库。架构师要明确逻辑所在层及其可移植/测试成本；锁的并发规则需补充来源。

## 软考关注

- 本仓库没有为该学习日细目关联章节级大纲或教材证据。
- Golden Set 主题级索引：`gs-comp-2025-h2-q08`, `gs-comp-2025-h1-q07`, `gs-comp-2025-h1-q33`。只表示相应 Topic 有索引样本，不证明本日子主题命中或考试频率。
- 不作“高频 / 必考 / 常考”结论。

## 记忆锚点

- 视图本身不存数据
- BEFORE 在数据操作前，AFTER 在成功操作后
- 存储过程封装预存 SQL
- 锁类型仅列名，SOURCE_GAP

## 来源与证据

- `data/learning-paths/system-architect-checkin-v1.json`：`checkin-103` 的来源身份、知识点索引与 mapping。
- 用户提供的打卡归档：`2026年09月/2026-09-25 视图-触发器-锁-存储过程.md`；本 Prompt 区块 SHA-256 记录于 frontmatter，原文未复制。
- `docs/learning-path/SYSTEM_ARCHITECT_CHECKIN_MAPPING_AUDIT.md`：来源映射审计；mapping 不改变 Path Item identity。
- `data/golden-set/`：关联样题索引 `gs-comp-2025-h2-q08`, `gs-comp-2025-h1-q07`, `gs-comp-2025-h1-q33`；不含题干、答案或解析。
