# Cockpit UI / UX Blueprint — 文档入口

> **状态**：PLANNING CONTRACT（已冻结的规划文档，**不含任何前端实现**）
> **上游 Epic**：Issue #5 · UI / UX Blueprint v0.1
> **覆盖范围**：UI.1 ～ UI.8
> **未覆盖范围**：UI.9 Wireframe / synthetic prototype、UI.10 Implementation readiness audit
> **Phase 编号**：本目录不占用、不分配任何 Phase 编号

---

## 1. 当前阶段

```text
Research Audit            ✅
Repository Bootstrap      ✅
Taxonomy v0.1             ✅
Golden Set Expansion      ✅
Progress Model v0.1       ✅
Deterministic Replay      ✅
Mastery / Review          ✅  P4.1～P4.5 domain contract / replay；UI 未实现
Adaptive Planner          ⏳  未冻结
30-Day Plan               ⏳  docs/30_DAY_CURRICULUM_DRAFT.md 仍是 DRAFT
Cockpit UI                ⏳  本目录只冻结规划，不实现
```

本目录是**规划层**产物。它使 Cockpit 的信息架构、页面地图、数据消费契约和实现 Gate 可审计、可版本控制，但**不产生任何可运行代码**。

---

## 2. Issue #5 的定位

Issue #5 是「前端开发之前的总控 Epic」，用于回答两个不可逆风险：

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
| **Gate B** | Mastery / Review v0.1 Gate PASS | ✅ domain replay | P4.1～P4.5 已冻结并由 `engine.review.replay.replay(...)` 输出 `MasteryReviewState v0.1`；P4.6/P4.7/P4.9 与 UI read model 仍未收口 |
| **Gate C** | Planner MVP Contract 冻结 | ❌ 未冻结 | Today Card / PlanTimeline / PlanModeSwitcher 的输入契约不存在 |
| **Gate D** | Cockpit Read Model 冻结 | 🟡 本轮定义 consumer contract | 见 [`READ_MODEL_CONTRACT.md`](READ_MODEL_CONTRACT.md)；**契约定义 ≠ 实现**，且 Phase 4 / Planner 字段仍为 TBD |

结论：

```text
Gate A 解锁的视图可以进入实现准备（Progress Summary / Coverage / Error）
Gate B 已解锁 domain consumer contract；正式 UI / read model 仍须按本文件实现
Gate C 解锁的视图只能显示明确的空态
Gate D 尚未完成 → 禁止开始正式前端实现
```

**Gate 状态以 `main` 为准**：只有合并进 `main` 的契约才能进入 Gate 判定。P4.5 replay 已满足 Gate B 的 domain 四问；合并不等于前端 UI 已实现。

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
mastery_state：new / learning / mastered
review_status：not_scheduled / scheduled / due / overdue
```

**仍未收口**：

```text
P4.6/P4.7 synthetic fixture / edge-case matrix
P4.9 validation report
```

**关键结论**：

```text
规则/证据契约 + P4.5 replay = 可消费的 domain output
UI 只能消费 replay 输出，不能消费 policy kernel 本身
UI 不得绕过 replay 直接调用 engine.rules.review_policy_v01 拼装视图
```

`data/review/fixture-schema.draft.json` 仍为 `status: draft` / `frozen: false`，因为 P4.6 fixture contract 尚未收口；`validate_review.py` 会输出 `PENDING_REVIEW_FIXTURE_MATRIX`。正式 UI read model 仍不得自行重算 mastery / due。

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
- [`docs/PHASE4_TEST_MATRIX.md`](../PHASE4_TEST_MATRIX.md)（P4.6/P4.7 测试设计，fixture matrix 仍待收口）
- [`docs/review/README.md`](../review/README.md)（P4.3 / P4.4，FROZEN v0.1）
- [`docs/review/MASTERY_POLICY_V01.md`](../review/MASTERY_POLICY_V01.md)
- [`docs/review/REVIEW_SCHEDULING_POLICY_V01.md`](../review/REVIEW_SCHEDULING_POLICY_V01.md)
- [`docs/review/POLICY_SYMBOL_FREEZE_V01.md`](../review/POLICY_SYMBOL_FREEZE_V01.md)（字段名 / 枚举冻结记录）
- [`docs/review/ASSUMPTIONS_PENDING_P4_1_P4_2.md`](../review/ASSUMPTIONS_PENDING_P4_1_P4_2.md)（`UNRESOLVED`）
- [`data/review/fixture-schema.draft.json`](../../data/review/fixture-schema.draft.json)（draft，非正式契约）
