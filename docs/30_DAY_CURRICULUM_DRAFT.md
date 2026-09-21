# 30-Day Curriculum Draft — 系统架构设计师备考工作台

> **状态**：DRAFT（Curriculum 设计草案，**不是**最终每日计划）
> **前置文档**：`docs/CONTENT_SOURCE_AUDIT.md`
> **边界**：本文件只定义 (1) 阶段设计 (2) 固定/动态边界 (3) 机器可读的任务契约 (4) 进度信号 (5) 确定性适配规则。
> 本文件**不包含** Day 1–30 的逐日任务清单，不决定技术栈，不设计 UI。
> **日期约定**：所有"Day N"均为**相对日**；绝对日期在生成时按考试日倒推绑定。

---

## 一、Curriculum Principles

原则由审计证据推导，每条附来源。

### P1 — 内容只索引，不复制
现有公开资料已覆盖教材、大纲、真题、模板（见审计第四节）。课程计划的职责是**指向**内容，不是承载内容。
→ 契约中所有任务只持有 `ref`（指针），不持有正文。

### P2 — 骨架必须锚定"三科共用节点"
【证据】"系统质量属性与架构评估" + "系统架构设计基础知识"同时是：综合知识最大分块（第三方权重 22.7%–29.3%）、案例分析 2024 起锁定的必答题、论文每场固定 1/4 的架构风格题。
→ 这两个主题在 Day 3–11 必须精读，并在 Day 12–19、Day 26–28 强制回访，不得一次性通过。

### P3 — 论文不能等到最后
【证据（反向）】希赛 30 天计划把论文练习放在 5/15–5/17（第 21–24 天）；`Altria1979` 2023 年在最后 4 天集中攻论文，案例分析 36 分未通过、论文贴线。
【证据（正向）】`wujiaming88` 12 周路线在第 3–5 周就开始"搭建 2 个可复用项目背景"。
→ 本草案把论文拆成三段：Day 3–11 **素材积累**（每天 1 张卡）→ Day 12–19 **提纲 + 首篇全文** → Day 20–28 **第二篇全文 + 素材定稿**。

### P4 — 每日必须有复习，且复习量可计算
【证据】`Zhang-986` `memoryIntervalDays()` 产生 1/3/7/15 天到期集合，欠债会累积；希赛两个计划都在每套真题后插入"错题巩固"；`wujiaming88` 冲刺周要求"只复习错题、高频卡、公式、案例模板"。
→ 复习是**唯一每天必做的固定任务**，且以 `due_card_count` 为可观测约束。

### P5 — 计划必须容纳"不学习的日子"
【证据】`Altria1979/README_2023.md` 在 22 个学习日内出现 ≥6 个休息日（10/14、10/23、10/26–10/29、11/1），并在 10/30 学到凌晨 2 点。`wujiaming88` 提供 8/14/22 小时三档投入。
→ 容量（分钟/周）是计划的第一等输入，日期不是。

### P6 — 弱项重排必须由数据触发，不由人感觉触发
【证据】`Zhang-986` 已实现 `weakModules(top5)`、`inferWeakModule()`、`byModule/byTerm/bySourceType` 三类汇总；`wujiaming88` 要求把错误分为"知识缺失/审题错误/计算错误/表达缺采分点"四类。
→ 适配规则只读 `Progress Signals`，不读主观描述。

### P7 — 真题池大于预算，因此选卷必须自适应
【证据】可用真题 = 2016下–2025下 共 36 份（`YoungHong1992`）+ 2026 上半年（`wujiaming88`）。30 天最多消化约 12–15 份。
→ 只有**固定场次的模拟套卷**（Day 20–25）按骨架锁定，其余真题由弱项信号挑选。

### P8 — 每科都要有"可交付物"，而不是"看过"
【证据】`Nye-2` 的 `课次学习计划.csv` 明确列出 `课后产出` 与 `达标标准`；`wujiaming88` 12 周路线要求"产出：知识地图、错题本、一个真实项目素材卡"。
→ 契约中的 `evidence[]` 是完成判定的唯一依据（见第四节）。

---

## 二、30-Day Phase Design

### 2.1 阶段总表

> 该结构由审计结果推导，**未采用**任务书中的示例分段（Day 1–3 / 4–10 / 11–20 / 21–27 / 28–30）。

