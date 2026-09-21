# Cockpit Page Map v0.1

> **状态**：PLANNING CONTRACT（Issue #5 · UI.3）
> **边界**：本文件冻结路由矩阵、导航结构与每个路由的 user job / data dependency / implementation gate；**不实现任何前端路由**。

---

## 1. 路由矩阵

状态图例：

```text
MVP         第一版 Cockpit 必须存在的路由
Later       需要额外数据契约或录入流程，先以入口 + 摘要存在
Future      无任何 contract，只规划不实现
Not Needed  v0.1 明确不需要的页面
```

| 路由 | 页面 | 状态 | user job | data dependency | implementation gate |
|---|---|---|---|---|---|
| `/` | Cockpit Dashboard | **MVP** | 一眼知道整体状态、今天做什么、哪些要复习 | `progress-state/v0.1` + User Config | Gate A ✅；Today 区域需 Gate C |
| `/today` | 今日学习 | **MVP** | 开始今天的任务并记录结果 | Planner 输出 + Review 输出 | Gate C + Gate B |
| `/review` | 复习队列 | **MVP** | 清掉今天到期的复习 | MasteryReviewState（Issue #4） | Gate B |
| `/progress` | 学习进度 / 掌握度 | **MVP** | 解释 accuracy / coverage / error / mastery | `progress-state/v0.1` + Issue #4 | Gate A ✅ + Gate B |
| `/settings` | 配置（考试 / 时间 / 时区） | **MVP（最小）** | 设定考试日期、时区、可用时间、目标 | User Configuration | Gate 0（无账号体系） |
| `/plan` | 学习计划 | **Later** | 看清 30 天结构与可调整的近期安排 | Planner 输出 | Gate C |
| `/comprehensive` | 综合知识 | **Later** | 练综合题并查看 topic 级表现 | 题源接入 + 作答交互 + `progress-state/v0.1` | Gate A ✅；题源接入未就绪 |
| `/case` | 案例分析 | **Later** | 练案例并按 capability 记录证据 | capability-level 证据录入流程 + `progress-state/v0.1` | Gate A ✅；录入流程未就绪 |
| `/essay` | 论文 | **Future** | 论文准备到哪一步 | essay contract | 未解锁（独立 Future） |
| `/resources` | 资源索引 | **Later** | 查看内容来源与引用 | source catalog + 版权边界确认 | 未解锁 |
| `/explain/:kind/:id` | 解释详情（可选深链） | **Later** | 追一条状态 / 任务的原因链 | 对应 read model 的 explain 字段 | 可先以 `ExplainPanel` 内联实现 |
| `/assessment` | 模拟考试 | **Not Needed（v0.1）** | — | assessment contract | assessment contract 未冻结 |

---

## 2. 逐路由说明

### 2.1 `/` — Cockpit Dashboard

| 项 | 内容 |
|---|---|
| user job | 打开后立刻知道：整体怎么样、今天做什么、哪些要复习、离目标多远 |
| 状态 | **MVP** |
| data dependency | `progress-state/v0.1`（Gate A ✅）、User Configuration、Planner（Today 区域）、Issue #4（Review 区域） |
| implementation gate | 综合 / 案例 / 统计 / 倒计时区域：Gate A；Today 区域：Gate C；Review 区域：Gate B |
| 卡片组成 | `OverallProgressCard`、`TodayFocusCard`、`OperationalStatsGrid`、`ExamCountdown`、`StudyCalendar`、`SubjectStatusGrid` |
| 未冻结时的行为 | Today 区域显示 `EmptyState`「Planner contract 尚未冻结」；Review 区域显示 `UnavailableBadge` |

**冻结约束**：Dashboard 不得因为依赖缺失而渲染伪造数据。允许「少卡片」，不允许「假卡片」。

---

### 2.2 `/today` — 今日学习

| 项 | 内容 |
|---|---|
| user job | 今天做什么、开始做、做完记录 |
| 状态 | **MVP**（Today-first 核心闭环入口） |
| data dependency | Planner 输出（tasks / theme / capacity）+ Review 输出（due） |
| implementation gate | **Gate C**（Planner）+ **Gate B**（Review） |
| 核心流程 | 见第 5 节 Flow A |
| 未冻结时的行为 | `EmptyState`：「Planner contract 尚未冻结」；不渲染任务列表，不渲染伪造 CTA 目标 |
| Explain | 任务展开显示触发 rule id / 信号快照 / plan version（依赖 Planner 的 explain 输出） |

