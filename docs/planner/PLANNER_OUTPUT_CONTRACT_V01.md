# Planner Output Contract v0.1（P5.3）

> **范围：冻结“计划长什么样”。** 本文定义 Planner 输出 projection 的结构和机器验证约束；不定义如何选择、排序、分配容量或解释某个业务优先级，也不实现 Planner replay。

## 1. 定位与事实边界

```text
PlannerOutput = deterministic projection
PlannerOutput != Progress Fact
PlannerOutput != Review Evidence
PlannerOutput != Task Completion
```

删除旧 PlannerOutput 后，相同完整输入快照与相同执行 policy 必须可重新生成相同输出。PlannerOutput 不得含 `completed`、`done`、`actual_minutes`、`streak`、`completion_rate` 等执行结果；本契约没有 Task Execution。

输出中的分钟是计划估算，单位为整数分钟。`planned_minutes` 不是实际耗时；review policy、真实复习 due 和 mastery 仍只来自 P4 的 `MasteryReviewState v0.1`，Planner 不重算。

## 2. 顶层模型与元数据

机器 Schema：[`data/planner/planner-output.schema.json`](../../data/planner/planner-output.schema.json)。顶层结构：

```json
{
  "schema_version": "planner-output/v0.1",
  "planner_policy": {"policy_id": "…", "policy_version": "…"},
  "input_snapshot_schema_version": "planner-input/v0.1",
  "as_of": "2026-01-01T00:00:00Z",
  "timezone": "Asia/Shanghai",
  "generated_for_local_date": "2026-01-01",
  "horizon": {"unit": "local_calendar_days", "day_count": 7},
  "days": [],
  "explain_traces": []
}
```

- `planner_policy` 是实际生成本计划的 policy identity/version；P5.1 的 `planner-policy/input-contract/v0.1` 仍是**非执行输入契约标记**，不能被冒充为执行 policy。执行 identity 的具体规则由 P5.4 冻结。
- 输出固定回显输入 schema 版本、显式 `as_of`、显式 IANA timezone 和 policy identity/version。
- **不定义 input digest/hash。** P5.1 提供确定性 `canonical_json`，但没有 digest 契约；ProgressState v0.1 也没有 event digest。输出不声称具有完整 input-content fingerprint。需要精确重建时，调用方须保留相应完整 input snapshot；不得用上述元数据假装唯一内容身份。
- `generated_for_local_date` 是 `as_of` 在 `timezone` 下的本地日期，不是机器日期。

## 3. Today 与 Rolling 7-Day

唯一正式表示为 `PlannerOutput.days[7]`，不另存 `today` 或独立 Today Plan 对象：

```text
today consumer alias = days[0]
```

因此不会出现 Today 与 Rolling `days[0]` 双份状态漂移。UI consumer 应从 `days[0]` 投影 Today。

窗口为 **7 个连续本地日历日**：

```text
Day 0 = generated_for_local_date
Day 1 = Day 0 + 1 local calendar date
...
Day 6
```

本地日期边界只由输出 timezone 决定；不得按机器时区或固定 24 小时推算跨 DST 日期。`day_offset` 固定对应数组位置 `0..6`。

## 4. PlanDay

每个 `days[]` 元素包含：

| 字段 | 语义 |
|---|---|
| `day_offset` | Horizon 内偏移，0–6，必须等于数组索引 |
| `local_date` | 连续的 ISO 本地日期 |
| `study_day` | 对 `UserConfiguration.study_days` 的确定性投影（ISO weekday） |
| `capacity_minutes` | 此日 Planner 声明的计划容量，整数分钟；是否在 rest day 设为 0 不由 P5.3 决定 |
| `planned_minutes` | 分配给本日 tasks 的计划分钟总数 |
| `remaining_minutes` | 未分配容量 |
| `tasks` | 已纳入本日计划的 PlanTask |
| `unmet_demand` | 合法但未被纳入本日计划的需求 |

所有分钟字段为 `0..1440` 整数。冻结不变量：

```text
0 <= planned_minutes <= capacity_minutes
remaining_minutes = capacity_minutes - planned_minutes
sum(tasks[].planned_minutes) = planned_minutes
capacity_minutes = 0 => tasks = []
```

不允许隐藏 planning overhead。`study_day` 可从配置确定，但其 capacity 值与排程处理方式仍属 P5.4；P5.3 不推断非学习日容量。

### 合法空状态

容量为正、无合法 demand 时可以合法输出空日：`tasks=[]`、`planned_minutes=0`、`remaining_minutes=capacity_minutes`、`unmet_demand=[]`。容量为 0 也合法；tasks 必须为空。存在但未排入的合法 demand 用 `unmet_demand` 表达。未知 / malformed / unsupported input 应 fail closed，不能变成 unmet demand。

## 5. PlanTask v0.1

```json
{
  "task_id": "stable opaque id",
  "task_type": "review",
  "target_kind": "review_item",
  "target_ref": "review/topic/DATA.DATABASE.RELATIONAL",
  "planned_minutes": 10,
  "explain_trace_id": "trace-id"
}
```

