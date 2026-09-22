# P4.3 / P4.4 Policy Symbol Freeze Record v0.1

> 本文件是 **P4.3 / P4.4 窗口**对并行测试设计窗口（`test/p4-review-matrix`，已由 PR #6 合并）中
> **owner 为 P4.3 / P4.4 的 policy symbol** 与 **CONTRACT GAP** 的冻结记录。
>
> PR #6 合并后，`data/review/fixture-plan.json` 已在 main 上。本窗口按该 manifest 自己的
> freeze 机制，只把 **owner 为 P4.3 / P4.4 的 20 个 symbol** 从 `status: unfrozen` 更新为
> `status: frozen`。这是 P4.3/P4.4 的历史 freeze record；后续 P4.1/P4.2 contract 与
> P4.5 replay 已在独立文档和 engine 中收口，fixture manifest 的剩余 symbol 仍由 P4.6/P4.7
> 统一升级，不在本文件中回写。

## 0. Policy identity

| 项目 | 冻结值 |
| --- | --- |
| mastery policy | `mastery-policy/spaced-consecutive/v0.1` |
| review policy | `review-policy/simple-ladder/v0.1` |
| projection schema | `review-policy-projection/v0.1`（schema 版本号由 P4.5 / P4.6 命名空间确认） |
| 权威文档 | `MASTERY_POLICY_V01.md`、`REVIEW_SCHEDULING_POLICY_V01.md` |
| 可执行实现 | `engine/rules/review_policy_v01.py` |

---

## 1. P4.3 symbol（mastery）

| Symbol | 冻结值（JSON） |
| --- | --- |
| `MASTERY_STATE_ENUM` | `["new", "learning", "mastered"]` |
| `MASTERY_INITIAL_STATE` | `"new"` |
| `MASTERY_SUCCESS_STREAK_TO_MASTERED` | `{"metric": "consecutive_success_day_count", "min_consecutive_successes": 3, "min_distinct_success_local_dates": 3, "reset_on_failure": true, "same_local_date_repeat_does_not_advance": true}` |
| `MASTERY_FAILURE_TRANSITION` | `{"transition": {"new": "learning", "learning": "learning", "mastered": "learning"}, "resets_consecutive_success": true}` |
| `MASTERY_MASTERED_PERSISTENCE` | `"revocable"` |
| `MASTERY_MASTERED_FAILURE_TRANSITION` | `"demote_to_learning"` |
| `MASTERY_INSUFFICIENT_EVIDENCE_STATE` | `{"effect": "no_change", "counter_field": "insufficient_evidence_count", "is_failure": false}` |
| `MASTERY_ILLEGAL_TRANSITION_POLICY` | `{"policy": "impossible_by_construction", "reason": "transition function is total over (mastery_state, policy outcome)", "input_validation_categories": ["invalid_timestamp", "future_evidence", "duplicate_evidence_id", "invalid_evidence_outcome", "invalid_timezone", "invalid_policy_input"]}` |
| `STATE_FIELD_NAMES` | 见第 3 节 |

## 2. P4.4 symbol（scheduling）

| Symbol | 冻结值（JSON） |
| --- | --- |
| `SCHED_INTERVAL_LADDER` | `[1, 3, 7, 15]` |
| `SCHED_FIRST_DUE_RULE` | `{"no_evidence": "not_scheduled", "anchor": "first_evaluated_evidence.occurred_at", "first_interval_days": 1, "due_local_date": "local_date(anchor, tz) + interval_days"}` |
| `SCHED_SUCCESS_ADVANCE_RULE` | `{"applied_interval_days": "INTERVAL_LADDER_DAYS[min(d - 1, 3)]", "d": "distinct local dates of successes in the current run", "same_local_date": "no_advance", "cap_index": 3}` |
| `SCHED_FAILURE_RESET_RULE` | `{"applied_interval_days": 1, "resets": ["consecutive_success_count", "consecutive_success_day_count"], "demotes_mastered": true}` |
| `SCHED_MASTERED_MAINTENANCE_RULE` | `{"enabled": true, "interval_days": 15, "included_in_due_count": true, "mastery_change_on_success": "none", "mastery_change_on_failure": "demote_to_learning"}` |
| `SCHED_OVERDUE_RULE` | `{"changes_interval": false, "changes_mastery": false, "overdue_starts": "first local midnight after next_due_local_date"}` |
| `SCHED_SAME_DAY_REPEAT_RULE` | `{"counted_as_evidence": true, "advances_interval": false, "changes_due_date": false, "ordering": "(occurred_at_utc, evidence_id) ascending", "duplicate_evidence_id": "reject"}` |
| `SCHED_DUE_COUNT_DEFINITION` | `{"unit": "review_item", "statuses": ["due", "overdue"], "invariant": "due_count == due_today_count + overdue_count"}` |
| `SCHED_DUE_GRANULARITY` | `{"stored": ["next_due_at (UTC instant)", "next_due_local_date (YYYY-MM-DD)"], "canonical": "instant", "due_boundary": "inclusive", "overdue_boundary": "exclusive"}` |
| `SCHED_DATE_BOUNDARY_TIMEZONE` | `{"timezone": "explicit IANA schedule_timezone (required, no implicit default)", "implicit_machine_timezone": "forbidden", "recorded_metadata": ["schedule_timezone", "tzdata_version"], "local_day_start": "earliest instant whose local date >= D"}` |
| `STATE_DUE_PROJECTION_NAMES` | `{"field": "review_status", "values": ["not_scheduled", "scheduled", "due", "overdue"], "reason_field": "review_status_reason", "interval_field": "review_interval_days"}` |

---

## 3. `STATE_FIELD_NAMES`（policy 层字段名，已冻结）

