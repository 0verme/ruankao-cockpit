---
content_version: offline-learning-unit/v0.1
path_id: system-architect-checkin
path_version: 1.0.0
item_id: checkin-080
order: 80
title: "E-R 数据模型与数据字典"
source:
  date: "2026-09-02"
  file: "2026年09月/2026-09-02 结构化需求分析.md"
  prompt_sha256: ce1737c0e5e33e697b8d15ea811654c7f068e905d2f7dbdb080d5362b7ae8124
mapping:
  status: partial
  confidence: high
  topic_ids:
    - SOFTWARE.ENGINEERING.ANALYSIS_DESIGN
generation:
  mode: offline-agent
  status: draft
review_status: unreviewed
---

# E-R 数据模型与数据字典

## 今天学会什么
- 列出 E-R 图的实体、属性、联系三要素
- 按局部设计、集成消冲突、消冗余梳理 E-R 流程
- 说明数据字典如何定义分析模型中的命名元素

## 先建立直觉

E-R 图组织实体及其联系；多个局部视图合并时，要处理同一事物被不同方式描述的问题。数据字典则为图中的名称提供精确解释，避免团队对字段和数据流各自理解。

## 核心知识

### E-R 建模

基本要素为实体、属性、联系；关系类型包括一对一、一对多、多对多。流程是确定需求范围、识别实体、定义联系与属性，再集成局部视图、消除属性/命名/结构冲突，最后去除冗余。

### 数据字典

在 DFD 基础上定义所有命名元素，使名字有明确解释。条目包括数据项、数据结构、数据流、数据存储、加工和外部实体；可用于沟通验证、设计开发及后续维护。

## 一张脑图式结构

```text
局部 E-R 视图 → 合并全局视图 → 消除冲突 → 去冗余
冲突：属性 / 命名 / 结构
数据字典：数据项、结构、流、存储、加工、外部实体的定义
```

## 易混点 / 对比

属性冲突是类型/格式/取值范围差异；命名冲突是同名异义或异名同义；结构冲突是抽象或组成不同。数据字典提供定义，不替代 E-R 图结构。

## 架构师视角

数据模型集成需要统一概念、命名和结构；数据字典把分析模型连接到数据库、接口与编码输入。维护定义的一致性可以减少跨团队沟通歧义。

## 软考关注

- 本仓库没有为该学习日细目关联章节级大纲或教材证据。
- Golden Set 主题级索引：`gs-comp-2025-h1-q06`。只表示相应 Topic 有索引样本，不证明本日子主题命中或考试频率。
- 不作“高频 / 必考 / 常考”结论。

## 记忆锚点

- E-R 三要素：实体、属性、联系
- 关系基数：1:1、1:N、M:N
- 先局部建模再集成消冲突
- 数据字典定义 DFD/ER 中的名称

## 来源与证据

- `data/learning-paths/system-architect-checkin-v1.json`：`checkin-080` 的来源身份、知识点索引与 mapping。
- 用户提供的打卡归档：`2026年09月/2026-09-02 结构化需求分析.md`；本 Prompt 区块 SHA-256 记录于 frontmatter，原文未复制。
- `docs/learning-path/SYSTEM_ARCHITECT_CHECKIN_MAPPING_AUDIT.md`：来源映射审计；mapping 不改变 Path Item identity。
- `data/golden-set/`：关联样题索引 `gs-comp-2025-h1-q06`；不含题干、答案或解析。