**Today 是核心路径**：如果只能实现一个页面，就是它。但在 Gate C 通过前，它只能是空态。

---

### 2.3 `/review` — 复习队列

| 项 | 内容 |
|---|---|
| user job | 今天有哪些内容到期、为什么到期、复习后发生什么 |
| 状态 | **MVP**（数据依赖 Issue #4） |
| data dependency | **Issue #4**：`MasteryReviewState`、`review_item`、`due_count`、`review_due_at`、transition reason |
| implementation gate | **Gate B**（未通过） |
| 排序 | **100% 来自 engine**；UI 不重新排序、不自行计算优先级 |
| 未冻结时的行为 | `UnavailableBadge`：「依赖 Mastery / Review v0.1」 |

**冻结约束**：Review Queue 的排序、优先级、next due 全部来自 engine 输出。UI 不得用「看起来更合理」的顺序重排。

详细呈现规则见 [`REVIEW_MASTERY_UX.md`](REVIEW_MASTERY_UX.md)。

---

### 2.4 `/progress` — 学习进度 / 掌握度

| 项 | 内容 |
|---|---|
| user job | 解释 accuracy / coverage / error / mastery，而不是只看一个数字 |
| 状态 | **MVP**（掌握度部分依赖 Issue #4） |
| data dependency | `progress-state/v0.1`（Gate A ✅）+ Issue #4（mastery 部分） |
| implementation gate | Gate A ✅（accuracy / coverage / errors）；Gate B（mastery） |
| 组成 | `ProgressSummary`、`TopicAccuracyList`、`CoverageBreakdown`、`ErrorCauseBreakdown`、`CapabilityEvidenceList` |
| 未冻结时的行为 | mastery 区块显示 `UnavailableBadge`；不得用 `topic accuracy` 冒充 mastery |

**冻结约束**：

```text
topic accuracy != mastery
capability score_ratio != mastery
coverage（taxonomy 节点分母）!= 考试权重覆盖率
```

---

### 2.5 `/settings` — 配置

| 项 | 内容 |
|---|---|
| user job | 设定考试日期、时区、每日可用时间、目标 |
| 状态 | **MVP（最小）** |
| data dependency | User Configuration（不是 domain 事实） |
| implementation gate | Gate 0（但**没有账号体系**；配置属于本地用户输入） |
| 最小字段 | `exam_date`、`timezone`、`daily_available_minutes` / 档位、目标 / 及格线（标注为「目标 / 参考」） |
| 未定义 | 配置的持久化方式、配置版本、配置迁移 → 不在本轮冻结 |

**冻结约束**：

```text
1. 无登录、无账号、无用户系统、无云同步
2. 目标 / 及格线必须标注为「目标 / 参考」，不得显示为 domain 事实
3. 配置不得覆盖或伪造 domain 指标
```

---

### 2.6 `/plan` — 学习计划

| 项 | 内容 |
|---|---|
| user job | 看清 30 天结构与近期可调整安排 |
| 状态 | **Later** |
| data dependency | Planner 输出（Backbone / Rolling 7-Day / Daily Adaptive） |
| implementation gate | **Gate C**（Planner MVP Contract 冻结） |
| 组成 | `PlanTimeline`、`PlanDayAccordion`、`PlanMilestoneBadge` |
| 未冻结时的行为 | `EmptyState`：「Planner contract 尚未冻结」 |

**冻结约束**：

```text
1. 不得硬编码 docs/30_DAY_CURRICULUM_DRAFT.md 的 Day 1..30
2. 必须区分 Static Curriculum / Generated Plan / Adaptive Daily Plan
3. 见 TODAY_PLANNER_UX.md
```

---

### 2.7 `/comprehensive` — 综合知识

| 项 | 内容 |
|---|---|
| user job | 练综合题，并查看 topic 级表现 |
| 状态 | **Later** |
| data dependency | 题源接入 + 作答交互 + `progress-event/v0.1`（`comprehensive_attempt`） |
| implementation gate | Gate A ✅（数据侧）；**题源接入与作答流程未就绪** |
| 当前形态 | 入口 + 摘要（消费 `global.*` / `topics[*].accuracy` / `errors.*` / `coverage.*`） |
| 版权约束 | 只索引 / 引用来源，不复制题干、选项、答案、解析、OCR、PDF |

**冻结约束**：在题源接入与版权边界确认前，本页不得渲染题目正文。

---

### 2.8 `/case` — 案例分析

