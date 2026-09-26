# Review Scheduling Policy v0.1（冻结）

```text
policy_id      review-policy/simple-ladder
policy_version v0.1
status         FROZEN（本窗口 P4.4）
```

机器可读常量：`engine/rules/review_policy_v01.py`
可执行转移测试：`tests/test_review_policy.py`

本文件冻结：interval ladder、scheduling transition、时间语义、failure 语义、mastered maintenance、
`due_count`。本文档本身不实现 replay、不定义 Review Item / Review Evidence contract；P4.1/P4.2 contracts 与 P4.5 replay 已分别冻结 / 实现，完整审计见 [`../PHASE4_VALIDATION_REPORT.md`](../PHASE4_VALIDATION_REPORT.md)。

> 这不是自适应复习算法。没有 SM-2、FSRS、forgetting curve、ease factor、难度参数、AI 判断、
> 个性化权重或 planner。policy 的全部输入是：item 的 policy-eligible evidence、显式 `as_of`、
> 显式 IANA timezone 与冻结的 policy version。

---

## 1. Option A vs Option B

必须先在两个简单方案中做出选择，而不是默认沿用课程草案的 `1 / 3 / 7 / 15` 写法。

### Option A — 字面草案

```text
success: 1 -> 3 -> 7 -> 15      （可变 ladder 指针，成功时 +1）
failure: reset -> 1             （指针清零）
next_due = last_evidence_instant + interval 天（同一时刻偏移）
```

### Option B — 日历锚定 + 派生 ladder（**选定**）

```text
applied_interval(success) = LADDER[min(d - 1, 3)]     # d = 当前 run 的 spaced-success 日期数
applied_interval(failure) = LADDER[0] = 1
next_due_local_date       = local_date(evidence, tz) + applied_interval 天
next_due_at               = start_of_local_day(next_due_local_date, tz)
```

即：间隔值仍然是 `1 / 3 / 7 / 15`，但

1. ladder 位置不再是可变指针，而是当前 run 的**派生函数**；
2. 到期时间是**本地日历日 00:00 锚定**，不是 `occurred_at + N × 86400s`。

### 对比

| 维度 | Option A | Option B | 结论 |
| --- | --- | --- | --- |
| 解释性 | “指针现在在第几档”需要读历史猜 | “这个 run 里有几次达到 due boundary 的 spaced success”可从 evidence 重建 | B |
| 实现复杂度 | 需要额外可变状态 + 同一天防刷逻辑 | 两个派生量；同一天重复成功天然幂等 | B |
| failure 语义 | 指针清零，语义清楚 | run 清零 + 间隔 1 天，语义相同且副作用可见 | 平（B 更可解释） |
| mastered maintenance | 指针顶格后无定义行为 | 顶格即 15 天 maintenance，自然衔接 | B |
| 时间边界 | 23:50 成功 → 次日 23:50 才 due；“今天到期”会随钟点抖动 | 到期日 00:00 起即 due；与“今天”对齐 | B |
| 未来升级成本 | 指针状态需要迁移 | 只改 `LADDER` / transition，历史 evidence 不变 | B |

**决定：v0.1 采用 Option B。** 它没有改变草案的间隔数值，但把语义从“可变指针 + 时刻偏移”
改为“派生 ladder + 本地日历日锚定”。理由记录见第 11 节。

---

## 2. Policy identity 与参数

```text
policy_id       review-policy/simple-ladder
policy_version  v0.1

interval_ladder_days                [1, 3, 7, 15]
failure_interval_days               1                # == ladder[0]
mastered_maintenance_interval_days  15               # == ladder[max]
same_day_success_advances_interval  false
overdue_changes_interval            false
insufficient_evidence_changes_state false
due_boundary                        local_day_start_inclusive
overdue_boundary                    first_local_midnight_after_due_local_date
evidence_ordering                   utc_instant_then_evidence_id
future_evidence                     reject
```

