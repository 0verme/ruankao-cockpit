---
content_version: offline-learning-unit/v0.1
path_id: system-architect-checkin
path_version: 1.0.0
item_id: checkin-041
order: 41
title: "云计算：部署与服务模式"
source:
  date: "2026-07-18"
  file: "2026年07月/2026-07-18 云计算.md"
  prompt_sha256: f5488d1f385bcaac4042bd4ef2dcad3b86aea5a7603934bf233a3a7193c5903f
mapping:
  status: exact
  confidence: high
  topic_ids:
    - EMERGING.TECHNOLOGY.CLOUD_COMPUTING
generation:
  mode: offline-agent
  status: draft
review_status: source_gap
---

# 云计算：部署与服务模式

## 今天学会什么
- 整理来源列出的云部署模式和服务模式
- 辨认 IaaS、PaaS、SaaS、FaaS、AIaaS/MaaS 名称
- 明确本来源不足以解释模式边界和责任划分

## 先建立直觉

云计算这一日提供了部署方式和服务交付方式两个分类轴，但 Prompt 只列出名称，没有定义。不能用名称本身推导谁管理哪些资源或何时选用。

## 核心知识

### 来源列出的分类

部署模式包括公有云、私有云、混合云；服务模式包括 IaaS、PaaS、SaaS、FaaS、AIaaS（MaaS）。

### SOURCE_GAP

云计算定义、各部署模式边界、服务模式的责任划分及适用场景都没有正文支持；保留术语索引，待补充证据。

**SOURCE_GAP：云计算及部署/服务模式只有标题和缩写，没有定义或责任边界。**

## 一张脑图式结构

```text
云计算
├─ 部署：公有云 / 私有云 / 混合云
└─ 服务：IaaS / PaaS / SaaS / FaaS / AIaaS(MaaS)
定义、责任边界和选型依据待补证
```

## 架构师视角

部署位置与服务抽象会影响责任边界及架构约束，但当前来源不足以支撑决策。不要仅凭缩写判断供应方与使用方分别承担什么。

## 软考关注

- 本仓库没有为该学习日细目关联章节级大纲或教材证据。
- Golden Set 主题级索引：`gs-comp-2024-h1-q65`。只表示相应 Topic 有索引样本，不证明本日子主题命中或考试频率。
- 不作“高频 / 必考 / 常考”结论。

## 记忆锚点

- 部署模式三项：公有、私有、混合
- 服务模式五项：IaaS/PaaS/SaaS/FaaS/AIaaS(MaaS)
- 定义与责任分工仍为 SOURCE_GAP

## 来源与证据

- `data/learning-paths/system-architect-checkin-v1.json`：`checkin-041` 的来源身份、知识点索引与 mapping。
- 用户提供的打卡归档：`2026年07月/2026-07-18 云计算.md`；本 Prompt 区块 SHA-256 记录于 frontmatter，原文未复制。
- `docs/learning-path/SYSTEM_ARCHITECT_CHECKIN_MAPPING_AUDIT.md`：来源映射审计；mapping 不改变 Path Item identity。
- `data/golden-set/`：关联样题索引 `gs-comp-2024-h1-q65`；不含题干、答案或解析。