| Phase | Day | 天数 | 名称 | 目的 | 主要证据来源 |
|---|---|---|---|---|---|
| **P0** | 1–2 | 2 | Calibration | 建立个人基线 + 错题分类法 + 选定 2 个项目背景 | `wujiaming88` 12 周路线"第 1–2 周 诊断与建框架"（压缩为 2 天） |
| **P1** | 3–11 | 9 | Core Backbone（三科主梁） | 精读共用节点 + 覆盖高权重域 + 论文素材起量 | 希赛权重表；案例必答题锁定；三色卡 🔴 清单 |
| **P2** | 12–19 | 8 | Case Capability Sprint + Essay Draft | 案例按**能力**而非年份推进；完成首篇论文全文 | 希赛 30 天"案例知识 4 天 → 真题 9 天"的结构改造；`wujiaming88` "每两周一篇全文" |
| **P3** | 20–25 | 6 | Integration & Mock | 限时整卷（综合 75 题 / 案例 90 min / 论文 120 min）× ≥2 轮 | `2026下半年备考总指南` 第 9–10 周"至少两次全流程模拟" |
| **P4** | 26–28 | 3 | Weakness Reinforcement | **由信号驱动**，无固定内容；补齐 P3 暴露的洞 | `Zhang-986` `weakModules`；希赛 5/19–5/21 错题梳理 |
| **P5** | 29–30 | 2 | Consolidation & 机考 Rehearsal | 速查/错题/素材定稿；机考系统操作演练 | `2026下半年备考总指南` 第 11–12 周；`xxlllq` 的机考指南 PDF |

合计 2 + 9 + 8 + 6 + 3 + 2 = **30 天**。

### 2.2 各阶段详细设计

#### P0 · Day 1–2：Calibration

| 维度 | 内容 |
|---|---|
| 目标 | 产出 4 个校准资产，作为后续自适应规则的初值 |
| 综合 | 做 **1 套近年真题**（不限时，允许查资料），按官方大纲 13 类归类错题（依据：`2026下半年备考总指南` "做一套近年综合知识真题，不限时，建立错题分类"） |
| 案例 | **只读不做**：读 1 套近年案例 + 4 个论文题，判断"哪一科最弱"（同上来源） |
| 论文 | 选定 **2 个项目背景**（可为工作项目），写"项目事实卡"：规模 / 技术栈 / 部署 / 量化指标（依据：`wujiaming88` "搭建 2 个可复用项目背景，不背整篇范文"） |
| 产出 | ① 知识地图（13 类初值掌握度）② 错题分类法（4 类：知识缺失/审题/计算/表达缺采分点）③ 2 张项目事实卡 ④ 每周可用时长（8 / 14 / 22 小时档） |
| 退出条件 | 4 个产出齐备；`baseline_accuracy` 已记录 |

#### P1 · Day 3–11：Core Backbone

| 维度 | 内容 |
|---|---|
| 固定锚点 | 质量属性与架构评估、架构风格（依据 P2 原则）—— 必须在 Day 3–7 内首次精读，Day 8–11 回访一次 |
| 综合 | 每日 30–50 题，按权重顺序推进：架构 → 软件工程 → 数据库 → 计算机系统基础/网络 → 安全/可靠性 → 法规/数学（依据：希赛权重排序 + `Zhang-986` module_counts） |
| 案例 | **每日 1 题**，按能力标签而不是年份（能力枚举见审计 4.2）；优先：质量属性场景 → 架构风格辨析 → 建模填图 → 数据库/缓存 |
| 论文 | **每日 1 张素材卡**（不是写全文）：把当天/历史项目的技术细节挂到"适用论题"矩阵上（模型来自 `wujiaming88/论文/素材库/万能项目素材.md` 的字段结构） |
| 复习 | 每日清到期卡片；当天错题全部进入复习队列 |
| 产出 | 13 类掌握度首轮实测；案例能力 ≥6 项各 1 题；素材卡 ≥9 张；架构风格/质量属性"能画 + 能出采分点话术" |
| 退出条件 | 素材卡 ≥9 张且 2 个项目均覆盖 ≥4 个论题；架构风格 + 质量属性达成"可复述 + 可举例" |