| 项 | 内容 |
|---|---|
| user job | 练案例，并按 Case Capability 记录 score evidence |
| 状态 | **Later** |
| data dependency | capability-level 证据录入流程 + `progress-event/v0.1`（`case_attempt` + `capability_scores`） |
| implementation gate | Gate A ✅（数据侧）；**证据录入流程未就绪** |
| 当前形态 | 入口 + 摘要（消费 `case.score_ratio` / `capabilities[*].score_ratio` / `evidence_status`） |

**冻结约束**：

```text
1. 案例总分不得复制给每个被引用的 capability
2. 只有带 capability_scores 证据的 capability 才有 score_ratio
3. insufficient_evidence 不等于 0，也不等于失败
4. Knowledge Topic 与 Case Capability 必须分开展示，不得合并成一个百分比
```

---

### 2.9 `/essay` — 论文

| 项 | 内容 |
|---|---|
| user job | 论文准备到哪一步 |
| 状态 | **Future** |
| data dependency | essay contract（不存在） |
| implementation gate | 未解锁（Gate 之外，独立 Future） |
| 当前形态 | 入口 + 不可用态说明；**不做论文编辑器** |

**冻结约束**：在 essay contract 冻结前，本页不得显示任何分数、进度条或「篇数」类指标。参考 UI 中出现的任何论文分数形值均属非契约。

---

### 2.10 `/resources` — 资源索引

| 项 | 内容 |
|---|---|
| user job | 查看内容来源与引用位置 |
| 状态 | **Later** |
| data dependency | source catalog + 版权边界确认（`docs/CONTENT_SOURCE_AUDIT.md`、`taxonomy/source-mappings.json`） |
| implementation gate | 未解锁 |
| 当前形态 | 入口 + 来源清单（source_id / source_path / license 分类） |

**冻结约束**：遵守 `AGENTS.md` 的 A/B/C/D 分类；license 不明确时不复制原文。

---

### 2.11 `/explain/:kind/:id` — 解释详情（可选深链）

| 项 | 内容 |
|---|---|
| user job | 追一条状态或任务的原因链，并拿到可复现的版本信息 |
| 状态 | **Later**（可先以 `ExplainPanel` 内联实现） |
| data dependency | 对应 read model 的 explain 字段（evidence / policy version / transition reason / `as_of`） |
| implementation gate | 取决于被解释对象：Gate A / B / C |
| `:kind` 取值（规划） | 与 `ExplainView` 的 `subject_kind` 对齐：`progress` / `capability` / `review_item` / `plan_task` / `metric` |

**冻结约束**：

```text
1. 若 engine 未输出原因 → 显示「原因不可用」，不得由 UI 推测
2. 深链必须携带 as_of（或可确定地重建 as_of），否则解释不可复现
3. :id 不得是展示名称 / 自由文本；必须是稳定 canonical id
```

**身份稳定性风险（已知未决）**：`review_item_id` 在 taxonomy / capability 版本升级时的迁移策略尚未冻结（依赖 Issue #4 · D8）。在此之前，`/explain` 深链的长期稳定性不作承诺。

---

### 2.12 `/assessment` — 模拟考试

| 项 | 内容 |
|---|---|
| user job | — |
| 状态 | **Not Needed（v0.1）** |
| data dependency | assessment contract（不存在） |
| implementation gate | assessment contract 冻结后再评估 |

**冻结约束**：不建页面，也不在 Dashboard / Stats 中伪造模拟分数或「完成 N 场模拟」类指标。

---

## 3. 明确不需要的页面

以下路由在 v0.1 **不创建**，因为不存在对应需求：

| 路由 | 原因 |
|---|---|
| `/admin` | 无管理需求；无权限系统 |
| `/login`、`/register`、`/account` | 无账号 / 用户系统 |
| `/community`、`/forum` | 无社区需求 |
| `/shop`、`/store` | 无资源商城需求 |
| `/cloud-sync` | 无云同步需求 |
| `/ai-tutor` | 无 AI tutor 需求 |

**规则**：没有明确 user job 的入口不建。不要为了「看起来像一个完整产品」而创建路由。

---

## 4. 导航结构

