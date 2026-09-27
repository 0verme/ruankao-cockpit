# Cockpit Page Map v0.1

## Product Boundary Override / 2026-09-27

Issue #27 是当前产品边界最高依据。本文件是 historical design/reference inventory，不是 MVP route checklist。MVP 目标为单一 `/` Dashboard，Today / Review / Progress 是信息区，不是独立页面。旧路由、导航、页面与 Gate 清单不得作为实现要求；真实 UI Slice 只能由 #16 dogfood 摩擦触发。

> **状态**：Historical / design reference inventory（Issue #5 · UI.3）
> **边界**：保留旧路由语义参考，不冻结当前实现路线，也不实现任何前端路由。

---

## 1. 路由矩阵

以下是历史路由草图的状态说明；当前只有 `/` Single Dashboard 是候选 MVP 表面。Today / Review / Progress 必须先理解为 Dashboard 信息区。

```text
MVP         仅指 Single Dashboard（`/`），不是多路由清单
Deferred    独立页面不属于当前 MVP
Future      无必要证据或 domain contract 时不实现
Not Needed  当前明确不需要
```

| 路由 | 页面 | 状态 | user job | data dependency | implementation gate |
|---|---|---|---|---|---|
| `/` | Cockpit Dashboard | **Single Dashboard MVP target** | Today / Review / Progress 信息区 | 只消费真实 domain output 与显式 user config | 实现不在当前范围；先由 #16 dogfood 判断是否需要 |
| `/today` | 今日学习 | **Deferred：不是独立 MVP 路由** | Dashboard Today 信息区参考 | Today-only Planner output | 不创建独立路由；未来 UI 需 dogfood evidence |
| `/review` | 复习队列 | **Deferred：不是独立 MVP 路由** | Dashboard Review 信息区参考 | `MasteryReviewState v0.1` | 不创建独立路由；保持真实 domain mapping |
| `/progress` | 学习进度 / 掌握度 | **Deferred：不是独立 MVP 路由** | Dashboard Progress 信息区参考 | `progress-state/v0.1` + `MasteryReviewState v0.1` | 不创建独立路由；保持真实 domain mapping |
| `/settings` | 配置（考试 / 时间 / 时区） | **非 MVP 独立路由** | 仅在真实摩擦证明需要时评估配置入口 | User Configuration | 不预设独立设置页面 |
| `/plan` | 学习计划 | **Deferred** | 不属于 Single Dashboard MVP；不实现课程计划页 | Today-only Planner output（Rolling / Backbone deferred） | 无当前实现 Gate |
| `/comprehensive` | 综合知识 | **Remove from MVP** | 不建设站内练题 / 学习平台页面 | 外部学习资源引用 | 不创建独立路由 |
| `/case` | 案例分析 | **Remove from MVP** | 不建设独立案例课程 / 练习页面 | 外部学习资源引用 | 不创建独立路由 |
| `/essay` | 论文 | **Remove from MVP** | 不建设论文工作流 | 无 MVP 依赖 | 不创建独立路由 |
| `/resources` | 资源索引 | **Deferred：不建独立资源页** | Dashboard 可按需提供外部资源链接 | 外部资源引用 | 不托管或复制正文 |
| `/explain/:kind/:id` | 解释详情（可选深链） | **Deferred：独立路由** | 保留 lightweight inline Explain | 真实 domain Explain source | 不建 Explain 页面 |
| `/assessment` | 模拟考试 | **Not Needed（v0.1）** | — | assessment contract | assessment contract 未冻结 |

---

## 2. 逐路由说明

### 2.1 `/` — Cockpit Dashboard

| 项 | 内容 |
|---|---|
| user job | 打开后立刻知道：整体怎么样、今天做什么、哪些要复习、离目标多远 |
| 状态 | **MVP** |
| data dependency | `progress-state/v0.1`（Gate A ✅）、User Configuration、Planner（Today 区域）、`MasteryReviewState v0.1`（Review 区域） |
| implementation gate | 旧 Gate A / B 仅说明 domain availability；Gate C 不再是 Dashboard MVP blocker。任何 UI Slice 先等待 #16 的真实摩擦证据 |
| 卡片组成 | `OverallProgressCard`、`TodayFocusCard`、`OperationalStatsGrid`、`ExamCountdown`、`StudyCalendar`、`SubjectStatusGrid` |
| 未实现时的行为 | 当前不开发 UI；若未来因真实摩擦实现，只显示有 domain source 的字段，并如实表达 unavailable / insufficient evidence |

**冻结约束**：Dashboard 不得因为依赖缺失而渲染伪造数据。允许「少卡片」，不允许「假卡片」。

---

### 2.2 `/today` — 今日学习