spaced-success eligibility 沿用现有 due contract：首次 success 没有 previous due，允许建立第一阶；之后仅当
`evidence.occurred_at >= previous next_due_at`（due boundary 含等号）时才推进 `d` / ladder。Early success
仍计为 success evidence，但保留已有 interval / due，不推进 spaced mastery。

约束：

- ladder 必须非递减、正整数；`failure_interval_days` 必须等于 ladder 首项；
- `mastered` 的 maintenance 间隔必须等于 ladder 末项；
- 任何参数变化都必须产生新的 `policy_version`，不允许原地修改 v0.1。

---

## 3. Scheduling transition table

设 `D = local_date(evidence.occurred_at, schedule_timezone)`，`previous_due_at` 为应用本条 evidence 前已有的 due instant，
`d' = 应用本条 evidence 之后的 spaced-success 日期数`。首次 success 没有 `previous_due_at`，视为可推进；后续
success 只有在 `evidence.occurred_at >= previous_due_at` 时才可推进。

| # | Condition | interval | next_due_local_date | Reason code |
| --- | --- | --- | --- | --- |
| S1 | 无 evidence | — | 不排期 | `no_evidence_not_scheduled` |
| S2 | success 且（无 previous due 或 `occurred_at >= previous_due_at`），spaced 日期新增 | `LADDER[min(d'-1,3)]` | `D + interval` | `success_schedules_ladder_interval` |
| S3 | success 与上一条 success 同一本地日期 | 不变 | 不变 | `same_day_success_keeps_schedule` |
| S4 | success `occurred_at < previous_due_at`，且不是同一本地日期 | 不变 | 不变（保持原 due） | `early_success_keeps_schedule` |
| S5 | `failure` | `1` | `D + 1` | `failure_schedules_retry_interval` |
| S6 | `insufficient` | 不变 | 不变 | （无 scheduling transition） |

时间投影（无新 evidence）：

| # | Prior status | 条件 | Next status |
| --- | --- | --- | --- |
| P1 | `not_scheduled` | 出现在 S2 / S5 之后 | `scheduled` 或 `due` |
| P2 | `scheduled` | `as_of >= next_due_at` | `due` |
| P3 | `due` | `local_date(as_of) > next_due_local_date` | `overdue` |
| P4 | `due` / `overdue` | S2 / S5 把 `next_due_at` 推到 `as_of` 之后 | `scheduled` |
| P5 | `due` / `overdue` | 时间继续流逝 | 保持；**不改变 interval、不改变 mastery** |

`review_status_reason`：

```text
not_scheduled_no_evaluated_evidence
scheduled_due_in_future
due_on_due_local_date
overdue_since_next_local_date
```

---

## 4. Interval 语义

| 事件 | 应用的 interval（天） | 说明 |
| --- | --- | --- |
| 第 1 次 spaced success | 1 | 首次 success 无 previous due；建立 1 天 due |
| 第 2 次 spaced success | 3 | 达到前一次 due boundary 后成功；3 天后到期 |
| 第 3 次 spaced success | 7 | 再次达到 due boundary 后成功；达到当前 mastery 阈值 |
| 第 4 次及以后 spaced success | 15 | maintenance 顶格 |
| early success（跨 local date 也一样） | 不变 | 记录成功，但不推进 ladder、不滚动原 due |
| failure | 1 | 无论此前在哪个档次 |
| 同一天重复成功 | 不变 | 不缩短也不延长 |
| `overdue` | 不变 | overdue 是投影，不是惩罚 |

`review_interval_days` 的语义被冻结为：

```text
用于计算当前 next_due_at 的那个 interval（单位：本地日历日）
```

它在 `not_scheduled` 时为 `null`。它不表示“距离上次复习已经过了多少天”，
也不表示“下次间隔预计会是多少”。

---

## 5. 时间语义（重点）

### 5.1 冻结结论

```text
存储 / 计算：timezone-aware instant（UTC 为规范形式）
日期投影：  显式 IANA timezone（schedule_timezone，例如 Asia/Shanghai）
到期表示：  next_due_at（instant）+ next_due_local_date（本地日期）同时保存
```

