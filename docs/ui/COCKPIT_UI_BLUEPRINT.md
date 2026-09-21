# Cockpit UI Blueprint v0.1

> **状态**：PLANNING CONTRACT（Issue #5 · UI.1 / UI.2）
> **上游**：`README.md`、`AGENTS.md`、`data/progress/schema.json`、`engine/progress/README.md`、`engine/rules/README.md`
> **边界**：本文件冻结产品目标、UX 原则、信息架构与 Dashboard 卡片数据语义；**不实现任何 UI**。

---

## 1. Product Goal

Cockpit 是整条 `Progress Events → Replay → Mastery/Review → Planner → Cockpit` 链路的最终消费面。它必须让用户每天打开后立刻知道：**今天该做什么、为什么做、做完后发生什么**。

Cockpit 必须能回答四个核心问题：

| # | 问题 | 主要承载位置 | 当前可完整回答？ |
|---|---|---|---|
| Q1 | 我现在准备得怎么样？ | `OverallProgressCard`、`SubjectStatusGrid` | 🟡 部分（综合 / 案例可用；论文不可用） |
| Q2 | 我今天应该做什么？ | `TodayFocusCard` | ❌ 依赖 Planner contract |
| Q3 | 哪些内容需要复习？ | `ReviewQueue` / `DueBadge` | ❌ 依赖 Issue #4 |
| Q4 | 离目标还有多远？ | `ExamCountdown`、Coverage、Assessment | 🟡 倒计时可用（User Config）；目标达成度依赖 assessment contract |

### 1.1 验收目标

| # | 目标 | 验收方式 |
|---|---|---|
| G1 | 首屏回答四个核心问题 | 每张 Dashboard 卡片都能对应一个明确问题 |
| G2 | 只消费真实 domain output | 每个指标都有 domain source，或在映射表中明确标记 `Future` / `user_config` |
| G3 | 解释性优先 | 状态与任务可展开「为什么」，且原因来自 engine 输出 |
| G4 | 保持领域语义隔离 | Knowledge Topic ≠ Case Capability；accuracy ≠ mastery |
| G5 | 诚实表达无数据 | `null` / `insufficient_evidence` 显示为「未评估 / 证据不足」，不显示 0，也不显示假分数 |
| G6 | 桌面高信息密度 + 移动可用 | Desktop 三栏 / Tablet 两栏 / Mobile 单栏 Today-first |
| G7 | 可审计 | Read Model 可派生、可缓存、可重建，不成为新事实源 |

### 1.2 明确不是

```text
题库平台
论文编辑器
AI tutor
资源商城
社区
营销官网 / Landing Page
深色科技大屏
账号 / 权限 / 云同步系统
```

---

## 2. UX Principles

| # | 原则 | 含义 | 违反示例 |
|---|---|---|---|
| UX1 | **Fact-first** | UI 只渲染 domain output；不推算 accuracy / mastery / review_due / plan completion | 前端把「连续答对 3 题」自行判为 `mastered` |
| UX2 | **Today-first** | 首屏最重要的问题是「今天做什么」；移动端尤其如此 | 移动端首屏是一张巨大的统计圆环 |
| UX3 | **Explainability first-class** | 任何状态与推荐都必须能展开原因链，而不是只有一个数字 | 只显示「今天复习 12 项」而无到期原因 |
| UX4 | **语义隔离** | Knowledge Topic 与 Case Capability 在 UI 层仍是两个维度，禁止合并成一个百分比 | 三科压成一个「掌握度 N%」式模型 |
| UX5 | **Honest null** | 无数据 = 未评估 / 证据不足（中性灰），不等于失败（红），也不等于 0 分 | `accuracy = null` 渲染为 `0%` |
| UX6 | **Draft ≠ Contract** | 课程草案、参考截图、示例数字不得成为 UI 数据来源 | 把 `docs/30_DAY_CURRICULUM_DRAFT.md` 的 Day 表硬编码进页面 |
| UX7 | **Explicit as_of** | 若「刷新」实际是 deterministic replay，必须显示为「重放至 as_of = …」并展示 replay 版本；UI 不得隐式使用系统当前时间决定事实 | 静默用 `now()` 决定「今天到期」 |
| UX8 | **Progressive Disclosure** | 用户层只显示友好标签；工程字段（policy version、transition reason、evidence、版本元数据）放在 Explain 层 | 首屏显示 `review-policy/v0.1` |
| UX9 | **Dense but Calm** | 高信息密度、轻边框、克制用色；不做彩色卡片堆叠 | 每张卡不同底色 + 巨型数字 |
| UX10 | **No Premature System** | 不做 Design System 工程化；只冻结 design direction、语义色与组件边界 | 本轮产出 token package / 主题引擎 |
| UX11 | **No UI-side ordering** | 队列排序、优先级、next due 全部来自 engine | 前端按「看起来更合理」重排复习队列 |
| UX12 | **Two independent dimensions** | mastery status 与 scheduling status 分层渲染，不强行合成单一互斥枚举 | 一个 badge 同时表示「已掌握」和「已逾期」 |

