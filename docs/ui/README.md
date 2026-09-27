# Cockpit UI / UX Blueprint — 文档入口

## Product Boundary Override / 2026-09-27

Issue #27 是当前产品边界最高依据。本目录与 Issue #5 旧 UI Blueprint 仅为 **historical / design reference inventory**，不是 MVP implementation checklist。当前 UI 目标只有一个 Single Dashboard（Today / Review / Progress 信息区）；独立路由、多页面导航、PlanTimeline、PlanModeSwitcher、完整 Read Model 家族与大规模组件体系均 deferred。只有 #16 dogfood 产生真实摩擦后才评估最小 UI Slice。

保留真实 domain → UI truthfulness、`null` / `insufficient_evidence`、Topic / Capability 隔离、Explain、responsive 与基本 accessibility。

> **状态**：Historical / design reference inventory（不含前端实现；不是当前执行计划）
> **上游 Epic**：Issue #5 · UI / UX Blueprint v0.1（受 Issue #27 override）
> **覆盖范围**：旧 UI.1 ～ UI.8 参考材料
> **Phase 编号**：本目录不占用、不分配任何 Phase 编号

---

## 1. 当前产品状态（非功能路线图）

```text
Today-only Planner + local CLI engineering loop  ✅
真实产品验证 / Dogfood（Issue #16）             ⏳ 当前优先
Rolling 7-Day / Curriculum Backbone / 30-Day     DEFERRED by Issue #27
Web UI                                          未实现；不自动开工
```

本目录保留旧信息架构、页面地图、数据消费语义与设计护栏供查阅；它不产生可运行代码，也不要求按旧页面、Read Model 或 Gate 清单继续扩张。

---

## 2. Issue #5 的定位

Issue #5 当前仅作为 **design/reference inventory** 保留，不是前端开发 Epic 或实现排期。真实产品优先级由 Issue #27 控制；未来是否需要 UI 由 #16 的 dogfood evidence 决定。旧 blueprint 中的事实正确性护栏仍可参考，用于阻断两个不可逆风险：

```text
风险 A：UI 自己推算 mastery / review_due / plan completion
        → 事实型学习指标失去确定性来源

风险 B：为了填满卡片而复制课程草案或参考截图的数字
        → Draft 被 UI 反向升级为事实，违反 AGENTS.md Progress 约束
```

本目录中的每一份文档都服务于阻断这两个风险，而不是服务于「让 UI 看起来完整」。

---

## 3. Gate 状态

Gate 定义沿用 Issue #5。当前真实状态如下：

| Gate | 含义 | 当前状态 | 说明 |
|---|---|---|---|
| **Gate 0** | 无领域依赖的规划 / 静态原型 | 🟡 部分允许 | 本目录（IA / Page Map / token / component 方向）已完成；wireframe 与 synthetic prototype（UI.9）**未开始** |
| **Gate A** | Progress Contract 稳定 | ✅ PASS | `progress-event/v0.1` + `progress-state/v0.1` + `progress-replay/v0.1` 已在 main 冻结并验证 |
| **Gate B** | Mastery / Review v0.1 Gate PASS | ✅ PASS | Phase 4 四项 Gate 已由 fixtures、tests 与正式报告验证；`engine.review.replay.replay(...)` 输出 `MasteryReviewState v0.1`。Review Queue 等 consumer 的 UI / Read Model 代码仍未实现 |
| **Gate C** | 旧 Planner / horizon consumer Gate | ⚪ **superseded / deferred by #27，非 MVP blocker** | Today-only Planner / CLI 已存在；Rolling、Backbone、PlanTimeline / PlanModeSwitcher 不要求实现 |
| **Gate D** | 完整 Cockpit Read Model | ⚪ **非当前实现 Gate** | 不建设完整 Read Model 家族；若 dogfood 后确有 UI Slice，再定义其最小真实 domain mapping |

旧 Gate A / B 可作为 domain truthfulness 参考；Gate C 的 Rolling / Backbone 要求已由 #27 superseded / deferred，Gate D 的完整 Read Model 也不是 MVP 前置条件。当前没有 Web UI 实现计划：先完成 #16 真实 dogfood，再根据明确摩擦决定是否需要 Single Dashboard Slice。

Gate B PASS 只说明 Review domain output 可用，不代表 UI 已实现。Phase 4 事实与证据见 [`docs/PHASE4_VALIDATION_REPORT.md`](../PHASE4_VALIDATION_REPORT.md)。

**Gate 状态以 `main` 为准**：只有合并进 `main` 的契约才能进入 Gate 判定。Phase 4 replay + fixtures + tests + P4.9 report 共同验证 Gate B 四问；合并不等于前端 UI 已实现。

---

## 4. 能力可用性分类