- `review_due_at` **是 instant**，不是 local date；local date 是它的派生物。
- 两者同时保存，因为 Gate 需要回答“今天哪些到期”（日期问题）与“是否已经到达”（时刻问题）。
- 不允许隐式使用运行机器 timezone。禁止 `datetime.now()`、`date.today()`、
  无参数 `astimezone()`；`schedule_timezone` 必须是显式 IANA 名称，
  传入 `local` / `system` / 空值一律拒绝（`invalid_timezone`）。

### 5.2 到期基准：本地日历日 00:00

```text
next_due_local_date = local_date(evidence, tz) + interval 天
next_due_at         = start_of_local_day(next_due_local_date, tz)
```

`start_of_local_day(D, tz)` 被定义为：**本地日期等于 `D`（或在其之后）的最早 instant**。

- 正常情况：`D` 当天本地 00:00；
- 本地 00:00 不存在（DST gap，例如 `America/Santiago` 2019-09-08）：该本地日期的最早存在时刻（01:00 本地）；
- 整个本地日期不存在（被跳过的日历日，例如 `Pacific/Apia` 2011-12-30）：
  返回下一个存在日期的最早 instant，并**用返回的 instant 重新计算有效到期日期**。

因此 `next_due_local_date` 的冻结语义是：

```text
next_due_local_date = local_date(next_due_at, tz)      # 有效日期，而非请求日期
```

这样 overdue 判定与 due 判定在所有时区下都保持一致。

### 5.3 首次 due 的基准

v0.1 不为“从未有 evidence 的 item”排期：

```text
new item + 无 evidence -> next_due_at = null, review_status = not_scheduled
```

第一次到期时间是**第一条可评估 evidence 的 `occurred_at`** 所在本地日 + interval：

- 首次成功 → `D + 1 天`；
- 首次失败 → `D + 1 天`（reason 不同）。

即 v0.1 不使用“首次暴露 + 1 天”的隐式规则；首次排期由第一条 evidence 决定。
Evidence 是否产生由 P4.1/P4.2 的显式 Review Context 与事实契约约束；scheduling policy 不从“首次学习”或日期间隔推断 evidence。无 evidence item 不排期，第一条可评估 evidence 是 v0.1 排期锚点。

### 5.4 success / failure 后的 due

见第 3、4 节。要点：

- 首次 / due-boundary success：间隔由 spaced-success run 派生，到期日锚定该 success 的本地日期，不从上一次 due 日期累加；
- early success（`occurred_at < previous next_due_at`）：仍是有效 evidence，但不推进间隔 / `d`，保持原 interval 与 due；更新成功计数和 `last_review_at`；
- failure：间隔重置为 1 天，到期日 = `D + 1`；
- 同一天内的重复成功不改变到期日（幂等）；不同 local date 的 early success 也不改变原 due；
- `overdue` 本身不改变 interval，但到期后成功可以正常推进 ladder。

### 5.5 到期边界

| 情形 | 结论 |
| --- | --- |
| `as_of < next_due_at` | `scheduled` |
| `as_of == next_due_at`（精确到期时刻） | `due`（**包含**边界） |
| `next_due_at < as_of`，且本地日期仍等于到期日期 | `due` |
| `local_date(as_of) > next_due_local_date` | `overdue` |

即：

```text
due      = (as_of >= next_due_at) and (local_date(as_of) == next_due_local_date)
overdue  = local_date(as_of) > next_due_local_date
```

overdue 从**到期日之后的第一个本地 00:00** 开始，而不是从 `next_due_at + 24h` 开始，
也不是从某个宽限期开始。

因为 `next_due_at` 永远是本地日 00:00，所以“在到期日当天完成复习”一定会把 `next_due_at`
推到下一个本地日 00:00 之后，item 当天不会再出现在到期集合里。

### 5.6 排序与重复

```text
evidence 排序键 = (occurred_at 转换到 UTC, evidence_id) 升序
```