---

## 3. Information Architecture

### 3.1 总体骨架

```text
AppShell
├─ TopHeader
│  ├─ ExamDirectionLabel        # 当前考试方向（User Config）
│  ├─ PlanModeSwitcher          # 7 / 14 / 30 天（Planner 依赖 → 未冻结前不渲染）
│  └─ ReplayControl             # 显式 as_of + replay version
├─ ContextStrip                 # 高频全局上下文（白名单字段）
└─ PrimaryNav                   # 一级导航

Dashboard（默认路由 `/`）
├─ 左栏：整体备考状态
│  └─ OverallProgressCard
├─ 中栏：今日行动中心（首屏最重要）
│  └─ TodayFocusCard
└─ 右栏：运营统计与时间约束
   ├─ OperationalStatsGrid
   ├─ ExamCountdown
   ├─ StudyCalendar
   └─ SubjectStatusGrid
```

### 3.2 TopHeader

```text
产品名：软考高级备考 Cockpit
当前考试方向：<User Configuration，不硬编码>
当前计划 / 冲刺阶段：<Planner 输出；未冻结时显示空态>
```

右侧控件（规划，不实现）：

| 控件 | 依赖 | 未冻结时的行为 |
|---|---|---|
| 计划视图切换（7 / 14 / 30 天） | Planner 输出 | 不渲染（不是显示假数据） |
| 导入 / 导出 | 事件写路径 | 不渲染 |
| 重放（Replay，显式 `as_of`） | Progress replay（Gate A 已 PASS） | 可渲染；必须显示 `as_of` 与 `replay_rule_version` |
| 设置 | User Configuration | 指向 `/settings` |

**重放语义冻结**：

```text
重放至 as_of = <timestamp>
replay_rule_version = progress-replay/v0.1
```

UI 不得把重放表述为无参数的「刷新」，也不得让「今天」由浏览器本地时间隐式决定；日历日边界必须显式携带 timezone。

### 3.3 ContextStrip

只保留高频全局上下文。**白名单**（其余字段一律不放）：

| 字段 | 来源分类 | 展示语义 |
|---|---|---|
| 考试方向 | user_config | 值本身 |
| 科目 | user_config | 值本身 |
| 每日可用时间 | user_config（未来可由 Planner 校准） | 值本身 + 「配置」标记 |
| 及格线 / 目标 | user_config | **必须标注「目标 / 参考」，不是 domain 事实** |
| 当前策略 / 版本 | aggregate（replay 元数据） | Progressive disclosure：折叠显示 |

**禁止**把 Context Strip 变成信息垃圾带：低频、装饰性、没有消费方的字段不进入。

### 3.4 PrimaryNav