#### P2 · Day 12–19：Case Capability Sprint + Essay Draft

| 维度 | 内容 |
|---|---|
| 综合 | 每日 25–40 题，**按 P1 暴露的低正确率域加权**（自适应）；每周 ≥1 套限时真题 |
| 案例 | 每日 1–2 题，**按能力成簇**（缓存 / 建模 / 分布式 / 嵌入式 / 大数据 / 安全），每簇结束后写"该能力的采分点清单" |
| 论文 | Day 12–14 从素材卡生成 **2 个提纲**；Day 15–19 完成 **首篇全文**（限时 120 分钟，全文 ≥1 次完整写作；依据 P3 原则） |
| 复习 | 到期卡片 + 案例踩坑点（`common_error`）回访 |
| 产出 | 案例能力清单 ≥8 项；论文提纲 2 份；论文全文 1 篇；论文素材卡 ≥16 张 |
| 退出条件 | **首篇全文已完成**（硬约束，不可顺延到 Day 20 之后） |

#### P3 · Day 20–25：Integration & Mock

| 维度 | 内容 |
|---|---|
| 固定任务 | ≥2 轮完整模拟（每轮：综合 150 min + 案例 60–90 min + 论文 120 min）；轮次间隔 ≥2 天用于消化 |
| 综合 | 目标线 **55 分**（不是 45 分）—— 依据 `2026下半年备考总指南` "目标不是 45 分，而是稳定 55 分，给陌生新技术题留余量" |
| 案例 | 每次模拟后按 **采分点** 自评并记录 `case_score`（四类错误归因必填） |
| 论文 | 第 **2** 篇全文（限时）；对比首篇，标注"理论/实践/效果"配比是否接近 30/60/10 |
| 复习 | 保持每日到期卡片；模拟错题按 topic 聚合 |
| 产出 | 2 轮模拟成绩单；2 篇论文全文；按 topic 聚合的错题簇 |
| 退出条件 | 两轮模拟均完成；`recent_score`、`case_score`、`essay_progress` 均有值 |

#### P4 · Day 26–28：Weakness Reinforcement

| 维度 | 内容 |
|---|---|
| 内容来源 | **完全由适配规则决定**（见第六节），骨架只保留"每天仍有复习 + 每天仍有 1 个案例" |
| 综合 | 只做弱项域 + 错题重刷；不再新增知识域 |
| 案例 | 只做 `capability_accuracy` 最低的 2 个能力 |
| 论文 | 素材终稿：把 2 个项目的事实卡与论据矩阵冻结（不再新增项目） |
| 全局约束 | 若 `due_card_count` 累积 > 阈值，本阶段可整体降级为 review-only（见规则 R4） |

#### P5 · Day 29–30：Consolidation & 机考 Rehearsal

| 维度 | 内容 |
|---|---|
| 综合 | 只读速查表 / 公式卡 / 法规卡 / 英语术语卡（`wujiaming88` 冲刺周口径） |
| 案例 | 只读自查的采分点清单与六要素模板 |
| 论文 | 只读 2 份提纲 + 素材终稿；**不写新全文** |
| 必做 | **机考系统操作演练**（标记、切题、交卷、绘图、输入法；依据 `2026下半年备考总指南` 第 12 周 + `xxlllq`/`xiaomabenten` 的机考指南） |
| 禁止 | 学习新知识域（审计证据：`2026下半年备考总指南` "不再大规模学习新内容，保持作息和手感"） |

### 2.3 与现有计划的差异（说明为何不照抄）

| 差异点 | 现有计划 | 本草案 | 理由 |
|---|---|---|---|
| 基线长度 | 无（希赛直接从章节开始） | 2 天 | 没有基线就无法做弱项重排 |
| 论文时点 | 第 21–24 天（希赛 30 天） | 素材 Day 3 起 / 全文 Day 15–19 起 | `Altria1979` 2023 反向证据 |
| 案例组织 | 按年份顺序做真题 | 按**能力**成簇 | 审计 4.2 显示真考按能力分布，年份顺序会重复覆盖热点、遗漏冷点 |
| 三科关系 | 完全串行（章 → 案例 → 真题 → 论文） | 综合+案例弱并行；论文前段并行、中段独立 | `wujiaming88` 12 周"三科并进" + 串行失败案例 |
| 模拟阶段 | 无独立模拟，直接做真题 | Day 20–25 两轮全流程限时 | 三科合格线独立且不滚动，必须练"同一天三科"的体力与切换 |
| 弱项阶段 | 无（仅有"错题巩固"穿插） | Day 26–28 独立 3 天 | 需要时间窗才能生效 |
| 机考演练 | 未纳入计划 | Day 29–30 硬性 | 2023 起全面机考（`xxlllq/UpdateLog` 时间线） |