### 4.1 Available（当前 `progress-state/v0.1` 已可确定性计算）

```text
global.attempt_count / correct_count / incorrect_count / accuracy
topics[*].attempt_count / correct_count / incorrect_count / accuracy
case.attempt_count / scored_attempt_count / score_earned / score_possible / score_ratio
capabilities[*].attempt_count / score_earned / score_possible / score_ratio / evidence_status
errors.error_count / classified_error_count / unclassified_error_count
errors.error_count_by_cause / errors.error_cause_mix
coverage.l1 / coverage.l2 / coverage.l3  (covered / total / ratio)
study.session_count / study_minutes
schema_version / replay_rule_version / event_schema_version
taxonomy_version / capability_version
replayed_event_count
```

### 4.2 依赖 Issue #4（Phase 4）—— domain replay 已可消费，UI 仍为规划

**已冻结并可消费（已在 main）**：

```text
P4.1/P4.2  review-model/v0.1 + review-event/v0.1 + review-evidence/v0.1
P4.3/P4.4  mastery-policy/spaced-consecutive/v0.1
           review-policy/simple-ladder/v0.1
P4.5        mastery-review-state/v0.1（显式 as_of + timezone）
P4.6/P4.7  36 个冻结 synthetic fixtures、validator、edge-case / determinism tests
P4.8/P4.9  文档 / 架构同步、四项 Gate 正式验证报告
Available   mastery_state / mastery_reason；review_status / reason；due counts；
           review_interval_days / next_due_at / next_due_local_date；evidence trace；
           policy / adapter versions；as_of / timezone / tzdata_version
```

Phase 4 domain contract / output / fixture matrix / validation **均已收口，Gate B PASS**。尚未实现的是 UI / Read Model / frontend，不是 P4.6 / P4.7 / P4.9。

**关键结论**：

```text
规则/证据契约 + P4.5 replay = 可消费的 domain output
UI 只能消费 replay 输出，不能消费 policy kernel 本身
UI 不得绕过 replay 直接调用 engine.rules.review_policy_v01 拼装视图
```

`data/review/fixture-schema.draft.json` 保留为已 superseded 的历史草案；正式 P4.6 fixture contract 是 `mastery-review-fixture/v0.1`，由 `fixture-schema.v0.1.json` 定义。`validate_review.py` 只报告 fixture matrix，不单独判定 Gate。正式 UI read model 仍不得自行重算 mastery / due。

### 4.3 依赖 Planner（当前不存在）

```text
Today Plan / day_index / plan_phase / day_type
theme.primary_topic_id / supporting_topic_ids / capability_ids
capacity.planned_minutes / tier
tasks[] / task ref / est_minutes / required
plan version / plan explain（rule id + signal snapshot）
计划完成度
```

### 4.4 Future（无任何 contract）

```text
assessment / mock score / recent_score
essay status / essay progress / 论文评分
task execution / completion_rate / 完成日
streak
capacity_actual
笔记作为事实
exam score normalization（75 分制换算）
```

### 4.5 User Configuration（用户输入，不是 domain 事实）

```text
考试日期（→ 倒计时剩余天数）
时区
每日可用时间 / 档位
及格线 / 目标（必须标注为「目标 / 参考」）
```

---

## 5. 文档导航

| 文档 | 覆盖 | 内容 |
|---|---|---|
| [`COCKPIT_UI_BLUEPRINT.md`](COCKPIT_UI_BLUEPRINT.md) | UI.1 / UI.2 | Product Goal、UX Principles、Information Architecture、Dashboard 六张卡片的数据语义 |
| [`PAGE_MAP.md`](PAGE_MAP.md) | UI.3 | 路由矩阵、导航结构、每个路由的 user job / data dependency / implementation gate |
| [`DOMAIN_TO_UI_MAPPING.md`](DOMAIN_TO_UI_MAPPING.md) | UI.4 | UI Metric → Domain Field 映射表、来源分类、null / unavailable 语义、非契约参考值清单 |
| [`REVIEW_MASTERY_UX.md`](REVIEW_MASTERY_UX.md) | UI.5 | mastery status 与 scheduling status 二维分离、用户层 / Explain 层、Review Queue 排序归属 |
| [`TODAY_PLANNER_UX.md`](TODAY_PLANNER_UX.md) | UI.6 | Static Curriculum / Generated Plan / Adaptive Daily Plan 区分、Today Card consumer contract |
| [`RESPONSIVE_ACCESSIBILITY.md`](RESPONSIVE_ACCESSIBILITY.md) | UI.7 | Desktop / Tablet / Mobile 断点行为、移动端降级策略、WCAG 2.1 AA 要求 |
| [`DESIGN_DIRECTION.md`](DESIGN_DIRECTION.md) | UI.8 | 视觉方向、语义色、token 方向（非 token package） |
| [`COMPONENT_MAP.md`](COMPONENT_MAP.md) | UI.8 | 组件边界、view-model 输入约定、禁止事项 |
| [`READ_MODEL_CONTRACT.md`](READ_MODEL_CONTRACT.md) | UI Read Model | 7 个 read model 的 consumer contract 与 source-of-truth 边界 |

