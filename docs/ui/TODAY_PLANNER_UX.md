# Today / Planner UX Contract v0.1

> **状态**：PLANNING CONTRACT（Issue #5 · UI.6）
> **依赖**：Planner contract（**未冻结**）+ Issue #4 domain replay（**P4.5 已完成**）
> **重要声明**：本文件只冻结「UI 如何消费未来 Planner 输出」的规划。**不实现 Planner，不定义 Planner 的输出 schema。**
> **备注**：下方的 `review.*` domain 值由 `MasteryReviewState v0.1` replay 提供；本文件不直接调用 policy kernel。

---

## 1. 当前实现状态

```text
Adaptive Planner              ❌ 不存在
30-Day Plan 实例化             ❌ 不存在
Rolling 7-Day Plan            ❌ 不存在
Daily Adaptive Tasks          ❌ 不存在
task execution contract       ❌ 不存在
plan completion               ❌ 不存在
Today Plan                    ❌ 不存在
plan version / policy version ❌ 不存在
plan explain（rule id + signal snapshot） ❌ 不存在
```

现状证据：

- `engine/rules/README.md` 的 **计划形态（Future）** 明确把 Backbone / Rolling / Daily 三层列为未来工作。
- `README.md` 的当前状态把 `Adaptive Planner`、`30-Day Plan` 标为 ⏳。
- `docs/architecture/README.md` 把 `Adaptive Planner` 与 `Cockpit UI` 标为 ⏳，并说明本阶段未实现 planner。

因此：

```text
TodayFocusCard 的 Planner 任务区当前状态 = EmptyState
复习 domain 数据源 = P4.5 replay 可用；Today read model / UI 仍未实现
```

---

## 2. 三种计划形态必须区分（核心冻结决策）

UI 与文档必须严格区分三种不同事物：

| 形态 | 定义 | 来源 | 当前状态 |
|---|---|---|---|
| **Static Curriculum** | 课程设计草案：阶段划分、原则、候选规则 | `docs/30_DAY_CURRICULUM_DRAFT.md` | **DRAFT**，不是 contract |
| **Generated Plan** | 由 Planner 依据 Backbone + 信号生成的计划实例 | Planner contract | ❌ 未冻结 |
| **Adaptive Daily Plan** | 每日根据当天结果写回并重排的当日任务 | Daily Adaptive（Planner 的一部分） | ❌ 未冻结 |

**UI 最终只消费 Planner 输出**，不得消费 Static Curriculum，也不得自行生成 Adaptive 结果。

```text
Static Curriculum  ✗→ UI
Generated Plan      ✓→ UI（Planner 冻结后）
Adaptive Daily Plan ✓→ UI（Planner 冻结后）
```

---

## 3. `docs/30_DAY_CURRICULUM_DRAFT.md` 的地位

该文件当前状态：

```text
DRAFT（Curriculum 设计草案，不是最终每日计划）
```

冻结约束：

```text
1. 它是 Draft，不得因 UI 需要而升级为正式 contract
2. 不得硬编码进 UI
3. 其中的规则必须等对应正式契约（Issue #4 / Planner）逐项裁决
4. UI 不得把它的阶段名、天数、阈值、配额当作事实
```

### 3.1 明确禁止硬编码为 UI Contract 的草案内容

| 草案内容 | 类型 | 状态 |
|---|---|---|
| `Day 1..30` 逐日结构 | 阶段设计 | Draft；**禁止硬编码** |
| `1 / 3 / 7 / 15` 复习间隔 | Review policy 参数 | ✅ P4.4 冻结；UI 只消费 replay 输出 |
| `连续答对 >= 3 → mastered` | Mastery policy 规则 | ✅ P4.3 冻结；实际字段为 `mastery_state` |
| `due_card_count` | 复习债务信号 | ❌ 非冻结字段；使用 replay 的 `review.due_count`（unit = review_item） |
| `baseline_accuracy` / `recent_score` | 候选信号 | `recent_score` 依赖 assessment contract |
| `capacity.tier`（8 / 14 / 22 小时档） | 候选容量档位 | Draft；不得作为 UI 常量 |
| `error_cause_mix` 阈值（例如 `> 0.5`） | 候选规则阈值 | Draft；Planner 冻结前不得进入 UI |
| `completion_rules` / `adaptation.*` 规则 | 候选规则 | Draft；**禁止在 UI 中实现** |
| `weakModules` / `inferWeakModule()` | 参考实现 | 第三方结构参考，不是本仓库契约 |