---

## 三、Fixed vs Adaptive

### 3.1 固定（Backbone，不可协商）

| # | 固定项 | 频率/时点 | 不可协商的理由 |
|---|---|---|---|
| F1 | 复习到期卡片 | **每天** | P4 原则；`Zhang-986` due 集合会累积 |
| F2 | 论文素材卡 ≥1 张 | Day 3–11 每天 | P3 原则；素材是唯一只能自产的部分 |
| F3 | 综合题量下限（≥20 题/天） | Day 3–25 | 保持手感；低于此量 `topic_accuracy` 无统计意义 |
| F4 | 至少 1 道案例 | Day 3–28（含 P4） | 案例是三科中最难短期补的（`Altria1979` 两次都是案例最低） |
| F5 | 架构风格 + 质量属性回访 | Day 3–7 首读；Day 8–11、Day 20–25、Day 26–28 各回访 | P2 原则（三科共用节点） |
| F6 | 首篇论文全文完成 | 在 Day 19 结束前 | P3 原则；这是最重要的硬里程碑 |
| F7 | ≥2 轮全流程限时模拟 | Day 20–25 | 三科不滚动保留 |
| F8 | 机考系统演练 | Day 29–30 | 2023 起全面机考 |
| F9 | 错题必须归因 4 类之一 | 每次错题时 | P6 原则；无归因的错题无法触发正确规则 |

### 3.2 动态（Adaptive，由信号决定）

| # | 动态项 | 决定者 |
|---|---|---|
| A1 | 当日综合题的**主题分布**（在下限之上） | `topic_accuracy` 排序 |
| A2 | 当日案例的**能力标签** | `capability_accuracy` 排序 |
| A3 | 是否使用真题套卷、用哪一年 | `recent_score` + `coverage` |
| A4 | 案例题量 1–3 题 | `capacity.available_minutes` |
| A5 | 某天是否降级为 review-only | `due_card_count` |
| A6 | 是否把某天改为休息日 | `capacity_actual` 连续低于计划 |
| A7 | P4 的全部内容 | 适配规则集合（第六节） |
| A8 | 论文从"提纲"推进到"全文"的具体日期 | `essay_progress` + `capacity` |

### 3.3 为什么是 `Backbone + Rolling 7-Day + Daily Adaptive`

| 层 | 解决什么 | 证据 |
|---|---|---|
| **30-Day Backbone** | 保证不可协商的锚点不被弱项重排冲掉（论文里程碑、模拟时点、机考演练） | 希赛/`Nye-2` 的失败模式：要么全固定，要么全靠人肉调整 |
| **Rolling 7-Day** | 吸收容量波动与复习欠债；给"休息日"合法位置 | `Altria1979` 真实日志有 ≥6 个休息日；`Zhang-986` 的到期集合是天然 7 日窗口 |
| **Daily Adaptive** | 把当天实际结果写回，并触发下一轮重排 | `Zhang-986` 的 attempts → weakModules → 重刷闭环 |

**三层之间的契约**：Backbone 只输出"里程碑 + 阶段"，Rolling 7-Day 只输出"未来 7 天的可调整配额"，Daily 只输出"今天做什么 + 今天记录什么"。**改编只能发生在 Rolling 与 Daily 两层**；要改 Backbone 必须显式声明（视为计划失败信号，而非日常调整）。

---

## 四、Daily Task Contract（机器可读契约）

> 本节只定义 **schema**。不填满 Day 1–30。第 4.3 节给一个 Day 8 的**示意实例**。
> 设计目标：可被确定性规则读取、可由不同 executor（人 / CLI / AI）执行、可离线存储。

### 4.1 Schema

