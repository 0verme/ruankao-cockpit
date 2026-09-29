---
content_version: offline-learning-unit/v0.1
path_id: system-architect-checkin
path_version: 1.0.0
item_id: checkin-025
order: 25
title: "访问控制模型与实现技术"
source:
  date: "2026-07-02"
  file: "2026年07月/2026-07-02 安全性设计-02.md"
  prompt_sha256: ba86e5f8a2d883390c4a10967496cd80da3ad5756b56c4adb8d0a8cfe0ace8ed
mapping:
  status: split
  confidence: high
  topic_ids:
    - SEC.INFORMATION.ACCESS_CONTROL
    - SEC.ARCHITECTURE.MODELS
generation:
  mode: offline-agent
  status: draft
review_status: source_gap
---

# 访问控制模型与实现技术

## 今天学会什么
- 识别主体、客体、策略三个访问控制要素
- 区分 DAC、MAC、RBAC、TBAC、OBAC、ABAC 的授权依据
- 比较访问控制矩阵、ACL、能力表和授权关系表的表示角度

## 先建立直觉

访问控制回答主体能否对某个客体执行某种操作。模型决定依据什么授权，实现技术则决定权限关系如何存储和查询；二者不要混为一层。

## 核心知识

### 授权模型

DAC 由客体所有者自主授予；MAC 由系统按不可随意改动的安全标签和全局策略裁决；RBAC 先把权限给角色，再把用户分配角色。TBAC 随任务/工作流动态激活并回收权限；OBAC 将策略关联到被保护对象；ABAC 根据主体、客体、操作或环境属性计算策略。

### 表示与实现

访问控制矩阵以主体为行、客体为列，交叉项是操作权限。ACL 以客体为中心列出可访问主体和权限；能力表以主体为中心列出其可用能力；授权关系表用（主体、客体、权限）记录权限关系。

### 未展开的模型

原始 Prompt 只列 BLP、Biba、Chinese Wall 名称，没有给出安全目标、规则或差异；本单元不按常见教材知识补写。

**SOURCE_GAP：BLP、Biba、Chinese Wall 只有标题，缺少定义和比较规则。**

## 一张脑图式结构

```text
访问控制
├─ 模型：DAC / MAC / RBAC / TBAC / OBAC / ABAC
├─ 抽象关系：主体 × 客体 × 权限 → 矩阵
└─ 存储视角：客体中心 ACL / 主体中心能力表 / 关系表
```

## 易混点 / 对比

RBAC 通过角色间接分配权限；ABAC 按属性和策略动态判断。ACL 按客体列主体，能力表按主体列可访问对象。BLP/Biba/Chinese Wall 的差异当前为 SOURCE_GAP。

## 架构师视角

选择授权模型时要看策略依据是所有者、系统标签、角色、任务、对象还是多维属性；再选择便于管理和检查的权限表示。不要把“模型能表达什么”和“权限存在哪”当成同一决策。

## 软考关注

- 本仓库没有为该学习日细目关联章节级大纲或教材证据。
- Golden Set 主题级索引：`gs-case-2026-h1-5-q1`。只表示相应 Topic 有索引样本，不证明本日子主题命中或考试频率。
- 不作“高频 / 必考 / 常考”结论。

## 记忆锚点

- 授权三要素：主体、客体、策略
- RBAC：用户—角色—权限
- TBAC：权限跟任务阶段变化
- ACL 看客体，能力表看主体
- BLP/Biba/Chinese Wall 待补来源

## 来源与证据

- `data/learning-paths/system-architect-checkin-v1.json`：`checkin-025` 的来源身份、知识点索引与 mapping。
- 用户提供的打卡归档：`2026年07月/2026-07-02 安全性设计-02.md`；本 Prompt 区块 SHA-256 记录于 frontmatter，原文未复制。
- `docs/learning-path/SYSTEM_ARCHITECT_CHECKIN_MAPPING_AUDIT.md`：来源映射审计；mapping 不改变 Path Item identity。
- `data/golden-set/`：关联样题索引 `gs-case-2026-h1-5-q1`；不含题干、答案或解析。
