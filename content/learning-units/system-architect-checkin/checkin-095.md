---
content_version: offline-learning-unit/v0.1
path_id: system-architect-checkin
path_version: 1.0.0
item_id: checkin-095
order: 95
title: "性能测试：负载、稳定、压力与并发"
source:
  date: "2026-09-17"
  file: "2026年09月/2026-09-17 性能测试.md"
  prompt_sha256: a863d4999a6bff6f03d94659af28c1c4383b3035078a66738221f7c610d023a8
mapping:
  status: split
  confidence: high
  topic_ids:
    - SOFTWARE.ENGINEERING.TESTING
    - QUALITY.ATTRIBUTES.PERFORMANCE
generation:
  mode: offline-agent
  status: draft
review_status: source_gap
---

# 性能测试：负载、稳定、压力与并发

## 今天学会什么
- 区分性能指标与测试目的
- 比较负载、稳定、压力、并发和强度测试
- 梳理性能测试过程和方法主题

## 先建立直觉

性能测试不是只测一个响应时间，而是在目标负载、持续运行或极限资源条件下观察系统表现，定位瓶颈并为容量规划提供依据。

## 核心知识

### 指标与目的

来源列响应时间、吞吐量、资源利用率、并发用户数、错误率；目标包括识别性能瓶颈和支撑容量规划。

### 测试类型

负载测试观察预期工作负载；稳定性测试长时间运行以发现长期问题；压力测试逐渐增加负载直至极限并关注失效/恢复；并发测试观察同时操作的竞争、死锁或数据问题；强度测试关注资源紧缺/超载下表现。流程为准备、执行、分析优化、回归。

### SOURCE_GAP

虚拟用户、WUS 方法及梯度压力策略只有名称，没有实施细节。

**SOURCE_GAP：虚拟用户/WUS 与梯度压力方法未给出步骤或工作负载模型。**

## 一张脑图式结构

```text
目标负载 → 指标观察
├─ 正常压力：负载测试
├─ 长时间：稳定性测试
├─ 接近极限：压力测试
├─ 同时操作：并发测试
└─ 资源异常：强度测试
准备 → 执行 → 分析优化 → 回归
```

## 易混点 / 对比

负载看预期工作压力，稳定性看持续时间，压力测试寻找服务极限，并发测试聚焦并发操作冲突。

## 架构师视角

测试方案应把容量目标、观测指标和失效边界对应起来。架构师可用结果定位瓶颈并验证容量假设；没有负载模型时，单个压测数字不能代表生产表现。

## 软考关注

- 本仓库没有为该学习日细目关联章节级大纲或教材证据。
- Golden Set 主题级索引：`gs-comp-2024-h2-q55`, `gs-comp-2025-h1-q23`, `gs-comp-2025-h1-q26`。只表示相应 Topic 有索引样本，不证明本日子主题命中或考试频率。
- 不作“高频 / 必考 / 常考”结论。

## 记忆锚点

- 指标：响应、吞吐、利用率、用户数、错误率
- 稳定性关注长时间运行
- 压力关注极限与失效恢复
- 并发关注竞争/死锁/一致性

## 来源与证据

- `data/learning-paths/system-architect-checkin-v1.json`：`checkin-095` 的来源身份、知识点索引与 mapping。
- 用户提供的打卡归档：`2026年09月/2026-09-17 性能测试.md`；本 Prompt 区块 SHA-256 记录于 frontmatter，原文未复制。
- `docs/learning-path/SYSTEM_ARCHITECT_CHECKIN_MAPPING_AUDIT.md`：来源映射审计；mapping 不改变 Path Item identity。
- `data/golden-set/`：关联样题索引 `gs-comp-2024-h2-q55`, `gs-comp-2025-h1-q23`, `gs-comp-2025-h1-q26`；不含题干、答案或解析。