**UI 的实现禁止项**：

```text
UI 不得实现任何 adaptation rule
UI 不得计算 weak module 排序
UI 不得实现 completion rule
UI 不得用草案阈值决定任何展示
```

---

## 4. TodayFocusCard 的 consumer contract

UI 只定义「消费需求」，不定义 Planner 输出。

### 4.1 当前（Planner 未冻结）

| 项 | 内容 |
|---|---|
| 显示内容 | 空态：「Planner contract 尚未冻结」 |
| 允许的字段 | 无 |
| CTA | 不渲染可用 CTA（不得指向伪造任务流） |
| Explain | 不渲染（无原因可解释） |
| 禁止 | 渲染任何任务、天数、主题、时长、进度 |

### 4.2 Planner 冻结后（规划，字段名均为 TBD）

```text
day_index                                   TBD — dependent on Planner contract
plan_phase                                  TBD — dependent on Planner contract
day_type                                    TBD — dependent on Planner contract
theme.primary_topic_id                      TBD — dependent on Planner contract
theme.supporting_topic_ids                  TBD — dependent on Planner contract
theme.capability_ids                        TBD — dependent on Planner contract
capacity.planned_minutes / capacity.tier    TBD — dependent on Planner contract
tasks[].id / type / ref / est_minutes / required
                                            TBD — dependent on Planner contract
plan_version / policy version               TBD — dependent on Planner contract
cta_target                                  TBD — dependent on Planner contract
explain（rule id + signal snapshot）         TBD — dependent on Planner contract
```

依赖 Issue #4 的复习区块：

```text
review.due_count                            ✅ P4.5 replay 输出（unit = review_item）
review.overdue_count                        ✅ P4.5 replay 输出
review.next_due_at                          ✅ item-level P4.5 replay 输出
```

### 4.3 消费约束（冻结）

```text
C1  UI 不得生成、拆分、合并、补全或重排任务
C2  UI 不得从课程草案推导「今天该做什么」
C3  UI 不得用倒计时天数自行推断阶段（如「最后 7 天 = 冲刺」，除非 Planner 输出该语义）
C4  UI 不得把任务数量、时长、配额补成「看起来合理」的默认值
C5  tasks[].ref 只能是指针；UI 不得内联第三方题干、答案、解析、OCR 或 PDF 正文
C6  theme 中的 Knowledge Topic 与 Case Capability 必须分字段渲染（语义隔离）
C7  无计划时，必须可区分「契约未冻结」与「今天确实没有任务」
C8  任务排序与优先级来自 Planner；UI 不得重排
```

---

## 5. PlanTimeline 的 consumer contract

| 项 | 内容 |
|---|---|
| user job | 看清 30 天结构与近期可调整安排 |
| 依赖 | Planner output（Backbone / Rolling 7-Day / Daily） |
| 当前状态 | `EmptyState`「Planner contract 尚未冻结」 |
| 规划字段 | `TBD — dependent on Planner contract`（每天：日序、主题、预计时长、核心目标、任务数量、完成状态、CTA） |
| 计划视图窗口（7 / 14 / 30 天） | 必须来自 Planner；**未冻结时控件不渲染**（不是渲染禁用态 + 假数据） |

**约束**：

```text
1. 三层结构（Backbone / Rolling 7-Day / Daily）的展示区别由 Planner 契约决定，UI 不得自行发明
2. 「可调整窗口」的范围由 Planner 输出；UI 不得让用户调整 Backbone
3. 里程碑（milestone）来自 Planner，不由 UI 用日期推算
```

---

## 6. Explain 链

Planner 冻结后，任务必须可展开解释：

