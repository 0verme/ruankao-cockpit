# Today / Planner UX Contract v0.1

> **状态**：PLANNING CONTRACT（Issue #5 · UI.6）
> **依赖**：Planner Output v0.1 contract（P5.3 已冻结；Planner replay / output generation 未实现）+ Issue #4 domain replay（**P4.5 已完成**）
> **重要声明**：本文件只冻结「UI 如何消费 Planner 输出」的规划。Planner output schema 见 [`docs/planner/PLANNER_OUTPUT_CONTRACT_V01.md`](../planner/PLANNER_OUTPUT_CONTRACT_V01.md)；本文件不实现 Planner。
> **备注**：下方的 `review.*` domain 值由 `MasteryReviewState v0.1` replay 提供；本文件不直接调用 policy kernel。

---

## 1. 当前实现状态

```text
Planner replay / output generation  ❌ 不存在（P5.3 Output contract 已冻结）
30-Day Plan 实例化                    ❌ 不存在（30-Day Curriculum 仍为 DRAFT）
Rolling 7-Day output structure        ✅ P5.3 contract 已冻结；尚未生成
Daily Adaptive Tasks                  ❌ 不存在（P5.6 replay 尚未实现）
task execution contract               ❌ 不存在
plan completion                       ❌ 不存在
Today Plan output                     ❌ 尚未生成；consumer alias 为 PlannerOutput.days[0]
policy / as_of / Explain structure     ✅ output contract 已冻结；尚无执行结果
```

现状证据：

- `engine/rules/README.md` 的 **计划形态（Future）** 明确把 Backbone / Rolling / Daily 三层列为未来工作。
- `README.md` 的当前状态把 `Adaptive Planner`、`30-Day Plan` 标为 ⏳。
- `docs/architecture/README.md` 把 `Adaptive Planner` 与 `Cockpit UI` 标为 ⏳，并说明本阶段未实现 planner。

因此：

```text
TodayFocusCard 的 Planner 任务区当前状态 = EmptyState（Planner output 未生成，Phase 5 Gate 未通过）
复习 domain 数据源 = P4.5 replay 可用；Today read model / UI 仍未实现
```

---

## 2. 三种计划形态必须区分（核心冻结决策）

UI 与文档必须严格区分三种不同事物：

| 形态 | 定义 | 来源 | 当前状态 |
|---|---|---|---|
| **Static Curriculum** | 课程设计草案：阶段划分、原则、候选规则 | `docs/30_DAY_CURRICULUM_DRAFT.md` | **DRAFT**，不是 contract |
| **Generated Plan** | 由 Planner 生成的计划 projection | P5.3 PlannerOutput contract | 🟡 结构已冻结（Today + Rolling 7-Day）；生成器未实现 |
| **Adaptive Daily Plan** | Task Execution 后根据事实重排的当日任务 | Future contract / replay | ❌ 未冻结；不属于 P5.3 projection |

**UI 最终只消费 Planner 输出**，不得消费 Static Curriculum，也不得自行生成 Adaptive 结果。

```text
Static Curriculum  ✗→ UI
Generated Plan      ✓→ UI（PlannerOutput 已生成且 Gate C 解锁后）
Adaptive Daily Plan ✓→ UI（Execution / adaptive contract 冻结后；非 P5.3）
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

### 4.1 当前（Planner output 尚未生成）

| 项 | 内容 |
|---|---|
| 显示内容 | 空态：「Planner 尚未生成计划」（Phase 5 Gate 未通过） |
| 允许的字段 | 无（Planner output 尚未生成；有效空计划须由已生成的 output 显式表达） |
| CTA | 不渲染可用 CTA（不得指向伪造任务流） |
| Explain | 不渲染（无原因可解释） |
| 禁止 | 渲染任何任务、天数、主题、时长、进度 |

### 4.2 PlannerOutput v0.1 consumer projection

```text
Today = PlannerOutput.days[0]               # 唯一数据源，不存在独立 today payload
day_offset / local_date / study_day          PlanDay v0.1
capacity_minutes / planned_minutes           PlanDay v0.1
remaining_minutes / tasks[] / unmet_demand[] PlanDay v0.1
tasks[].task_id / task_type / target_kind / target_ref / planned_minutes / explain_trace_id
                                               PlanTask v0.1；当前 task_type 仅 review
planner_policy / input_snapshot_schema_version / as_of / timezone
                                               PlannerOutput v0.1