- 与 `progress-replay/v0.1` 的 `(UTC instant, event_id)` 规则一致；
- 输入数组顺序不影响结果；
- 同一时间戳的多条 evidence 按 `evidence_id` 词序应用，结果稳定；
- 同一天多次 review 全部计入 evidence 计数；对 scheduling 而言重复成功是幂等的；
- 不同 local date 但发生在 `previous next_due_at` 之前的 success 同样属于 early review，不推进 spaced-success day count；
- 重复 `evidence_id` 直接被拒绝，v0.1 不做静默去重；
- P4.2 已冻结 deterministic `evidence_id = evidence/{source_event_id}/{review_item_id}`；因此排序键中的 ID 稳定且无需 fallback。

### 5.7 `as_of` 与 future evidence

```text
发生时刻 == as_of  -> 接受并应用
发生时刻  > as_of  -> 拒绝，category = future_evidence
```

v0.1 选择**fail closed**：replay 不会静默丢弃未来事实，也不会泄漏未来事实。
需要“只回放到某时刻”的调用方应传入覆盖该时刻的 `as_of`。
（“显式标记并排除”作为未来扩展，不进入 v0.1。）

### 5.8 时区等价与 UTC 等价

- `2026-03-01T10:00+08:00`、`2026-03-01T02:00Z`、`2026-03-01T03:00+01:00` 是同一 instant，
  在相同 `schedule_timezone` 与相同 policy 下产生**完全相同**的状态；
- 相同 instant、不同 `schedule_timezone` 可能产生不同的 `next_due_local_date` 与不同 `review_status`；
  这是显式输入差异，不是不确定性；
- 时间相关输出必须记录 `schedule_timezone` 与 `tzdata_version`（本地日边界依赖 tzdata）。

### 5.9 确定性要求

```text
same evidence (same evidence_ids, same instants, same outcomes)
+ same policy version
+ same as_of
+ same schedule_timezone
+ same tzdata
= byte-identical projection
```

不依赖：系统当前时间、运行机器 timezone、输入数组顺序、字典迭代顺序、
上一次 aggregate state、AI 判断。

---

## 6. Mastered maintenance

| 方案 | 行为 | 评价 |
| --- | --- | --- |
| A | `mastered` 后不再排期（graduate） | 简单、`due_count` 自然下降；但长期不再回访，真考前的遗忘无法被复习发现；未来 policy 升级需要“取消毕业”的迁移 |
| B | `mastered` 后保留 maintenance 间隔（15 天） | 语义连续；`due_count` 仍可解释；failure 仍可降级；未来 policy 升级只需重算 |

**决定：v0.1 采用 B。**

- `mastered` item 保持 `review_status ∈ {scheduled, due, overdue}`，间隔固定为 ladder 末项 15 天；
- 达到 due boundary 后的 maintenance success 不改变 mastery（`mastered_success_maintenance`），并按 15 天滚动 due；early success 保留 evidence，但不提前滚动 maintenance due；
- maintenance 失败降级为 `learning`，并按 failure 语义安排 1 天后复习；
- `due_count` **包含** maintenance 到期 item（见第 8 节），否则 `due_count` 将不再等于
  item-level due 投影数量。

`mastered` 不是一个终止状态，这是与 Option A 的本质区别。

---

## 7. Failure 语义

failure 表示“有明确事实表明这次没有答对/没有达到成功标准”。它**不包含**以下情形：

```text
未作答 / 缺考
证据不足（insufficient evidence）
数据缺失
实际 0 分（是否算 failure 由 P4.2 outcome 映射决定）
```

字段变化：

| 字段 | spaced success | success（同一天 / early） | failure | insufficient |
| --- | --- | --- | --- | --- |
| `evaluated_evidence_count` | +1 | +1 | +1 | 不变 |
| `successful_review_count` | +1 | +1 | 不变 | 不变 |
| `failure_count` | 不变 | 不变 | +1 | 不变 |
| `insufficient_evidence_count` | 不变 | 不变 | 不变 | +1 |
| `consecutive_success_count` | +1 | +1 | **= 0** | 不变 |
| `consecutive_success_day_count` | +1 | 不变 | **= 0** | 不变 |
| `last_review_at` | 更新 | 更新 | 更新 | **不变** |
| `review_interval_days` | `LADDER[min(d-1,3)]` | 不变 | **= 1** | 不变 |
| `next_due_at` / `next_due_local_date` | 重算 | 不变 | `D + 1` | 不变 |
| `mastery_state` | 见 mastery 文档 | 不变 | `mastered → learning`，其余不变 | 不变 |

