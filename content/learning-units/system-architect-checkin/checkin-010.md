---
content_version: offline-learning-unit/v0.1
path_id: system-architect-checkin
path_version: 1.0.0
item_id: checkin-010
order: 10
title: DSSA：领域软件架构的形成
source:
  date: "2026-06-17"
  file: "2026年06月/2026-06-17.md"
  prompt_sha256: f8d1020983bf54312ca2b972b8a3c4a223314c62071433265cf84cf82f9eb1c4
mapping:
  status: partial
  confidence: medium
  topic_ids:
    - ARCH.FOUNDATION.REUSE
generation:
  mode: offline-agent
  status: draft
review_status: unreviewed
---

# DSSA：领域软件架构的形成

## 今天学会什么
- 解释 DSSA 面向特定问题领域中的一组应用，而不是单个孤立程序。
- 区分领域分析、领域设计和领域实现各自的产出目标。
- 区分领域专家与分析、设计、实现人员的职责。

## 先建立直觉

当多个应用共享同一领域中的需求和结构时，可以先沉淀共同基础，再在其上生成具体应用。DSSA（特定领域软件体系结构）就是为一组领域应用提供组织结构参考的开发基础。

## 核心知识

DSSA由领域模型、参考需求、参考体系结构等组成，目标是在特定领域中支持多个应用的生成。三个基本活动顺序为：

1. **领域分析：**取得领域模型，描述该领域系统之间的共同需求。
2. **领域设计：**依据领域模型形成 DSSA。
3. **领域实现：**根据领域模型和 DSSA 开发或组织可复用信息。

参与者包括领域专家、领域分析人员、领域设计人员和领域实现人员。专家提供领域知识；分析人员建立领域模型；设计人员据此建立 DSSA；实现人员根据模型和架构开发或提取可复用构件。

## 一张脑图式结构
```text
特定领域的一组应用
└─ 共同基础：领域模型 + 参考需求 + 参考架构
   ├─ 领域分析 → 共同需求模型
   ├─ 领域设计 → DSSA
   └─ 领域实现 → 可复用信息/构件
```

## 易混点 / 对比
- 领域模型描述共同需求；DSSA 是领域设计阶段的目标，不是领域模型的另一个名字。
- 领域实现阶段使用领域模型和 DSSA；不是只把架构文档交给开发者。
- 本项是 `PARTIAL` mapping：DSSA 与架构复用相关，但来源主题并不等同于通用复用 Topic 的全部范围。

## 架构师视角
如果多个应用确有共同领域需求，抽取共性可以形成重复使用的结构基础；但抽取边界依赖领域分析，过早把差异当共性会让参考架构失去适用性。该取舍来自“为一组应用提供基础”的目标，不代表所有同领域系统都能直接复用同一设计。

## 软考关注
仓库没有本单元对应的具体大纲段落或直接样题索引；不作频率结论。

## 记忆锚点
- DSSA 服务于一个领域中的一组应用。
- 分析得领域模型，设计得 DSSA，实现组织可复用信息。
- 专家提供领域知识，三类人员分别承担分析、设计、实现工作。

## 来源与证据
- `data/learning-paths/system-architect-checkin-v1.json`：`checkin-010` 的知识点索引、confidence 与 PARTIAL mapping。
- 用户提供的打卡归档：`2026年06月/2026-06-17.md`；Prompt 区块 SHA-256 见 frontmatter。
- `docs/learning-path/SYSTEM_ARCHITECT_CHECKIN_MAPPING_AUDIT.md`：DSSA 与架构复用 Topic 的边界说明。