| 入口 | user job | 状态 |
|---|---|---|
| 今日 | 我今天做什么 | MVP 入口（内容依赖 Planner） |
| 计划 | 我的 30 天安排是什么 | Later（依赖 Planner） |
| 综合 | 我综合知识练得怎么样 / 去练习 | Later |
| 案例 | 我的案例能力弱在哪 / 去练习 | Later |
| 论文 | 我的论文准备到哪一步 | Future（无 essay contract） |
| 复习 | 今天哪些内容需要复习 | MVP（数据依赖 Issue #4） |
| 资源 | 内容从哪里来 | Later（只索引 / 引用） |

**规则**：没有明确 user job 的入口不建。

### 3.5 Dashboard 三栏职责

| 栏位 | 职责 | 回答的问题 |
|---|---|---|
| 左栏 | 整体备考状态（Overall Readiness / Progress） | Q1 我现在准备得怎么样 |
| 中栏 | Today / 今日行动中心 | Q2 我今天应该做什么 |
| 右栏 | Operational Stats + Exam Countdown + Study Calendar + Subject Status | Q1 / Q3 / Q4 的支撑证据与时间约束 |

---

## 4. Dashboard Blueprint

以下六张卡片为本轮**冻结的 Dashboard 组成**。每张卡片都必须声明：

```text
user question / available fields / future fields / empty state
unavailable state / data source / explain behavior
```

**通用约束**（适用于全部卡片）：

```text
1. UI 只渲染 view-model；卡片不直接读取 domain object graph
2. 任何字段都必须能在 DOMAIN_TO_UI_MAPPING.md 中找到一条映射
3. 没有 domain source 的字段不得渲染
4. 无数据 → 显式 empty / insufficient / unavailable 状态，禁止默认 0
5. 禁止为了卡片对称而编造同构数据模型（三科尤其如此）
```

---

### 4.1 OverallProgressCard

| 项 | 内容 |
|---|---|
| **user question** | 我现在准备得怎么样？ |
| **data source** | `progress-state/v0.1` aggregate + projection |
| **source category** | `aggregate`（综合 / 案例） + `future`（论文） |
| **implementation gate** | 综合 / 案例部分：Gate A ✅；论文部分：Gate 之外，长期 `unavailable` |
| **explain behavior** | 每个维度可展开到 `ProgressSummaryView` 的明细；版本元数据走 `PolicyVersionFooter` |

**available fields（当前可用）**

| 维度 | 字段 | 来源 |
|---|---|---|
| 综合知识 | `global.attempt_count` / `global.correct_count` / `global.incorrect_count` / `global.accuracy` | `progress-state/v0.1` |
| 综合知识 | `coverage.l1/l2/l3.ratio` | `progress-state/v0.1` |
| 综合知识 | `errors.error_count` / `errors.error_count_by_cause` | `progress-state/v0.1` |
| 案例分析 | `case.attempt_count` / `case.scored_attempt_count` / `case.score_ratio` | `progress-state/v0.1` |
| 案例分析 | `capabilities[*].score_ratio` / `capabilities[*].evidence_status` | `progress-state/v0.1` |
| 元数据 | `schema_version` / `replay_rule_version` / `taxonomy_version` / `capability_version` | `progress-state/v0.1` |

**future fields（当前不可用）**

| 维度 | 字段 | 依赖 | 标记 |
|---|---|---|---|
| 论文 | outline readiness / material coverage / practice status / assessment | essay contract | `TBD — essay contract 未冻结` |
| 三科 | mastery / 掌握度 | P4.3 / P4.4 已冻结枚举与字段名；需 P4.5 replay | `TBD — dependent on P4.5 replay` |
| 三科 | 目标达成度（离及格线多远） | assessment contract | `TBD — assessment contract 未冻结` |

**维度可用性矩阵（冻结，禁止补齐成同构）**

| 维度 | 可消费 | 当前状态 |
|---|---|---|
| 综合知识 | `global.accuracy` 系列、`topics[*].accuracy`、`coverage.*`、`errors.*` | Available |
| 案例分析 | `case.score_ratio`（加权）、`capabilities[*].score_ratio` + `evidence_status` | Available（**不是 75 分制，不是 exam score**） |
| 论文 | 无 | **Future / unavailable**，显示「尚未建立契约」 |