| 项 | 内容 |
|---|---|
| user job | 今天做什么、开始做、做完记录 |
| 状态 | **Deferred standalone route**；Today 是 Dashboard 信息区 |
| data dependency | Planner 输出（tasks / theme / capacity）+ `MasteryReviewState v0.1` review output（due） |
| implementation gate | **非当前实现 Slice**；如 dogfood 证明需要 UI，使用现有 Today-only Planner 与 Review replay，不要求 Rolling / Backbone Gate |
| 核心流程 | 见第 5 节 Flow A |
| 当前状态 | 不实现独立 Today 页面；未来若 Dashboard Slice 经 dogfood 证实必要，只消费现有 Today-only output，不伪造任务或 CTA 目标 |
| Explain | 任务展开显示触发 rule id / 信号快照 / plan version（依赖 Planner 的 explain 输出） |

**Today 是核心信息区，不是独立页面。** 当前 Today-only 计划可由 CLI 使用；本文件不要求启动 Web UI，也不再以旧 Gate C / Rolling / Backbone 作为 MVP blocker。

---

### 2.3 `/review` — 复习队列

| 项 | 内容 |
|---|---|
| user job | 今天有哪些内容到期、为什么到期、复习后发生什么 |
| 状态 | **Deferred standalone route**；Review 是 Dashboard 信息区 |
| data dependency | **Issue #4**：`MasteryReviewState v0.1` — P4.1～P4.9 已完成，Phase 4 Gate PASS |
| implementation gate | **Gate B PASS**；Review consumer 已解锁；正式 UI Read Model / frontend 仍未实现 |
| 排序 | **100% 来自 engine**；UI 不重新排序、不自行计算优先级 |
| 未接入 UI 时的行为 | 实现层 unavailable；UI 不得绕过 replay 自行计算 due / mastery |

**冻结约束**：Review Queue 的排序、优先级、next due 全部来自 engine 输出。UI 不得用「看起来更合理」的顺序重排。

详细呈现规则见 [`REVIEW_MASTERY_UX.md`](REVIEW_MASTERY_UX.md)。

---

### 2.4 `/progress` — 学习进度 / 掌握度

| 项 | 内容 |
|---|---|
| user job | 解释 accuracy / coverage / error / mastery，而不是只看一个数字 |
| 状态 | **Deferred standalone route**；Progress 是 Dashboard 信息区 |
| data dependency | `progress-state/v0.1`（Gate A ✅）+ `MasteryReviewState v0.1`（mastery domain output） |
| implementation gate | Gate A ✅（accuracy / coverage / errors）；Gate B ✅ PASS（mastery domain available，UI 未实现） |
| 组成 | `ProgressSummary`、`TopicAccuracyList`、`CoverageBreakdown`、`ErrorCauseBreakdown`、`CapabilityEvidenceList` |
| 未接入 UI 时的行为 | mastery 区块显示实现层 unavailable；不得用 `topic accuracy` 冒充 mastery |

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
| 状态 | **非 MVP 独立页面**；是否需要配置入口由真实摩擦决定 |
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

### 2.6 `/plan` — 学习计划（DEFERRED）

| 项 | 内容 |
|---|---|
| user job | 历史规划草图；30-Day / Rolling 不是当前产品目标 |
| 状态 | **DEFERRED；不属于 MVP** |
| data dependency | Today-only Planner output；Rolling / Backbone deferred |
| implementation gate | 无当前 UI Gate；该计划页已 DEFERRED，不因旧 Gate C 实现 |
| 组成 | `PlanTimeline`、`PlanDayAccordion`、`PlanMilestoneBadge` |
| 当前状态 | 不实现计划页；Rolling / Backbone / 30-Day 均 deferred |

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

P4.1 已冻结 `review_item_id` 的稳定 identity；`/explain` 深链必须使用 engine 输出的 canonical ID，不得由 UI 自行拼接。

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

## 4. 历史多页面导航草图（DEFERRED）

以下 PrimaryNav 只是旧 IA 参考，不是要实现的导航。MVP 不以页面数量或导航完整度为目标；Dashboard 已满足需求时不新增 route。


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

## 5. Historical User Flow References（非当前实现计划）

以下流程保留为领域闭环语义参考；它们不要求建设独立页面或启动 UI。当前工程闭环由本地 CLI 提供，产品验证由 #16 dogfood 负责。


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

以下是旧 UI 草图；它不构成当前实现路线或必须达成的 UI flow：

```text
Dashboard
→ 看到整体进度（Gate A 可用）
→ 看到「Planner contract 尚未冻结」或实现层 unavailable
```

P4.5 已使 Review domain output 可消费；UI 仍不得绕过 replay 或用伪任务补齐闭环。

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

## 6. 当前 MVP 边界

```text
Single Dashboard (`/`)
├─ Today
├─ Review
└─ Progress
```

以上是同一 Dashboard 的信息区，不是独立路由。独立 `/today`、`/review`、`/progress`、`/plan`、`/comprehensive`、`/case`、`/essay`、`/resources`，复杂导航、PlanTimeline、PlanModeSwitcher、完整 Read Model 家族与大规模组件体系均 DEFERRED / 不属于 MVP。Explain 保留轻量内联形态；外部资源仅做链接 / 引用。

**MVP 不做**：题库 / 课程执行平台、practice / case_practice / essay / mock_exam task expansion、论文编辑器、AI tutor、资源商城、社区、账号体系、复杂权限、云同步。

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