```text
PrimaryNav（一级导航，横向）
├─ 今日        /today
├─ 计划        /plan
├─ 综合        /comprehensive
├─ 案例        /case
├─ 论文        /essay
├─ 复习        /review
└─ 资源        /resources

TopHeader 右侧（二级控件）
├─ 计划视图切换（7 / 14 / 30 天）    依赖 Planner
├─ 导入 / 导出                        依赖事件写路径
├─ 重放（显式 as_of + replay 版本）    依赖 Gate A ✅
└─ 设置                              /settings

Dashboard 内（三级入口）
├─ 卡片 → 明细页（/progress、/case、/comprehensive）
└─ 状态 / 任务 → /explain/:kind/:id（或内联 ExplainPanel）
```

| 规则 | 内容 |
|---|---|
| N1 | 一级导航入口必须都能回答一个 user job；`Future` 入口（论文）保留但必须显示不可用态说明 |
| N2 | `PlanModeSwitcher` 在 Planner contract 冻结前**不渲染**，而不是渲染禁用项加假数据 |
| N3 | 导航不得暗示不存在的能力（例如不出现「模拟考试」入口） |
| N4 | 深链必须使用稳定 canonical id，不得使用展示名称 |
| N5 | 面包屑由路由层级推导，不引入额外状态 |

---

## 5. 关键用户流程

### Flow A · 每天打开 Cockpit（主闭环）

```text
Dashboard
→ 看今日任务（TodayFocusCard）        [Gate C]
→ 看到期复习（Review due）             [Gate B]
→ 开始学习                              [Gate C]
→ 记录事实事件（append-only）
→ 重放（显式 as_of）
→ Dashboard 更新
```

在 Gate B / Gate C 未通过时，Flow A 的合法形态只有：

```text
Dashboard
→ 看到整体进度（Gate A 可用）
→ 看到「Planner contract 尚未冻结」/「依赖 Mastery / Review v0.1」
```

**不允许**用伪任务把 Flow A 补成一个看起来完整的闭环。

### Flow B · 综合题

```text
/today（或 /comprehensive）
→ 作答
→ 提交 comprehensive_attempt（immutable event；错误可带 error_cause）
→ replay（显式 as_of）
→ global / topics / coverage / errors 更新
→ Dashboard / Progress 刷新
```

### Flow C · 复习

```text
/review
→ 选择 due item（排序来自 engine）
→ 完成 review
→ 产生 review evidence（Issue #4 契约）
→ mastery transition（Issue #4）
→ next due（Issue #4）
```

### Flow D · 案例分析

```text
/case
→ 完成案例子问题
→ 提交 case_attempt（可选总分证据 + capability_scores）
→ replay
→ case.score_ratio / capabilities[*] 更新
```

### Flow E · Explain

```text
点击状态 / 任务
→ 展开
→ evidence
→ rule / policy / version
→ as_of
→ result
```

### 所有 Flow 的共同约束

```text
1. 写路径必须落到 immutable events；UI 不得直接改写派生状态
2. 任何「今天」判断必须使用显式 as_of + timezone
3. 无 contract 的环节只能显示空态 / 不可用态，不得伪造
```

---

## 6. 页面与 MVP 边界

```text
MVP 集合（第一版 Cockpit 真正需要的路由）：
  /              Dashboard
  /today         Today（依赖 Planner / Issue #4）
  /review        Review Queue（依赖 Issue #4）
  /progress      Progress Summary（mastery 部分依赖 Issue #4）
  /settings      最小配置

摘要入口（Later）：
  /plan  /comprehensive  /case  /resources  /explain/:kind/:id

不实现：
  /essay（Future）  /assessment（Not Needed v0.1）
```

**MVP 不做**：题库平台、论文编辑器、AI tutor、资源商城、社区、账号体系、复杂权限、云同步。

---

## 7. 与其余 UI 文档的关系

| 关注点 | 文档 |
|---|---|
| Dashboard 卡片数据语义 | [`COCKPIT_UI_BLUEPRINT.md`](COCKPIT_UI_BLUEPRINT.md) |
| 指标 → domain 字段 | [`DOMAIN_TO_UI_MAPPING.md`](DOMAIN_TO_UI_MAPPING.md) |
| 页面数据输入 | [`READ_MODEL_CONTRACT.md`](READ_MODEL_CONTRACT.md) |
| Review 呈现 | [`REVIEW_MASTERY_UX.md`](REVIEW_MASTERY_UX.md) |
| Today / Plan 呈现 | [`TODAY_PLANNER_UX.md`](TODAY_PLANNER_UX.md) |
| 断点行为 | [`RESPONSIVE_ACCESSIBILITY.md`](RESPONSIVE_ACCESSIBILITY.md) |
| 组件边界 | [`COMPONENT_MAP.md`](COMPONENT_MAP.md) |