```yaml
schema: daily-task-contract/v1

# ── 身份 ───────────────────────────────────────────────
day: <int 1..30>                  # 相对日
date: <ISO date | null>           # 绑定时填入；未绑定为 null
phase: <baseline|core-backbone|case-essay|integration|reinforcement|consolidation>
day_type: <study|review-only|mock|consolidation|rest>

# ── 容量（计划的第一等输入，见原则 P5）──────────────────
capacity:
  planned_minutes: <int>
  tier: <light|standard|intensive>      # 8h / 14h / 22h 每周档位
  hard_stop: <ISO time | null>          # 防熬夜（Altria1979 曾学到凌晨 2 点）

# ── 主题（全部使用归一化 ID，不使用中文自由文本）────────
theme:
  primary_topic_id: <string>            # 例如 sa.arch.quality-attributes
  supporting_topic_ids: [<string>]
  capability_ids: [<string>]            # 案例能力枚举，见审计 4.2

# ── 目标（可被规则覆写的配额）───────────────────────────
targets:
  comprehensive:
    question_count: <int>               # 骨架下限 20
    topic_ids: [<string>]               # 空 = 由规则按弱项填充
    source_filter: <real|mock|all>
    time_limit_min: <int | null>
  case:
    case_count: <int>                   # 1..3
    capability_ids: [<string>]
    timed: <bool>
  essay:
    material_cards: <int>               # 素材卡新增数量
    outline_sections: <int>             # 提纲完成段数
    full_draft: <bool>                  # 是否产出全文
    time_limit_min: <int | null>
  review:
    due_card_target: <int>              # 默认清空当日到期
    wrong_question_target: <int>

# ── 任务（只持有指针，不持有正文，见原则 P1）────────────
tasks:
  - id: <string>
    type: <read|drill|case|essay|review|mock|rehearsal|note>
    ref:                              # 指向来源，不内联正文
      source_repo: <string | null>
      source_path: <string | null>
      topic_id: <string | null>
      local_asset: <string | null>
    est_minutes: <int>
    required: <bool>

# ── 证据（完成判定的唯一依据，见原则 P8）─────────────────
evidence:
  - key: <string>                     # 例如 topic_accuracy.sa.db.normalization
    type: <number|boolean|enum|text>
    required: <bool>
    unit: <string | null>

# ── 完成规则（只允许读 evidence）─────────────────────────
completion_rules:
  - id: <string>
    expr: <string>                    # 例如 "comprehensive.answered >= targets.comprehensive.question_count"
    on_miss: <rollover|downgrade|log-only>

# ── 适配（当日尚未执行的下一步，由规则生成）──────────────
adaptation:
  if_weak: []                         # [rule_id, ...]
  if_strong: []
  if_overrun: []
  if_underrun: []

# ── 备注（仅供人读，不参与计算）─────────────────────────
notes: <string | null>
```

### 4.2 字段约束（硬性）

| 约束 | 规则 |
|---|---|
| `question_count` 下限 | `>= 20`（F3）；`day_type == rest` 时为 `0` |
| `case_count` 下限 | `>= 1`（F4）；`day_type ∈ {rest, consolidation}` 时可放宽 |
| `material_cards` 下限 | P1 阶段 `>= 1`（F2） |
| `topic_id` / `capability_id` | **必须**来自归一化表，禁止自由文本（否则规则无法匹配） |
| `ref` | 至少一个非空字段；禁止内联正文（版权，见审计第七节） |
| `evidence[].required == true` | 未产出则该日 `completion != done` |
| `adaptation.*` 中的元素 | 必须是已定义的 `rule_id`（第六节），不允许匿名逻辑 |

### 4.3 示意实例（Day 8，仅为格式示例，不是最终任务）