**empty state**

```text
未评估 —— 尚无综合题作答事件（accuracy = null）
```

显示条件：`global.attempt_count = 0` 且 `case.attempt_count = 0`。
禁止把 `accuracy = null` 渲染为 `0%`；禁止显示任何占位百分比。

**unavailable state**

```text
论文维度：PaperUnavailableBadge →「尚未建立契约」
```

不允许显示 `0/75`、`—/75` 或任何形似分数的占位。

**解释链示例**

```text
综合正确率
→ global.correct_count / global.attempt_count
→ 事件集合（as_of 之前）
→ replay_rule_version = progress-replay/v0.1
→ taxonomy_version / capability_version
```

---

### 4.2 TodayFocusCard

| 项 | 内容 |
|---|---|
| **user question** | 我今天应该做什么？ |
| **data source** | Planner 输出（**未冻结**）+ Review 输出（Issue #4，**未冻结**） |
| **source category** | `planner` + `phase4` |
| **implementation gate** | Gate C（Planner）+ Gate B（Review） |
| **explain behavior** | 展开后显示触发的 rule id、输入信号快照、plan / policy version（未来字段，契约未冻结） |

**当前正式状态（必须冻结）**

```text
TodayFocusCard 的唯一合法当前状态 = EmptyState:
  「Planner contract 尚未冻结」
```

理由：Planner contract 不存在，UI 不得自行推算任务，也不得从 `docs/30_DAY_CURRICULUM_DRAFT.md` 复制任务。

**available fields（当前可用）**

| 字段 | 来源 | 说明 |
|---|---|---|
| 无 | — | Today 的正式任务字段**当前全部不可用** |

**future fields（依赖 Planner contract，字段名与枚举均为 TBD）**

```text
Today Plan / day_index / plan_phase / day_type         TBD — dependent on Planner contract
theme.primary_topic_id / supporting_topic_ids / capability_ids   TBD — dependent on Planner contract
capacity.planned_minutes / capacity.tier               TBD — dependent on Planner contract
tasks[].id / type / ref / est_minutes / required       TBD — dependent on Planner contract
plan_version / policy version                          TBD — dependent on Planner contract
cta_target                                             TBD — dependent on Planner contract
```

**future fields（依赖 Issue #4）**

```text
review.due_count        ✅ 字段名与语义已冻结（unit = review_item）
                        —— 但仍需 P4.5 replay 才能取值
review.overdue_count    ✅ 字段名已冻结；需 P4.5 replay
review.next_due_at      ✅ 字段名与粒度已冻结；需 P4.5 replay
```

**empty state**

```text
无今日计划：Planner contract 尚未冻结
```

**unavailable state**

| 子区域 | 不可用原因 | 表达 |
|---|---|---|
| 今日任务列表 | Planner contract 未冻结 | `UnavailableBadge` →「契约未冻结」 |
| 到期复习入口 | P4.5 replay 未实现 | `UnavailableBadge` →「依赖 Mastery / Review replay（P4.5）」 |

**硬约束**

```text
1. UI 不得自己生成、拆分、补全或重排任务
2. UI 不得硬编码 Day 1..30
3. UI 不得从课程草案推导「今天该做什么」
4. 「开始今日学习」CTA 在没有 plan 时不得指向伪造的任务流
```

---

### 4.3 OperationalStatsGrid

| 项 | 内容 |
|---|---|
| **user question** | 我的整体运营统计是什么？（时长 / 覆盖 / 错题 / 复习债务） |
| **data source** | `progress-state/v0.1` aggregate（部分 tile）+ Issue #4（部分 tile）+ 未定义 contract（部分 tile） |
| **source category** | `aggregate` + `phase4` + `future` |
| **implementation gate** | Available tile 可渲染；`phase4` / `future` tile 必须显示 `UnavailableBadge` |
| **explain behavior** | 每个 tile 必须声明 data source；可展开到对应明细视图 |

