---
content_version: offline-learning-unit/v0.1
path_id: system-architect-checkin
path_version: 1.0.0
item_id: checkin-049
order: 49
title: "服务间通信：同步、异步、REST 与 gRPC"
source:
  date: "2026-07-26"
  file: "2026年07月/2026-07-26 服务间的通信.md"
  prompt_sha256: 514a3b8b70886968e2a7f024bc3f68cca1facd33678bf3b433156a5e3c26cff4
mapping:
  status: split
  confidence: high
  topic_ids:
    - ARCH.SOA.SERVICE_PROTOCOLS
    - ARCH.SOA.SERVICE_BUS
generation:
  mode: offline-agent
  status: draft
review_status: source_gap
---

# 服务间通信：同步、异步、REST 与 gRPC

## 今天学会什么
- 识别来源列出的同步/异步通信比较维度
- 说出 HTTP/REST 与 gRPC 的学习主题
- 区分 gRPC 的四种通信形态名称

## 先建立直觉

服务通信要决定调用方是否等待、消息如何表达，以及交互是一问一答还是持续流。当前 Prompt 对大部分优缺点只列标题，但明确给出 gRPC 的四类通信模式。

## 核心知识

### 通信主题

来源把同步与异步通信作为两类方式，要求比较优缺点和适用场景；HTTP/REST 部分列请求类型及 JSON/XML 对比；这些部分没有提供内容。

### gRPC 模式

来源明确列出 Unary RPC、Server-Side Streaming、Client-Side Streaming、Bidirectional Streaming 四种交互形态。其他通信语义、性能、错误处理及格式比较未在 Prompt 展开。

**SOURCE_GAP：同步/异步与 REST/gRPC 的原理、优缺点和适用场景多为标题，不能据此做协议选型。**

## 一张脑图式结构

```text
服务间通信
├─ 调用时序：同步 / 异步（细节待补）
├─ HTTP/REST：请求与表示格式（细节待补）
└─ gRPC：Unary / 服务端流 / 客户端流 / 双向流
```

## 架构师视角

通信选择会影响服务耦合、等待关系和数据交互形态。当前来源不足以比较协议优缺点，因此只保留可确认的模式名称；设计前需补齐契约、错误处理和部署约束来源。

## 软考关注

- 本仓库没有为该学习日细目关联章节级大纲或教材证据。
- Golden Set 主题级索引：`gs-comp-2024-h2-q64`, `gs-comp-2025-h1-q30`, `gs-comp-2025-h1-q36`。只表示相应 Topic 有索引样本，不证明本日子主题命中或考试频率。
- 不作“高频 / 必考 / 常考”结论。

## 记忆锚点

- 同步/异步是通信时序主题
- REST、JSON/XML 细节待补
- gRPC 四种方式按流方向区分
- 不从协议名称推断性能优劣

## 来源与证据

- `data/learning-paths/system-architect-checkin-v1.json`：`checkin-049` 的来源身份、知识点索引与 mapping。
- 用户提供的打卡归档：`2026年07月/2026-07-26 服务间的通信.md`；本 Prompt 区块 SHA-256 记录于 frontmatter，原文未复制。
- `docs/learning-path/SYSTEM_ARCHITECT_CHECKIN_MAPPING_AUDIT.md`：来源映射审计；mapping 不改变 Path Item identity。
- `data/golden-set/`：关联样题索引 `gs-comp-2024-h2-q64`, `gs-comp-2025-h1-q30`, `gs-comp-2025-h1-q36`；不含题干、答案或解析。