```yaml
schema: daily-task-contract/v1
day: 8
date: null
phase: core-backbone
day_type: study

capacity:
  planned_minutes: 120
  tier: standard
  hard_stop: "23:30"

theme:
  primary_topic_id: sa.arch.quality-attributes
  supporting_topic_ids: [sa.arch.styles, sa.db.normalization]
  capability_ids: [quality-attribute-scenario, architecture-style-discrimination]

targets:
  comprehensive:
    question_count: 40
    topic_ids: [sa.arch.quality-attributes, sa.arch.styles]
    source_filter: real
    time_limit_min: 45
  case:
    case_count: 1
    capability_ids: [quality-attribute-scenario]
    timed: true
  essay:
    material_cards: 1
    outline_sections: 0
    full_draft: false
    time_limit_min: null
  review:
    due_card_target: 25
    wrong_question_target: 10

tasks:
  - id: t1
    type: review
    ref: { source_repo: local, source_path: null, topic_id: null, local_asset: review_queue.json }
    est_minutes: 20
    required: true
  - id: t2
    type: drill
    ref: { source_repo: wujiaming88/awesome-ruankao, source_path: "真题/系统架构设计师/2024年下半年/综合知识.md", topic_id: sa.arch.quality-attributes, local_asset: null }
    est_minutes: 40
    required: true
  - id: t3
    type: case
    ref: { source_repo: wujiaming88/awesome-ruankao, source_path: "真题/系统架构设计师/2024年上半年/案例分析.md", topic_id: null, local_asset: null }
    est_minutes: 35
    required: true
  - id: t4
    type: note
    ref: { source_repo: self, source_path: null, topic_id: sa.arch.quality-attributes, local_asset: essay_material.json }
    est_minutes: 25
    required: true

evidence:
  - { key: "topic_accuracy.sa.arch.quality-attributes", type: number, required: true, unit: ratio }
  - { key: "case.capability.quality-attribute-scenario.score", type: number, required: true, unit: "0-1" }
  - { key: "essay.material_card.count", type: number, required: true, unit: count }
  - { key: "review.due_cleared", type: boolean, required: true, unit: null }
  - { key: "minutes.actual", type: number, required: false, unit: minutes }

completion_rules:
  - { id: cr1, expr: "review.due_cleared == true", on_miss: rollover }
  - { id: cr2, expr: "comprehensive.answered >= targets.comprehensive.question_count", on_miss: rollover }
  - { id: cr3, expr: "case.attempted >= targets.case.case_count", on_miss: log-only }
  - { id: cr4, expr: "essay.material_card.count >= targets.essay.material_cards", on_miss: log-only }

adaptation:
  if_weak: [R1, R2]
  if_strong: [R5]
  if_overrun: [R6]
  if_underrun: [R6]

notes: "质量属性进入第二次回访；若首轮正确率已 >= 0.85，交由 R5 缩短本主题时长。"
```

---

## 五、Progress Signals

Planner 允许依赖的信号。所有信号必须可离线计算（依据 `Zhang-986` 的纯函数实现风格 + `Nye-2` 的 CSV 字段）。

| Signal | 定义 | 计算来源 | 粒度 | 用于规则 |
|---|---|---|---|---|
| `baseline_accuracy` | Day 1–2 不限时真题的正确率 | 作答记录 | 全局 + 每 topic | R1, R5 |
| `recent_score` | 最近一次限时综合套卷得分（0–75） | 套卷记录 | 全局 | R2, R5 |
| `topic_accuracy` | 某 topic 的滚动正确率（建议窗口 30 题） | 作答记录按 `topic_id` 聚合（`Zhang-986` `summarizeAttempts().byModule` 的同构实现） | per-topic | R1, R2, R5 |
| `error_count` | 未消化的错题数（按 topic / 按 4 类归因） | 错题队列 | per-topic + per-cause | R1, R3 |
| `error_cause_mix` | 知识缺失 / 审题 / 计算 / 表达 的占比 | 错题归因字段（F9） | 全局 | R3 |
| `mastery` | 每个 topic 的掌握状态（`new / learning / due / mastered`） | 记忆卡片状态机（`Zhang-986` `memoryState()`：连续答对 ≥3 → mastered） | per-topic | R4, R5 |
| `due_card_count` | 当日到期卡片数 | 间隔算法（1/3/7/15 天，`memoryIntervalDays`） | 全局 | R4 |
| `coverage` | 已作答题目覆盖的 topic 比例（相对 13 类大纲 + 能力枚举） | 作答记录去重 | 全局 | R2, R5 |
| `case_score` | 案例题按采分点自评得分率（0–1） | 案例记录 | per-capability | R2, R3 |
| `capability_accuracy` | 每个案例能力的平均得分率 | 案例记录按 `capability_id` 聚合 | per-capability | R2, R3 |
| `essay_progress` | 已完成全文篇数 / 提纲数 / 素材卡数 | 论文记录 | 全局 | R5, R3 |
| `study_minutes` | 当日实际学习分钟数 | 会话记录 | 全局 | R6 |
| `completion_rate` | 近 3 日 `completion_rules` 满足比例 | 契约执行日志 | 全局 | R6 |
| `capacity_actual` | 近 7 日实际分钟数的均值与方差 | 会话记录 | 全局 | R6 |
| `streak` | 连续达标天数 | 契约执行日志 | 全局 | 仅激励，不参与重排 |