**tile 冻结表**

| tile | 候选指标 | 分类 | 可消费字段 | 当前状态 |
|---|---|---|---|---|
| T1 | 累计学习时长 | `aggregate` | `study.study_minutes` | ✅ Available |
| T2 | 学习会话数 | `aggregate` | `study.session_count` | ✅ Available |
| T3 | 综合正确率 | `aggregate` | `global.accuracy`（分母 0 → `null`） | ✅ Available |
| T4 | 知识覆盖 | `aggregate` | `coverage.l1/l2/l3.ratio`（分母 = taxonomy 全量节点） | ✅ Available |
| T5 | 错题数 / 归因分布 | `aggregate` | `errors.error_count` / `errors.error_count_by_cause` / `errors.unclassified_error_count` | ✅ Available |
| T6 | 案例加权得分率 | `aggregate` | `case.score_ratio`（加权 earned/possible） | ✅ Available |
| T7 | 今日到期复习数 | `phase4` | `due_count`（unit = review_item） | 🟡 字段名已冻结；`TBD — dependent on P4.5 replay` |
| T8 | mastery 分布 | `phase4` | `new_count` / `learning_count` / `mastered_count` | 🟡 字段名已冻结；`TBD — dependent on P4.5 replay` |
| T9 | 计划完成度 | `future` | task execution contract | ⏳ 未冻结 |
| T10 | 近期 assessment | `future` | assessment contract | ⏳ 未冻结 |
| T11 | 连续学习天数 | `future` | 无 contract | ⏳ **禁止由 UI 推断** |

**empty state**

```text
未评估 —— 分母为 0 时显示「尚无数据」，不显示 0
```

**unavailable state**

```text
T7 / T8  → UnavailableBadge（依赖 Mastery / Review replay，P4.5）
T9 / T10 / T11 → UnavailableBadge（契约未定义）
```

**约束**

```text
1. 每个 tile 必须有可见来源声明（tooltip / footer / explain）
2. coverage 的分母是 taxonomy 节点数，不是「考试权重覆盖」
   → tile 文案必须避免「考纲覆盖率」式误导
3. study_minutes 只表示测量到的时长，不表示学习质量、专注度或效率
4. streak 不得由 UI 用事件时间戳自行推断
```

---

### 4.4 ExamCountdown

| 项 | 内容 |
|---|---|
| **user question** | 离目标考试还有多久？ |
| **data source** | User Configuration（`exam_date`） + 显式 timezone + 显式 `as_of` |
| **source category** | `user_config`（剩余天数由 projection 计算） |
| **implementation gate** | Gate 0（无领域依赖）；但**剩余天数必须使用显式 `as_of` 与 timezone** |
| **explain behavior** | 展开显示 `exam_date`、timezone、`as_of`、日历日边界规则 |

**available fields**

| 字段 | 来源 | 说明 |
|---|---|---|
| `exam_date` | user_config | 用户配置，不是 domain 输出 |
| `days_remaining` | projection | 由 `exam_date`、`as_of`、timezone 计算 |
| `timezone` | user_config | 日历日边界依据 |

**future fields**

| 字段 | 依赖 | 标记 |
|---|---|---|
| `plan_phase` / 冲刺阶段 | Planner | `TBD — dependent on Planner contract` |
| `milestone` / 里程碑 | Planner | `TBD — dependent on Planner contract` |

**empty state**

```text
未配置考试日期 —— 请前往设置
```

**unavailable state**

```text
冲刺阶段：UnavailableBadge（依赖 Planner contract）
```

**硬约束**

```text
1. UI Contract 不得硬编码任何具体考试日期
2. 不得使用浏览器本地时间隐式计算剩余天数
3. 剩余天数是 projection，不是 domain 事实，不得写回 domain
```

---

### 4.5 StudyCalendar