- **v0.1 唯一支持 task type：`review`**。MasteryReviewState 中存在正式且稳定的 review target；不从其余候选列表推导支持能力。
- 唯一支持的 target kind 为 `review_item`；`target_ref` 是 Review Model 已冻结的 canonical `review_item_id`，不是 label / 题干 / 自由文本：`review/topic/<topic_id>`、`review/question/<source_id>/<source_question_id>` 或 `review/case_capability/<capability_id>`。引用必须在本次有效 MasteryReviewState input 中存在。
- Topic、Case Capability ID catalog 的存在不等于存在对应的 `new_learning` / `case_practice` target 来源。P5.3 不纳入 `new_learning`、`practice`、`case_practice`；`essay`、`mock_exam` 也不支持。
- `planned_minutes` 为 `0..1440` 整数分钟，是 projection，不是实际用时。
- 不定义 `required` 或 priority 字段：前者的业务含义依赖 P5.4 selection policy；priority 的表示与语义也留给 P5.4。

### task_id identity semantics

`task_id` 必须稳定且确定性生成，不得随机生成 UUID。它表示以下语义身份的确定性编码：

```text
planner policy namespace + policy version
+ local_date + task_type + target_kind + canonical target_ref
```

相同 semantic task 与相同 replay 必须产生相同 `task_id`。v0.1 不冻结拼接、散列或其它具体编码算法；任务时长、展示文案和 Explain 内容不是 task identity 的组成部分。Output 内 task ID 必须唯一。

## 6. UnmetDemand

```json
{
  "demand_id": "stable opaque id",
  "demand_type": "review",
  "target_kind": "review_item",
  "target_ref": "review/topic/DATA.DATABASE.RELATIONAL",
  "requested_minutes": 10,
  "explain_trace_id": "trace-id"
}
```

此结构只表示**来源合法、但未被安排的 demand**，不表示 invalid/unsupported input。v0.1 `demand_type` 仅为 `review`，与当前支持 target 对齐。`requested_minutes` 是请求的计划分钟数（整数分钟），不是已分配或实际耗时。task 与 unmet demand 不允许在同一天重复表示同一个 review target。

`demand_id` 的稳定身份由 policy namespace/version、本地日期、demand type、target kind/ref 组成；不得随机生成，编码算法不在 P5.3 冻结。什么 demand 会被保留、推迟或列出均由 P5.4 / P5.5 决定。

## 7. ExplainTrace

`explain_traces[]` 是结构化 explain 容器，不是自然语言字段。每个 task 和 unmet demand 必须引用恰好一个 trace；不得有孤立或重复 trace。

每个 trace 固定包含：

```text
trace_id
subject_kind / subject_id
decision_category
reason_code
planner_policy.policy_id / policy_version
input_references[]          # 指向输入快照的 JSON Pointer
target_kind / target_ref
structured_inputs           # 结构化对象槽位
```

`reason_code` 是 machine-readable string slot，不冻结 P5.4 业务枚举；`decision_category` 仅区分 `task_scheduled` / `demand_unmet` 两种结构输出。`structured_inputs` 的具体键和值由相应 policy 决定；trace policy 必须与输出顶层一致，input reference 必须指向本次 input snapshot 的有效 JSON Pointer，target 必须与其 subject 一致。

可选 `display_message` 仅供展示，不能成为机器决策依据。自然语言不得作为唯一解释来源。

`trace_id` 在一个输出内唯一，并依据其 policy namespace/version、subject kind/id 与 decision category 稳定生成；不冻结具体编码算法，不得随机生成。

## 8. Validator 与错误语义

扩展现有 `scripts/validate_planner_contract.py`；只验证 schema 和 synthetic contract fixtures，不调用任何 schedule / allocate / replay 函数。校验包括：

- output schema / version、policy metadata、input schema / `as_of` / timezone traceability；
- IANA timezone、本地生成日期、7 日连续日期、study-day 投影与 day offset；
- target 格式与有效 input 的 Review Item identity；
- 唯一 task / demand / trace identity，Explain 引用、policy 与 target 一致性；
- 分钟范围、task minute sum、capacity / remaining 守恒及零容量约束；
- fail-closed 闭合对象，不接纳 execution 字段或未支持 task / target 类型。

## 9. 明确未冻结

### UNFROZEN — P5.4

```text
task ordering
priority semantics
review debt ordering
overdue vs due priority
capacity allocation
task duration policy
required / optional selection policy
unmet demand selection
stable tie-break business rule
执行 policy identity 如何进入受支持的 Planner input envelope
```

### UNFROZEN — P5.5

```text
new learning topic source
curriculum backbone
coverage-based selection
topic progression
prerequisite semantics
```

P5.3 冻结输出结构，不回答为什么选 A 而不选 B。`docs/30_DAY_CURRICULUM_DRAFT.md` 继续保持 DRAFT；Rolling 7-Day 不隐含 30 天实例化。P5.6 replay、P5.7 behavior fixtures、Task Execution、UI/API/DB 均不在本轮范围。