**信号优先级**（当规则冲突时）：`due_card_count` > `topic_accuracy` / `capability_accuracy` > `recent_score` > `essay_progress` > `streak`。
理由：复习欠债是不可逆的（间隔已到期），而弱项重排可以顺延一天。

---

## 六、Adaptation Rules Draft

只使用确定性规则（无 AI、无模糊推理）。每条规则可被单测覆盖。

### R1 · 弱项加权（综合）
```text
IF  topic_accuracy[topic] < 0.70  AND  sample_size[topic] >= 30
THEN 未来 3 天把该 topic 加入 targets.comprehensive.topic_ids
     且该 topic 题目数占比 >= 当日 question_count 的 40%
     并优先安排 error_count[topic] 中的错题重刷
```
依据：`Zhang-986` `summarizeAttempts().weakModules` 的阈值 ≥2 题即可排序，本规则提高到 ≥30 题以避免小样本抖动。

### R2 · 案例能力补强
```text
IF  capability_accuracy[cap] < 0.60  AND  attempts[cap] >= 2
THEN 未来 2 天 targets.case.capability_ids 只保留 [cap] 与次低者
     并要求产出该能力的 scoring_point 清单（evidence 必填）
```
依据：`wujiaming88` 案例答题模板的采分点结构。

### R3 · 论文硬里程碑保底
```text
IF  day >= 16
AND essay_progress.full_draft_count == 0
THEN 当天追加 essay.full_draft 任务（required = true）
     并把 comprehensive.question_count 下调至下限（20）
```
依据：原则 P3；反向证据为希赛 30 天把论文放到第 21–24 天。

### R4 · 复习欠债保护（最高优先级）
```text
IF  due_card_count > 60
THEN 次日 day_type = review-only
     targets.comprehensive.question_count = 0
     targets.case.case_count = 0
     仅允许 essay.material_cards >= 1 作为轻量任务
```
依据：`Zhang-986` 的 due 集合是 1/3/7/15 天机制的直接产物，欠债会指数累积；`wujiaming88` 冲刺周要求"只复习错题与高频卡"。

### R5 · 强项降配与再分配
```text
IF  recent_score >= 55
AND topic_accuracy[primary_topic_id] >= 0.85
AND 该状态连续 >= 3 天
THEN 该主题从后续 3 天的 topic_ids 中移除
     释放的时间按 60% / 40% 分给 capability_accuracy 最低的两项与 essay.full_draft
```
依据：`2026下半年备考总指南` "目标稳定 55 分"；审计结论"论文与案例是拉分项"。

### R6 · 容量校准（计划过载保护）
```text
IF  capacity_actual.mean_7d < capacity.planned_mean_7d * 0.75
AND completion_rate_3d < 0.60
THEN 把 tier 降一档（intensive → standard → light）
     下调 planned_minutes 20%
     并把未完成任务按 required 优先级重排（required 先，log-only 丢弃）
ELSE IF capacity_actual.mean_7d > planned * 1.25 AND completion_rate_3d >= 0.9
THEN 把 tier 升一档，并把增量全部给 P4 的弱项专项
```
依据：`Altria1979` 真实节奏含 ≥6 个休息日；`wujiaming88` 的三档投入（8/14/22 小时）。

### R7 · 错误归因改道（选装，验证后启用）
```text
IF  error_cause_mix["审题"] + error_cause_mix["表达缺采分点"] > 0.5
THEN 当周增加"答题表达训练"（案例分条目作答、采分点数量与分值匹配），
     而不是增加知识学习时长
ELSE IF error_cause_mix["知识缺失"] > 0.5
THEN 增加阅读时长，减少刷题量
```
依据：`wujiaming88` 要求把错误分为四类；希赛案例答题技巧要求"分条目答题，根据分值决定条目数量"。