| 项 | 内容 |
|---|---|
| **user question** | 我这些天有没有学习 / 有没有复习债务 / 有没有模拟？ |
| **data source** | 事件聚合（`occurred_at`）+ Issue #4（due / overdue）+ assessment contract（未来） |
| **source category** | `aggregate` + `phase4` + `future` |
| **implementation gate** | 「有学习记录」：Gate A ✅；「复习 due / overdue」：Gate B；「Assessment」「完成日」：未解锁 |
| **explain behavior** | 点击某一天展开当天的事实来源（事件类型、计数、`as_of`） |

**Calendar 只承载四类语义（冻结）**

| 语义 | 来源 | 当前状态 |
|---|---|---|
| 有学习记录（有事件） | immutable progress events | ✅ Available |
| 完成日（task execution） | task execution contract | ❌ Future |
| Review due / overdue | Issue #4（P4.4 规则已冻结；需 P4.5 replay） | 🟡 `TBD — dependent on P4.5 replay` |
| Assessment | assessment contract | ❌ Future |

**Legend 草案**

```text
○  有学习记录
●  已完成                  （Future — task execution contract）
!  有逾期复习              （Phase 4 — P4.4 规则已冻结，需 P4.5 replay）
△  有 Assessment           （Future — assessment contract）
```

**关键约束（冻结）**

```text
有学习事件 != 完成学习
```

在学习完成契约存在之前，Calendar **只能**显示「有学习记录」，不得显示「已完成 / 打卡成功」，也不得显示连续达标天数。

**empty state**

```text
本月无学习记录
```

**unavailable state**

```text
! 与 △ 图例项在依赖冻结前不渲染（不是渲染成灰色图例）
```

**时间语义约束**

```text
1. 每一天的归属由显式 timezone 的日历日决定，不由浏览器本地时区决定
2. 日历展示必须携带 as_of：未来事件不得泄漏到「今天」
3. 日历不聚合「学习质量」类判断（有事件不代表掌握）
```

---

### 4.6 SubjectStatusGrid

| 项 | 内容 |
|---|---|
| **user question** | 三科分别处于什么状态？ |
| **data source** | `progress-state/v0.1`（综合 / 案例） + Issue #4（review debt） + essay contract（论文） |
| **source category** | `aggregate` + `phase4` + `future` |
| **implementation gate** | 综合 / 案例：Gate A ✅；review debt：Gate B；论文：未解锁 |
| **explain behavior** | 每张卡展开到该科的明细视图（topic accuracy / capability evidence / coverage） |

**三张卡的数据模型必须分离（冻结，禁止同构化）**

| 卡片 | 消费重点 | 当前状态 |
|---|---|---|
| 综合知识 | `global.accuracy`、`coverage.*`、`topics[*].accuracy`、`errors.*`；review debt（Phase 4） | 🟡 部分 Available |
| 案例分析 | `capabilities[*].score_ratio`、`capabilities[*].evidence_status`、`case.score_ratio`；weak capability（Phase 4 之后的排序另议） | 🟡 Available（注意 `evidence_status`） |
| 论文 | outline readiness、material coverage、practice status、assessment | ❌ **全部 Future** |

**available fields**

```text
综合：global.accuracy / global.attempt_count / coverage.l1|l2|l3.ratio / errors.*  / topics[*].accuracy
案例：case.attempt_count / case.score_ratio / capabilities[*].score_ratio / capabilities[*].evidence_status
```

**future fields**

```text
综合：review debt                          TBD — dependent on P4.5 replay（P4.4 字段名已冻结）
案例：weak capability ranking              TBD — dependent on P4.5 replay（排序必须来自 engine）
论文：全部字段                             TBD — essay contract 未冻结
```

**empty state**

```text
综合：未评估（尚无综合题作答）
案例：证据不足（capabilities[*].evidence_status = insufficient_evidence）
论文：尚未建立契约
```

**unavailable state**

```text
论文卡 → PaperUnavailableBadge →「尚未建立契约」
review debt → UnavailableBadge →「依赖 Mastery / Review replay（P4.5）」
```

**硬约束（冻结）**

