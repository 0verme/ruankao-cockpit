---
content_version: offline-learning-unit/v0.1
path_id: system-architect-checkin
path_version: 1.0.0
item_id: checkin-047
order: 47
title: "分布式锁：数据库、Redis、ZooKeeper 与 Etcd"
source:
  date: "2026-07-24"
  file: "2026年07月/2026-07-24 分布式锁.md"
  prompt_sha256: 1c5cee3a93be0e7a1515bf2ce5d32bd8eb836dcdaf6e339681668d035f8077ad
mapping:
  status: exact
  confidence: high
  topic_ids:
    - DATA.DISTRIBUTED.DISTRIBUTED_LOCK
generation:
  mode: offline-agent
  status: draft
review_status: source_gap
---

# 分布式锁：数据库、Redis、ZooKeeper 与 Etcd

## 今天学会什么
- 比较来源给出的四类实现方案优缺点
- 按一致性、性能和组件复杂度识别取舍
- 标出具体加锁/释放机制尚未有来源说明

## 先建立直觉

分布式锁需要让多个进程协调对共享资源的访问。不同存储系统提供的协调语义、性能和依赖成本不同；不能只按吞吐选择而忽略一致性或故障行为。

## 核心知识

### 来源给出的比较

关系数据库方案实现简单、一致性强，但性能低、有单点和死锁风险且不支持重入；适合并发不高而一致性要求较高的场景。Redis 方案性能高、生态成熟，可扩展；需引入组件，并面对一致性、数据丢失和超时设置问题，适合较高并发且可容忍短期不一致的场景。

### 协调服务

ZooKeeper 方案强调一致性、规避死锁和公平锁，但引入组件、性能较低、学习成本较高；Etcd 强一致且相对 ZooKeeper 性能较高，但仍引入组件、性能相对 Redis 较低。原 Prompt 未提供各方案具体获取、续租和安全释放流程。

**SOURCE_GAP：SETNX/租约/临时节点等实现流程标题没有具体过程；锁超时和故障场景需补充技术来源。**

## 一张脑图式结构

```text
分布式锁选型
├─ 数据库：简单/一致性；性能与死锁代价
├─ Redis：性能；需评估数据丢失与超时
├─ ZooKeeper：强一致/公平；性能与运维成本
└─ Etcd：强一致、相对 ZooKeeper 较快；仍慢于 Redis（按来源描述）
```

## 易混点 / 对比

数据库与 ZooKeeper/Etcd 偏向较强一致性；Redis 偏性能。以上是来源给出的概括，具体协议保证和实现安全性仍需逐项验证。

## 架构师视角

要把锁服务故障、租约到期、进程暂停和数据恢复纳入设计；本日来源仅提供优缺点摘要，没有实现机制，不能把方案名称当作安全保证。高风险共享资源应先明确一致性要求与失效策略。

## 软考关注

- 本仓库没有为该学习日细目关联章节级大纲或教材证据。
- Golden Set 主题级索引：`gs-case-2024-h1-3-q1`, `gs-case-2024-h1-3-q2`, `gs-case-2024-h2-3-q1`。只表示相应 Topic 有索引样本，不证明本日子主题命中或考试频率。
- 不作“高频 / 必考 / 常考”结论。

## 记忆锚点

- 数据库简单但性能低，且来源指出死锁/单点风险
- Redis 性能高但需审视一致性、丢失与超时
- ZooKeeper/Etcd 强一致但有额外组件成本
- 具体实现机制仍为 SOURCE_GAP

## 来源与证据

- `data/learning-paths/system-architect-checkin-v1.json`：`checkin-047` 的来源身份、知识点索引与 mapping。
- 用户提供的打卡归档：`2026年07月/2026-07-24 分布式锁.md`；本 Prompt 区块 SHA-256 记录于 frontmatter，原文未复制。
- `docs/learning-path/SYSTEM_ARCHITECT_CHECKIN_MAPPING_AUDIT.md`：来源映射审计；mapping 不改变 Path Item identity。
- `data/golden-set/`：关联样题索引 `gs-case-2024-h1-3-q1`, `gs-case-2024-h1-3-q2`, `gs-case-2024-h2-3-q1`；不含题干、答案或解析。