必须分别验证的三个场景：

| 场景 | 结果 |
| --- | --- |
| `learning` → failure | 仍 `learning`；run 清零；1 天后复习 |
| `due` → failure | 状态不变（due 只是投影）；1 天后复习；overdue 不额外惩罚 |
| `mastered` → failure | 降级 `learning`；run 清零；1 天后复习 |

补充冻结规则：

- early success 仍增加 `evaluated_evidence_count`、`successful_review_count`、`consecutive_success_count`，并更新 `last_review_at`；不增加 `consecutive_success_day_count`，不改变 mastery / interval / due；
- 同一天内 “success → failure → success” 不会恢复到原 interval：失败当天的重新成功只得到 1 天间隔；
- 同一本地日内多次成功不推进 interval，也不推进 mastery；
- failure 之后的下一次成功按 `d = 1` 重新起算，因此间隔仍为 1 天，再下一次为 3 天。

---

## 8. `due_count` 语义

```text
due_count = 在 as_of 时刻，review_status ∈ {due, overdue} 的 review item 数量
```

冻结分解：

```text
due_count        == due_today_count + overdue_count
due_today_count  == review_status == "due" 的 item 数
overdue_count    == review_status == "overdue" 的 item 数
```

不变量（必须被测试断言）：

```text
due_count == count(item for item in items if item.review_status in {due, overdue})
```

规则：

- 统计单位是 **item**，不是 event；同日多次 review 不会增加 `due_count`；
- `scheduled` 与 `not_scheduled` 不计入；
- `mastered` 的 maintenance 到期计入；
- `overdue` item 计入 `due_count`（它仍然需要今天处理）。

拒绝的替代定义：把 `due_count` 定义为“截至 `as_of` 的 evidence 条数”或“今天的 review 事件数”；
那会让 `due_count` 不再是可执行的任务量，并与 item-level 到期集合不一致。

---

## 9. Item-level projection fields（供 P4.5 replay / P4.6 fixtures 使用）

以下是 policy kernel 目前输出的字段。**语义与字段名已由本窗口（P4.3 / P4.4）冻结**；
`MasteryReviewState v0.1` 的 schema、顶层对象名与 replay metadata 已由 P4.5 命名为
`mastery-review-state/v0.1`。重命名这些 policy 字段需要新的 policy version。

```text
review_item_id
mastery_state                    new | learning | mastered
mastery_reason                   <mastery reason code>
evaluated_evidence_count
successful_review_count
failure_count
insufficient_evidence_count
consecutive_success_count
consecutive_success_day_count
last_review_at                   UTC instant | null    # 最近一条“可评估”evidence
last_evidence_id                 str | null            # 最近一条 evidence（含 insufficient）
review_interval_days             int | null
next_due_at                      UTC instant | null
next_due_local_date              YYYY-MM-DD | null
review_status                    not_scheduled | scheduled | due | overdue
review_status_reason             <status reason code>
scheduling_reason                <scheduling reason code>
```

Aggregate：

```text
review.total_items
review.not_scheduled_count
review.scheduled_count
review.due_today_count
review.overdue_count
review.due_count
mastery.new_count / learning_count / mastered_count
```

Metadata（必须记录，用于解释与重建）：

```text
schema_version                  review-policy-projection/v0.1
policy.mastery_policy_id / .mastery_policy_version
policy.review_policy_id / .review_policy_version
policy.parameters
as_of                           UTC instant
schedule_timezone               IANA name
tzdata_version
```

