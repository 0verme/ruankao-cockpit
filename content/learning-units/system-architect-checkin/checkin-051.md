---
content_version: offline-learning-unit/v0.1
path_id: system-architect-checkin
path_version: 1.0.0
item_id: checkin-051
order: 51
title: "负载均衡类型与算法目录"
source:
  date: "2026-07-28"
  file: "2026年07月/2026-07-28 负载均衡.md"
  prompt_sha256: 2106db7ec5bcb091480b40ad808a70df4a53b6094261a2f3f14aaef1c30a2049
mapping:
  status: split
  confidence: medium
  topic_ids:
    - ARCH.COMMUNICATION.HIGH_AVAILABILITY
    - QUALITY.ATTRIBUTES.PERFORMANCE
generation:
  mode: offline-agent
  status: draft
review_status: source_gap
---

# 负载均衡类型与算法目录

## 今天学会什么
- 按静态/动态、软硬件、网络层次、部署位置和 DNS 列出负载均衡分类
- 识别来源提出的六种调度算法名称
- 明确算法适用条件当前未由来源给出

## 先建立直觉

负载均衡将请求分配到多个候选节点或服务。分类可以描述策略是否看实时状态、运行在何处或基于哪一层信息；算法标题本身不说明哪种一定最好。

## 核心知识

### 分类维度

提纲列出静态/动态、硬件/软件、四层/七层、客户端/服务端及基于 DNS 的负载均衡。它们是不同分类轴，不能合并成互斥的一组标签。

### 算法目录

轮询/加权轮询、随机/加权随机、哈希、一致性哈希、最小连接数、响应时间最短优先。来源没有给出算法流程、权重含义、节点异常处理或场景比较。

**SOURCE_GAP：负载均衡定义、算法机制和适用条件只列名称，没有解释。**

## 一张脑图式结构

```text
负载均衡
├─ 分类轴：状态 / 设备形态 / L4-L7 / 客户端-服务端 / DNS
└─ 算法：轮询 / 随机 / 哈希 / 一致性哈希 / 最小连接 / 最短响应
```

## 架构师视角

选择负载均衡方式需先明确流量入口、可观察状态、会话约束和节点健康信息。当前来源不足以比较算法或服务层次；不据名称提供架构建议。

## 软考关注

- 本仓库没有为该学习日细目关联章节级大纲或教材证据。
- Golden Set 主题级索引：`gs-comp-2025-h2-q09`, `gs-case-2020-h2-1-q1`, `gs-case-2020-h2-4-q3`。只表示相应 Topic 有索引样本，不证明本日子主题命中或考试频率。
- 不作“高频 / 必考 / 常考”结论。

## 记忆锚点

- 分类维度彼此不同，不是一组互斥选项
- 算法名称共六类
- 来源未说明权重、健康检查或适用条件
- SOURCE_GAP

## 来源与证据

- `data/learning-paths/system-architect-checkin-v1.json`：`checkin-051` 的来源身份、知识点索引与 mapping。
- 用户提供的打卡归档：`2026年07月/2026-07-28 负载均衡.md`；本 Prompt 区块 SHA-256 记录于 frontmatter，原文未复制。
- `docs/learning-path/SYSTEM_ARCHITECT_CHECKIN_MAPPING_AUDIT.md`：来源映射审计；mapping 不改变 Path Item identity。
- `data/golden-set/`：关联样题索引 `gs-comp-2025-h2-q09`, `gs-case-2020-h2-1-q1`, `gs-case-2020-h2-4-q3`；不含题干、答案或解析。
