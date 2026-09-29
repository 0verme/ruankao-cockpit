---
content_version: offline-learning-unit/v0.1
path_id: system-architect-checkin
path_version: 1.0.0
item_id: checkin-062
order: 62
title: "Kubernetes 资源类型与探针主题"
source:
  date: "2026-08-12"
  file: "2026年08月/2026-08-12 Kubernetes 资源类型.md"
  prompt_sha256: 1e19de3a5ef108d67164c37e2ce7203d7dcea80af2bc99c702f386234cc4966c
mapping:
  status: partial
  confidence: high
  topic_ids:
    - ARCH.CLOUD_NATIVE.CONTAINERS_SERVERLESS
generation:
  mode: offline-agent
  status: draft
review_status: source_gap
---

# Kubernetes 资源类型与探针主题

## 今天学会什么
- 整理 Kubernetes 提纲列出的资源对象
- 区分存活、就绪和启动探针三个名称
- 明确资源职责尚未由本日来源定义

## 先建立直觉

Kubernetes 资源清单覆盖工作负载、网络、配置与伸缩主题。当前来源只列资源名称，只有探针分出三种类型，但没有定义行为。

## 核心知识

### 资源清单

Namespace、Pod、Deployment、DaemonSet、StatefulSet、Job、CronJob、Service、Ingress、ConfigMap、Secret、HPA、VPA。

### 探针与证据缺口

Pod 部分列出存活、就绪、启动探针。Prompt 未解释它们的判断时机和失败后果，也没有说明各资源的控制器行为；避免从名称推导运行语义。

**SOURCE_GAP：各资源类型和三种探针只有名称，没有对象职责及行为定义。**

## 一张脑图式结构

```text
Kubernetes 资源索引
├─ 工作负载：Pod / Deployment / DaemonSet / StatefulSet / Job / CronJob
├─ 网络：Service / Ingress
├─ 配置：ConfigMap / Secret / Namespace
└─ 伸缩：HPA / VPA；Pod 探针：存活 / 就绪 / 启动
```

## 架构师视角

资源类型决定部署、网络、配置和伸缩的操作面，选型需要理解控制器生命周期与故障语义。当前来源仅作目录，尚不能据此提交部署配置。

## 软考关注

- 本仓库没有为该学习日细目关联章节级大纲或教材证据。
- Golden Set 主题级索引：`gs-comp-2024-h1-q65`, `gs-case-2025-h1-3-q2`, `gs-case-2026-h1-3-q2`。只表示相应 Topic 有索引样本，不证明本日子主题命中或考试频率。
- 不作“高频 / 必考 / 常考”结论。

## 记忆锚点

- 工作负载、网络、配置、伸缩资源分组便于复习
- 探针名称：存活、就绪、启动
- 具体行为为 SOURCE_GAP

## 来源与证据

- `data/learning-paths/system-architect-checkin-v1.json`：`checkin-062` 的来源身份、知识点索引与 mapping。
- 用户提供的打卡归档：`2026年08月/2026-08-12 Kubernetes 资源类型.md`；本 Prompt 区块 SHA-256 记录于 frontmatter，原文未复制。
- `docs/learning-path/SYSTEM_ARCHITECT_CHECKIN_MAPPING_AUDIT.md`：来源映射审计；mapping 不改变 Path Item identity。
- `data/golden-set/`：关联样题索引 `gs-comp-2024-h1-q65`, `gs-case-2025-h1-3-q2`, `gs-case-2026-h1-3-q2`；不含题干、答案或解析。