explain_traces[]                              结构化 trace；业务 reason code 留给 P5.4
plan_phase / theme / cta_target / required    不属于 P5.3 output contract
completion / actual_minutes                   无 Task Execution contract，禁止消费或推断
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
C5  `target_ref` 只能是稳定指针；UI 不得内联第三方题干、答案、解析、OCR 或 PDF 正文
C6  theme 中的 Knowledge Topic 与 Case Capability 必须分字段渲染（语义隔离）
C7  必须区分「Planner 尚未生成 output」与「有效 output 中今天 tasks=[]」
C8  任务排序与优先级来自 Planner；UI 不得重排
```

---

## 5. PlanTimeline 的 consumer contract

| 项 | 内容 |
|---|---|
| user job | 查看 Planner 提供的近期 7 日 projection；30-Day Backbone 当前仍为 DRAFT / Future |
| 依赖 | P5.3 PlannerOutput 的 Rolling 7-Day `days[]`（Today 取 `days[0]`）；30-Day Backbone 与 execution 不属于本 contract |
| 当前状态 | `EmptyState`「Planner 尚未生成计划」 |
| 输出字段 | `days[].local_date / study_day / capacity_minutes / planned_minutes / remaining_minutes / tasks[] / unmet_demand[]`；无 completion / phase / CTA 字段 |
| 计划视图窗口 | v0.1 固定为 7 日；没有 14 / 30 日切换契约，不渲染切换控件 |

**约束**：

```text
1. P5.3 只冻结 Rolling 7-Day projection；不输出 30-Day Backbone 实例或 Task Execution
2. PlanTimeline 只投影 PlannerOutput.days[]；UI 不得自行补全或重排
3. P5.3 不包含 plan_phase、milestone、task completion 或视图窗口切换
```

---

## 6. Explain 链

Planner output 生成后，每个 task / unmet demand 必须引用 `explain_trace_id`；结构化字段见 P5.3 `ExplainTrace`（policy identity/version、input JSON Pointer、target、decision category、reason_code slot、structured_inputs）。P5.3 不冻结业务 reason code / priority basis；AI 或 UI 不得补猜。

| 项 | 约束 |
|---|---|
| `input_references` | P5.3 使用指向完整 input snapshot 的 JSON Pointer |
| `planner_policy` / `target` | 随 trace 返回，且必须与 PlannerOutput / subject 一致 |
| `as_of` | 必须显式；Explain 绑定生成时的 `as_of` |
| `display_message` | 可选展示投影，不是 machine source；结构化字段才是机器依据 |
| 原因缺失 | 无 Planner output 时维持不可用空态；AI/UI 不得补猜 |

**当前状态**：P5.3 Explain 容器结构已冻结；Planner 尚无执行结果。

---

## 7. 空态与不可用态（冻结文案）

| 区域 | 当前状态 | 用户可见文案 |
|---|---|---|
| `TodayFocusCard` 任务区 | P5.3 contract 已冻结；Planner generation / Phase 5 Gate 未完成 | 「Planner 尚未生成计划」 |
| `TodayFocusCard` 复习区 | P4.5 domain replay available；Today read model 未实现 | 若 UI 尚未接入，显示实现层 unavailable；不得自行计算 due |
| `PlanTimeline` | Rolling 7-Day 结构已冻结；output generation 未实现 | 「Planner 尚未生成计划」 |
| `PlanModeSwitcher` | v0.1 只冻结 7 日 horizon | **不渲染**（无其它窗口 contract） |
| 冲刺阶段标签 | P5.3 未定义阶段 / milestone | 「尚未建立契约」 |

**规则**：空态文案必须说明「为什么没有」，而不是显示一个空的数字或 0 个任务。

---

## 8. 与 User Configuration 的边界

| 概念 | 归属 | 说明 |
|---|---|---|
| 每日可用时间 | `user_config` v0.1 | 用户声明的输入容量；与 output 的 `capacity_minutes` 是不同字段语义 |
| 计划容量（capacity / planned minutes） | `planner` | P5.3 output 字段；具体分配策略留给 P5.4 |
| 考试日期 | User Configuration v0.1 **未包含** | 倒计时另需经审查的配置契约；Planner 不推断 |
| 冲刺阶段 | `planner` | P5.3 未定义；不得由 UI 用倒计时推算 |
| 目标 / 及格线 | User Configuration v0.1 **未包含** | 必须等待独立配置契约，不得假称当前可用 |

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
| Planner output contract | ✅ P5.3 已冻结；replay / output generation 未实现 | Today Card 与 Rolling 7-Day consumer 仍受 Phase 5 Gate 阻塞 |
| Planner policy identity/version | ✅ P5.3 output metadata 有结构槽位；实际可执行 identity 规则留给 P5.4 | Explain 可追踪 policy；无独立 plan instance version |
| Planner Explain | ✅ P5.3 trace 容器已冻结；业务 reason code / policy basis 留给 P5.4 | Explain 展示层消费结构化 trace |
| Issue #4（review 区块） | ✅ Phase 4 Gate PASS；P4.5 replay 与全部 fixture / tests / validation 已通过 | Review domain output Available；Today 计划任务仍受 Planner Gate C 阻塞，consumer 实现尚未开始 |
| task execution contract | ❌ 未定义 | 计划完成度、完成日、streak |
| User Configuration v0.1 | ✅ P5.2 已冻结（timezone / daily_available_minutes / study_days） | `exam_date`、目标与偏好不在 v0.1 |

**本 PR 的诚实声明**：

```text
Planner output schema = frozen (P5.3)
Planner execution / Phase 5 Gate = unresolved
本文件只完成 consumer contract 侧规划，Today Card 当前只能显示「尚未生成计划」空态
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