```text
禁止把三科压缩成同一个「mastery 百分比」模型
禁止为论文卡补造字段以求三卡对称
insufficient_evidence 使用中性灰，不是红，也不是 0
```

---

### 4.7 其他候选卡片（本轮不冻结）

以下卡片出现在 Issue #5 的组件草案中，但**不属于本轮冻结的 Dashboard 六卡**：

| 卡片 / 区域 | 依赖 | 处理 |
|---|---|---|
| `PlanTimeline` | Planner contract | 见 [`TODAY_PLANNER_UX.md`](TODAY_PLANNER_UX.md)；本轮只冻结「消费 Planner 输出，不复制草案」 |
| `DailyNoteCard` | 无 contract | `Future`；语义边界见第 5 节 |

---

## 5. Note 语义边界

```text
Note != Progress Fact != Review Evidence
```

冻结规则：

```text
1. 自由文本笔记不得直接影响 mastery / accuracy / review_due / plan completion
2. `progress-event/v0.1` 上的 `note` 字段已明确「仅供人读，不参与指标」，UI 必须遵守同一语义
3. 若要引入「笔记作为事实」，必须有独立、明确、版本化的 contract 与独立事件类型
4. 在契约存在前，`DailyNoteCard` 属于 Future，不得出现于 MVP
```

---

## 6. Explainability

Explainability 是 Cockpit 的一级设计要求，不是附加功能。

| # | 要求 |
|---|---|
| E1 | 任何由 engine 产生的状态、推荐、due、任务，都必须有可展开的解释入口 |
| E2 | 解释内容只能来自 engine 输出：evidence / policy version / transition reason / `as_of` / rule id / signal snapshot |
| E3 | 若 engine 未输出原因，UI 显示「原因不可用」，**不得由 UI 生成推测性解释** |
| E4 | AI 只可用于解释文本润色、错误总结等辅助表达，不得生成事实型结论 |
| E5 | Explain 层必须显示版本信息，使历史结果可复现 |
| E6 | Explain 层默认折叠（Progressive Disclosure），首屏不暴露工程字段 |

---

## 7. 写路径约束

```text
UI → immutable events（append-only）
UI ✗→ 直接改写派生状态
```

| 允许 | 禁止 |
|---|---|
| 提交事实事件（attempt / session / 未来 review evidence） | 直接写 `ProgressState` 或 `MasteryReviewState` |
| 请求 replay（显式 `as_of`） | 让 UI 缓存成为事实源 |
| 读取 read model | 把 read model 写回 domain |
| 修改 user configuration | 用 user configuration 覆盖 domain 事实 |

---

## 8. 依赖与未决项

| 依赖 | 阻塞内容 | 当前状态 |
|---|---|---|
| D1 · Phase 4 Mastery / Review（Issue #4） | Review Queue、DueBadge、MasteryBadge、ExplainPanel、`due_count`、review debt | 🟡 **规则层已冻结**（P4.3 / P4.4）；**replay 未实现**（P4.5）→ UI 仍不可消费 |
| D2 · Planner contract | Today Card、PlanTimeline、PlanModeSwitcher、冲刺阶段 | 未冻结 |
| D3 · Cockpit Read Model contract | 所有页面的数据输入 | 本轮定义 consumer contract，未实现 |
| D4 · Assessment contract | 模拟分数、`recent_score`、目标达成度 | 未定义 |
| D5 · User Configuration contract | 考试日期、时区、每日可用时间、及格线目标 | 未定义（本轮只冻结「属于 user_config」这一分类） |
| D6 · Task execution contract | 计划完成度、完成日、streak | 未定义 |
| D7 · Essay contract | 论文状态卡、论文页面 | 未定义 |
| D8 · taxonomy / capability 迁移策略 | review item 深链稳定性 | 待 Issue #4 一并处理 |

**注意**：本文件中的所有 `TBD` 表示「上游契约尚未冻结」，不代表隐式默认值。任何实现前必须回到对应上游契约取值。