```json
{
  "nesting": "projection.items[review_item_id] = flat item object",
  "item_fields": [
    "review_item_id",
    "mastery_state",
    "mastery_reason",
    "evaluated_evidence_count",
    "successful_review_count",
    "failure_count",
    "insufficient_evidence_count",
    "consecutive_success_count",
    "consecutive_success_day_count",
    "last_review_at",
    "last_evidence_id",
    "review_interval_days",
    "next_due_at",
    "next_due_local_date",
    "review_status",
    "review_status_reason",
    "scheduling_reason"
  ],
  "aggregate": {
    "review": ["total_items", "not_scheduled_count", "scheduled_count", "due_today_count", "overdue_count", "due_count"],
    "mastery": ["new_count", "learning_count", "mastered_count"]
  },
  "metadata": ["schema_version", "policy", "as_of", "schedule_timezone", "tzdata_version"],
  "not_frozen_here": "本文件不重新冻结 MasteryReviewState 顶层 schema；P4.5 已采用 mastery-review-state/v0.1，并补充 replay metadata；不得重命名上述 policy 字段（重命名需要新 policy version）"
}
```

字段的序列化形式：`as_of` / `last_review_at` / `next_due_at` 为 UTC ISO 8601 instant（`+00:00` 形式，
`Z` 为等价输入）；`next_due_local_date` 为 `YYYY-MM-DD`；`review_interval_days` 为整数或 `null`。

---

## 4. CONTRACT GAP 收口

来源：`docs/PHASE4_TEST_MATRIX.md` 第 10 节。

| GAP | owner | 本窗口结论 | 状态 |
| --- | --- | --- | --- |
| GAP-07 mastery 状态枚举与字段名 | P4.3 | 采用两轴分层：`{new, learning, mastered}` + `{not_scheduled, scheduled, due, overdue}`；字段名见第 3 节 | **CLOSED (P4.3)** |
| GAP-08 mastered 持久性与失败行为 | P4.3 / P4.4 | mastered 可撤销；失败降级 `learning`；maintenance 保留，间隔 15 天 | **CLOSED (P4.3 / P4.4)** |
| GAP-09 非法状态跃迁处理 | P4.3 | 不存在非法跃迁（transition total）；拒绝只发生在输入层，category 见 `MASTERY_ILLEGAL_TRANSITION_POLICY` | **CLOSED (P4.3)** |
| GAP-10 interval ladder 与首次 due 基准 | P4.4 | ladder `[1,3,7,15]`；首次 due 以第一条可评估 evidence 的 `occurred_at` 为基准，本地日 + 1 天 | **CLOSED (P4.4)** |
| GAP-11 failure / overdue / 同日重复 | P4.4 | failure 直接重置为 1 天；overdue 不改变 interval；同日重复成功计入计数但不推进间隔、不改变到期日 | **CLOSED (P4.4)** |
| GAP-12 `due_count` 定义与 projection 字段名 | P4.4 | item 数，状态为 `due`/`overdue`；字段名见第 3 节；不变量 `due_count == due_today_count + overdue_count` | **CLOSED (P4.4)** |
| GAP-13 due 粒度与日期边界 timezone | P4.4 | 同时保存 instant 与 local date；边界使用显式 IANA timezone；due 含边界，overdue 从下一个本地 00:00 起 | **CLOSED (P4.4)** |
| GAP-05 success / failure 推导与 insufficient 边界 | P4.2 / P4.5 | comprehensive correctness 由 adapter 确定性映射；score 使用 `review-outcome/raw-facts/v0.1` 保守映射为 `insufficient`，阈值/rubric 仍不得写进 scheduling policy | **PARTIAL（保守 adapter 已冻结，score threshold 仍开放）** |
| GAP-15 同 timestamp tie-breaker | P4.5 | replay 统一按 evidence projection 的 `(occurred_at_utc, evidence_id)` 升序处理；输入事件顺序不影响输出 | **CLOSED (P4.5)** |
| GAP-16 validation error category 命名 | P4.5 | replay 保持 policy categories（`future_evidence` / `invalid_timezone` / `invalid_policy_input` 等），并对 replay envelope 使用 `invalid_replay_input`；拒绝不会静默降级 | **CLOSED (P4.5)** |
| GAP-14 replay API 的 `as_of` / version 输出 | P4.5 | `replay(...)` 显式接收 aware `as_of` 与 IANA `timezone`，输出 schema / policy / adapter / replay metadata | **CLOSED (P4.5)** |
| GAP-17 fixture schema 版本命名 | P4.6 / P4.7 | draft fixture schema 保持 `review-fixture/v0.1-draft`，正式 fixture version 仍待 matrix 收口 | OPEN（P4.6 / P4.7） |

---

## 5. 与测试设计窗口的一致性检查

`fixture-plan.json` 中这 20 个 symbol 已按本文件更新；仍可通过以下断言验证冻结记录与实现一致：

```text
fixture-plan.json policy_symbols[MASTERY_STATE_ENUM].value        == engine.rules.MASTERY_STATES
fixture-plan.json policy_symbols[SCHED_INTERVAL_LADDER].value     == engine.rules.INTERVAL_LADDER_DAYS
fixture-plan.json policy_symbols[MASTERY_SUCCESS_STREAK_TO_MASTERED].value.min_consecutive_successes
                                                                 == engine.rules.MASTERY_MIN_DISTINCT_SUCCESS_DAYS
fixture-plan.json policy_symbols[SCHED_MASTERED_MAINTENANCE_RULE].value.interval_days
                                                                 == engine.rules.MASTERED_MAINTENANCE_INTERVAL_DAYS
```

`tests/test_review_policy.py` 中的 `FrozenContractTests` 与 `DocumentationSyncTests`
已经保证代码常量与文档不会静默漂移。