---

## 6. 两条不可协商的声明

### 6.1 Planning ≠ Implementation

```text
docs/ui/**            = 规划与契约
前端工程 / UI 代码     = 未开始，且不在本轮范围
```

本目录中的任何字段、状态、组件或 token 都**不表示该能力已实现**。文档中出现的组件名（`TodayFocusCard`、`ReviewQueue` …）是**职责边界声明**，不是代码产物。

### 6.2 UI Read Model ≠ Source of Truth

```text
事实源：Immutable Progress Events（append-only）
派生：ProgressState / MasteryReviewState / Plan（deterministic replay）
展示：UI Read Model
```

UI Read Model：

```text
可以派生
可以缓存
可以重建

不能成为事实源
不能被写回 domain
不能产生新的业务事实
```

---

## 7. 本目录明确不做的事

```text
❌ React / Vue / Astro 初始化
❌ package.json 前端工程
❌ 正式 Web App
❌ API Server（FastAPI / Flask / 任意框架）
❌ 数据库（SQLite / PostgreSQL）
❌ 登录 / 账号 / 用户 / 权限系统
❌ Planner 实现
❌ Mastery 实现
❌ Review Scheduling 实现
❌ AI tutor / AI 自动评分 / AI 自动 mastery
❌ 复制第三方题库、教材、讲义或 PDF 正文
❌ 为了让卡片「看起来完整」而补业务默认值
```

---

## 8. 维护规则

1. **不得把 Draft 升级为 Contract**：`docs/30_DAY_CURRICULUM_DRAFT.md` 中的 `Day 1..30`、`1/3/7/15`、`连续答对 >= 3`、`due_card_count` 等规则，只有在对应正式契约冻结后才能被 UI 消费。
2. **不得虚构上游 schema**：Planner、Assessment、Essay 等尚未冻结的字段仍必须写 `TBD — dependent on ...`，不得给出看似确定的字段名与枚举。P4.1～P4.5 已冻结并实现的 `MasteryReviewState v0.1` 字段应直接引用 replay schema，不得由 UI 自行改写。
3. **不得引入虚假业务数据**：任何示例数值只能以 `reference-only` / `synthetic` / `non-contract` 形式出现，且不得被任何 domain、engine、validator 或 fixture 消费。
4. **不得改动 Phase 编号**：本目录引用 README / `docs/architecture/README.md` 的阶段顺序，但不新增、不重排、不命名任何 Phase。
5. **变更需可审计**：修改任何映射或状态语义时，必须在同一次改动中说明它对应哪个上游 contract 版本。

---

## 9. 上游引用

- [`README.md`](../../README.md)
- [`AGENTS.md`](../../AGENTS.md)
- [`docs/architecture/README.md`](../architecture/README.md)
- [`docs/30_DAY_CURRICULUM_DRAFT.md`](../30_DAY_CURRICULUM_DRAFT.md)（DRAFT）
- [`engine/progress/README.md`](../../engine/progress/README.md)
- [`data/progress/schema.json`](../../data/progress/schema.json)
- [`engine/rules/README.md`](../../engine/rules/README.md)
- [`taxonomy/README.md`](../../taxonomy/README.md)
- [`docs/PHASE4_TEST_MATRIX.md`](../PHASE4_TEST_MATRIX.md)（P4.6/P4.7 测试矩阵；最终状态与 Gate 证据见 Phase 4 Validation Report）
- [`docs/review/README.md`](../review/README.md)（P4.3 / P4.4，FROZEN v0.1）
- [`docs/review/MASTERY_POLICY_V01.md`](../review/MASTERY_POLICY_V01.md)
- [`docs/review/REVIEW_SCHEDULING_POLICY_V01.md`](../review/REVIEW_SCHEDULING_POLICY_V01.md)
- [`docs/review/POLICY_SYMBOL_FREEZE_V01.md`](../review/POLICY_SYMBOL_FREEZE_V01.md)（字段名 / 枚举冻结记录）
- [`docs/review/ASSUMPTIONS_PENDING_P4_1_P4_2.md`](../review/ASSUMPTIONS_PENDING_P4_1_P4_2.md)（RECONCILED；文件名保留历史，当前仅 score rubric 仍未冻结）
- [`data/review/fixture-schema.draft.json`](../../data/review/fixture-schema.draft.json)（draft，非正式契约）