```text
为什么今天安排这个任务？
→ 触发的 rule id
→ 输入信号快照
→ policy / plan version
→ 输出变更
```

| 项 | 约束 |
|---|---|
| rule id | 必须是 Planner 已定义的 rule 标识，不允许匿名逻辑 |
| signal snapshot | 必须来自 engine 输出，不允许 UI 回填 |
| plan version | 必须随 plan 返回 |
| `as_of` | 必须显式；解释必须绑定生成时的 `as_of` |
| 原因缺失 | engine 未输出 → 显示「原因不可用」，**UI 不得推测** |

**当前状态**：Explain 链的字段全部 `TBD — dependent on Planner contract`。

---

## 7. 空态与不可用态（冻结文案）

| 区域 | 当前状态 | 用户可见文案 |
|---|---|---|
| `TodayFocusCard` 任务区 | Planner contract 未冻结 | 「Planner contract 尚未冻结」 |
| `TodayFocusCard` 复习区 | P4.5 domain replay available；Today read model 未实现 | 若 UI 尚未接入，显示实现层 unavailable；不得自行计算 due |
| `PlanTimeline` | Planner contract 未冻结 | 「Planner contract 尚未冻结」 |
| `PlanModeSwitcher` | Planner contract 未冻结 | **不渲染** |
| 冲刺阶段标签 | Planner contract 未冻结 | 「尚未建立契约」（或在 `/settings` 中由用户配置） |

**规则**：空态文案必须说明「为什么没有」，而不是显示一个空的数字或 0 个任务。

---

## 8. 与 User Configuration 的边界

| 概念 | 归属 | 说明 |
|---|---|---|
| 每日可用时间 | `user_config` | 用户声明的容量 |
| 计划容量（planned minutes） | `planner` | Planner 依据可用时间与信号生成的计划额度 |
| 考试日期 | `user_config` | 倒计时输入 |
| 冲刺阶段 | `planner` | 不得由 UI 用倒计时推算 |
| 目标 / 及格线 | `user_config` | 必须标注「目标 / 参考」 |

冻结规则：

```text
user_config 是输入，不是 domain 事实
planner 输出不得被 user_config 直接覆盖
UI 不得把 user_config 值伪装成 Planner 输出
```

---

## 9. 依赖状态汇总

| 依赖项 | 状态 | 阻塞内容 |
|---|---|---|
| Planner output contract | ❌ 未冻结 | Today Card、PlanTimeline、PlanModeSwitcher、冲刺阶段 |
| Planner plan version | ❌ 未冻结 | Explain 可复现性 |
| Planner explain（rule id + signal snapshot） | ❌ 未冻结 | Explain 层 |
| Issue #4（review 区块） | ✅ Phase 4 Gate PASS；P4.5 replay 与全部 fixture / tests / validation 已通过 | Review domain output Available；Today 计划任务仍受 Planner Gate C 阻塞，consumer 实现尚未开始 |
| task execution contract | ❌ 未定义 | 计划完成度、完成日、streak |
| User Configuration contract | ❌ 未定义 | 考试日期、时区、可用时间、目标的持久化与版本 |

**本 PR 的诚实声明**：

```text
Planner dependency = unresolved
本文件只完成 consumer contract 侧规划，Today Card 当前只能显示空态
```

---

## 10. 与其余 UI 文档的关系

| 关注点 | 文档 |
|---|---|
| Today Card 卡片数据语义 | [`COCKPIT_UI_BLUEPRINT.md`](COCKPIT_UI_BLUEPRINT.md) §4.2 |
| Read model（`TodayPlanView`） | [`READ_MODEL_CONTRACT.md`](READ_MODEL_CONTRACT.md) §5.2 |
| 指标 → domain 映射（`planner` 分类） | [`DOMAIN_TO_UI_MAPPING.md`](DOMAIN_TO_UI_MAPPING.md) §6 |
| 路由（`/today`、`/plan`） | [`PAGE_MAP.md`](PAGE_MAP.md) §2.2 / §2.6 |
| 组件边界 | [`COMPONENT_MAP.md`](COMPONENT_MAP.md) |