历史可解释性：v0.1 不保存隐藏的 transition log；任意历史状态都可以用较小的 `as_of`
重新 replay 得到。Gate 的“为什么今天到期”由
`(last_evidence_id, scheduling_reason, review_interval_days, next_due_local_date, review_status_reason, policy version, as_of)`
共同回答。

---

## 10. Examples

使用 `Asia/Shanghai`。

| 事件 | occurred_at（本地） | interval | next_due_local_date | next_due_at (UTC) | `as_of` | status |
| --- | --- | --- | --- | --- | --- | --- |
| success（首次） | 03-01 23:50 | 1 | 03-02 | 03-01T16:00Z | 03-02 20:00 | `due`（整天 due，不因 23:50 抖动） |
| success | 03-02 09:00 | 3 | 03-05 | 03-04T16:00Z | 03-02 20:00 | `scheduled` |
| success（同日再来一次） | 03-02 21:00 | 3 | 03-05 | 03-04T16:00Z | 03-02 21:01 | `scheduled`（不变） |
| failure | 03-05 10:00 | 1 | 03-06 | 03-05T16:00Z | 03-05 20:00 | `scheduled` |
| success | 03-06 10:00 | 1 | 03-07 | 03-06T16:00Z | 03-06 20:00 | `scheduled` |

时间边界示例：

| 查询 `as_of` | 结果 |
| --- | --- |
| `03-01T23:59:59.999999+08:00` | `scheduled` |
| `03-02T00:00:00+08:00` | `due`（边界包含） |
| `03-02T00:00:00.000001+08:00` | `due` |
| `03-02T23:59:59.999999+08:00` | `due` |
| `03-03T00:00:00+08:00` | `overdue` |

---

## 11. Rejected Alternatives

| 方案 | 拒绝理由 |
| --- | --- |
| `occurred_at + N × 86400s` 的纯时刻偏移 | “今天到期”会随上次复习钟点漂移；跨 DST 会偏移；23:50 复习导致次日 23:50 才 due |
| 到期时间使用运行机器本地时区 | 违反确定性；`AGENTS.md` 要求显式输入 |
| 只存 local date，不存 instant | 无法表达“精确到期时刻”与跨时区比较；无法验证 UTC 等价性 |
| 只存 instant，不存 local date | “今天到期”无法脱离 tz 重新计算；Gate 的可解释性变差 |
| overdue 触发额外惩罚（缩短间隔） | 把投影混入规则；用户无法解释；未来 planner 才应该处理优先级 |
| overdue 达到阈值后降级 mastery | 时间流逝不是证据；会制造无 evidence 的 mastery 跃迁 |
| 可变 ladder 指针 + 同一天防刷补丁 | 隐藏状态更多；同一天重复成功天然幂等更简单 |
| failure 只降一档而不是重置 | “失败后 3 天再复习”对学习者为反直觉；v0.1 优先可解释 |
| mastered 后 graduation（不再排期） | 见第 6 节 |
| `due_count` 采用事件计数 | 不是可执行任务量；与 item-level 投影不一致 |
| `as_of` 之后的事件静默忽略 | 会静默泄漏未来事实，破坏可解释性与确定性 |
| 允许 `insufficient` evidence 触发 1 天后重试 | v0.1 保持“无 policy outcome ⇒ 无排期变化”；留给未来 `unresolved_review_queue` |
| 引入 SM-2 / FSRS / forgetting curve | 参数、迁移与解释成本过高；且违反 Issue #4 Out of Scope |
| 引入 AI 判断 `review_due` | 违反 `AGENTS.md` 的 deterministic 指标要求 |

---

## 12. Future Extensions（不实现）

- v0.2 ladder / 参数化 policy（必须新 policy version，历史 replay 保留 v0.1）；
- `unresolved_review_queue`：`insufficient` evidence 的显式再访问队列；
- 按 item kind 区分的 interval ladder；
- `as_of` 早于 evidence 时的显式 `exclude_future` 模式；
- planner 层的到期优先级（与 policy 分离）；
- tz 变更（用户跨时区）时的显式迁移规则。