### 规则护栏（所有规则共同遵守）

1. 任何规则**不得**改变 Backbone 里程碑（F6/F7/F8）。
2. 任何规则**不得**把 `due_card_target` 降为 0（除 `day_type == rest`）。
3. 同一 `rule_id` 连续触发不得超过 4 天，超过则升级为"计划失败"信号，需人工复核（防止规则震荡）。
4. 每条规则的触发必须写入执行日志（`rule_id`、输入信号快照、输出变更），以便复盘 —— 这是未来评估 plan 质量的数据基础。

---

## 七、尚未决定的事项（留给下一阶段）

| # | 未决问题 | 影响 | 需要什么才能决定 |
|---|---|---|---|
| 1 | `topic_id` 命名规范（是否直接用教材小节号 `2.2.2`） | 决定索引与聚合的稳定性 | 一次归一化演练（把 13 类大纲 ↔ 20 章 ↔ 三色卡 28 节 ↔ 1822 题对齐） |
| 2 | 案例 `capability` 枚举的最终粒度（当前候选 11 项） | 决定 R2 的敏感度 | 对 2016下–2026上 全部案例题打标一次 |
| 3 | 案例得分如何获得（自评 / 对照参考答案 / AI 评分） | 决定 `case_score` 可信度 | 需先有采分点清单；建议先用"采分点命中率"自评 |
| 4 | 复习算法是否停留在 1/3/7/15，还是升级为 SM-2 | 影响实现复杂度 | 先用 4 档间隔跑通 30 天，再评估 |
| 5 | 30 天是否应支持"考前不足 30 天"的压缩模式 | 决定是否需要多套 Backbone | 需要一个压缩映射表（如 14 天压缩比） |
| 6 | 休息日由用户声明还是由 R6 自动推断 | 影响计划稳定性 | 建议先声明式（Tier 输入），后自动 |
| 7 | 论文全文的"完成"判定（字数 / 三问回应 / 配比） | 影响 F6 达成判定 | 需要一篇真实草稿作为标定样本 |
| 8 | 是否把 2026 上半年新技术题（向量库/多模态测试）纳入 P1 必修 | 影响易过时内容处理 | 审计建议：仅入索引，不进正文 |

---

## 八、本草案刻意不做的事

- ❌ 未生成 Day 1–30 的逐日任务表
- ❌ 未选定技术栈、存储引擎、UI 框架
- ❌ 未复制任何第三方正文、题库、PDF
- ❌ 未引入 AI Planner（全部为确定性规则，可单测）
- ❌ 未修改任何第三方仓库
- ❌ 未把第三方"权重区间"当作官方数据（仅用于排序，且已标注两版本互相矛盾）

---

## 附录 A · 契约字段到审计证据的映射

| 契约字段 | 证据来源 |
|---|---|
| `capacity.tier` (8/14/22h) | `wujiaming88/docs/2026下半年备考总指南.md` 每周投入档位表 |
| `targets.comprehensive.question_count` 下限 20 | `Nye-2` 课次建议时长量级 + 希赛计划每日题量口径 |
| `targets.case.*` | 希赛案例答题技巧（分值决定条目数量） |
| `targets.essay.full_draft` | `wujiaming88` "每两周一篇全文" + 希赛 30 天 3 天 3 篇 |
| `targets.review.due_card_target` | `Zhang-986` `memoryIntervalDays()` |
| `evidence` 必填项 | `Nye-2` `课次学习计划.csv` 的"课后产出/达标标准" |
| `completion_rules.on_miss` | 本草案新增（现有资料无重排机制） |
| `adaptation.*` | 本草案新增（审计第七节缺口 #7） |

## 附录 B · 归一化候选（待确认，不在此冻结）

- **综合知识**：官方大纲 13 类（审计 4.1）
- **案例分析**：官方大纲 9 类（域）× 11 项能力（审计 4.2）
- **论文**：官方 5 类选题范围 × 4 题型（架构风格 / 测试质量 / 数据数据库 / 新技术）（审计 4.3）
- **教材映射**：第 2 版 20 章（`YoungHong1992/01.系统架构设计师教材-清洗版/INDEX.md`）
