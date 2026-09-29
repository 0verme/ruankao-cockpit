---
content_version: offline-learning-unit/v0.1
path_id: system-architect-checkin
path_version: 1.0.0
item_id: checkin-016
order: 16
title: 进程通信与事件驱动风格
source:
  date: "2026-06-23"
  file: "2026年06月/2026-06-23.md"
  prompt_sha256: fad80cf4388d9083caa20fd9017c0919d405961d89efb5502c75205286779f45
mapping:
  status: split
  confidence: high
  topic_ids:
    - ARCH.FOUNDATION.STYLES
    - ARCH.CLOUD_NATIVE.EVENT_DRIVEN
generation:
  mode: offline-agent
  status: draft
review_status: unreviewed
---

# 进程通信与事件驱动风格

## 今天学会什么
- 区分通过 RPC 直接通信与通过事件消息协作的结构。
- 说明事件生产者、事件通道和消费者的关系。
- 结合来源指出两种方式在耦合、顺序控制与一致性上的取舍。

## 先建立直觉

多个独立构件需要协作时，可以让一方直接调用另一方，也可以发布事件让感兴趣的消费者异步处理。前者交互关系直接；后者减少生产者对具体消费者的了解，但控制顺序和跟踪过程会更复杂。

## 核心知识

### 进程通信
系统由多个独立运行的构件组成，通过远程过程调用（RPC）通信。来源列出的优点包括容错性、可伸缩性和可维护性；代价包括网络通信开销、数据一致性问题及系统复杂性增加。

### 事件驱动
构件不直接进行远程调用，而通过事件消息协作。生产者向事件通道发布事件，不关心哪些消费者接收；消费者订阅感兴趣的事件，收到后异步执行逻辑。来源列出的好处是异步处理、解耦和削峰填谷；代价是复杂性增加、调试跟踪困难、放弃部分计算顺序控制，并需处理数据一致性问题。

## 一张脑图式结构
```text
独立构件协作
├─ RPC：调用方 ─请求→ 被调用方
└─ 事件驱动：生产者 → 事件通道 → 订阅者/消费者
                  （发布者不指定具体接收者）
```

## 易混点 / 对比
- RPC 表达调用方与被调用方；事件发布方表达“发生了什么”，不关心具体消费者。
- 异步可以改善响应和吞吐，但事件路径会削弱对处理顺序的直接控制。
- **SPLIT 边界：**本项既讨论一般架构风格，也涉及事件驱动架构 Topic；仍是一个 Path Item。

## 架构师视角
选择通信结构时，要同时考虑构件间耦合、网络代价、处理顺序和一致性要求。事件驱动的解耦不等于没有依赖：生产者与消费者仍需对事件语义达成约定，排查链路也需考虑跨构件过程。

## 软考关注
本仓库没有该单元细目的大纲条目或直接样题映射；不以相邻 Topic 的题目记录推断事件驱动考频。

## 记忆锚点
- RPC 看远程调用；事件风格看发布、通道、订阅。
- 生产者不指定具体消费者。
- 事件驱动换取解耦与异步，也带来顺序、跟踪和一致性成本。

## 来源与证据
- `data/learning-paths/system-architect-checkin-v1.json`：`checkin-016` 的 outline、SPLIT Topic IDs 与 confidence。
- 用户提供的打卡归档：`2026年06月/2026-06-23.md`；Prompt 区块 SHA-256 见 frontmatter。
- `docs/learning-path/SYSTEM_ARCHITECT_CHECKIN_MAPPING_AUDIT.md`：独立构件风格与事件驱动 Topic 的映射理由。
