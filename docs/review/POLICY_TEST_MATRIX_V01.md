# Policy Test Matrix v0.1

> 本文件是 P4.3 / P4.4 窗口形成的**policy-level 案例设计记录**，曾作为 P4.6 / P4.7 fixture 与边界测试的输入。
> P4.6 / P4.7 已完成：正式 expected outputs 以 `data/review/fixtures/` 为准，36 个冻结 replay fixtures 由 validator 执行；完整矩阵和 Gate 证据见 [`docs/PHASE4_TEST_MATRIX.md`](../PHASE4_TEST_MATRIX.md) 与 [`docs/PHASE4_VALIDATION_REPORT.md`](../PHASE4_VALIDATION_REPORT.md)。
>
> 历史记录：本文件形成时 `tests/test_review_policy.py` 有 38 个案例；当前全量 test count 以 validation report 的实际运行结果为准。
> 历史案例示例使用 `schedule_timezone = Asia/Shanghai`；每次 replay 仍须显式传入 IANA timezone，不存在隐式默认值。

符号：

```text
S = success evidence        F = failure evidence        I = insufficient evidence
D = 本地日历日期（Asia/Shanghai）
d = consecutive spaced-success local dates（首次 success 计入；后续仅 due-boundary success 计入）
```

---

## 1. Mastery

| # | 案例 | 输入 | 期望 |
| --- | --- | --- | --- |
| M1 | 无 evidence | — | `mastery_state = new`，reason `no_evaluated_evidence` |
| M2 | 首次成功 | `S@D1` | `learning`，reason `success_enters_learning`，`d = 1` |
| M3 | 首次失败 | `F@D1` | `learning`，reason `failure_enters_learning`，`d = 0` |
| M4 | 第二次到期成功 | `S@D1, S@D2 (occurred_at >= due)` | `learning`，reason `learning_success_below_mastery`，`d = 2` |
| M5 | 第三次到期成功 | `S@D1, S@D2 (due), S@D5 (due)` | 达到当前 Review Policy mastery 阈值，`d = 3` |
| M6 | 第四次到期 success | `…, S@D4 (due)` | 仍达到当前阈值，reason `mastered_success_maintenance` |
| M7 | 同一天重复成功 | `S@D1 09:00, S@D1 21:00` | `learning`，`d = 1`，interval 不变，due 不变 |
| M8 | `learning` 失败 | `S@D1, F@D2` | `learning`，reason `learning_failure_keeps_learning`，`d = 0` |
| M9 | `mastered` 后失败 | `S@D1, S@D2, S@D3, F@D4` | `learning`，reason `mastered_failure_demotes_learning`，`d = 0` |
| M10 | 累计计数不决定 mastery | `S,S,F,S,S`（due-boundary spaced run） | `successful_review_count = 4`，`mastery_state = learning` |
| M11 | 同日 `S,F,S` 不跳档 | `S@D1 09:00, F@D1 10:00, S@D1 11:00` | failure schedule 保持 1 天；末次 success 是 early，`d = 0`，due `D1 + 1` |
| M12 | 同日失败不可被同日成功撤销 | `F@D1 10:00, S@D1 11:00` | early success 不推进 `d`；interval `1`，`mastery_state = learning` |
| M13 | 仅 evidence 不足 | `I@D1` | `new`，reason `no_evaluated_evidence`，`insufficient_evidence_count = 1`，不排期 |
| M14 | evidence 不足不改变已有状态 | `S@D1, I@D2` | 与仅有 `S@D1` 时完全一致（除 insufficient 计数） |
| M15 | 跨日期但早于 due 的 success | `S@D1, S@D2 (due), S@D3 (before next due)` | success / `last_review_at` 记录；`d`、interval、due 与 mastery 不推进 |

---

## 2. Scheduling

| # | 案例 | 输入 | 期望 |
| --- | --- | --- | --- |
| S1 | 新 item 不排期 | 无 evidence | `next_due_at = null`，`review_status = not_scheduled` |
| S2 | 首次成功后 1 天 | `S@D1 10:00` | `review_interval_days = 1`，`next_due_local_date = D1+1` |
| S3 | 第二次到期成功后 3 天 | `S@D1, S@D2 10:00`（D2 due boundary 已到） | `review_interval_days = 3`，`next_due_local_date = D2+3` |
| S4 | 第三次到期成功后 7 天 | `S@D1, S@D2 (due), S@D5 (due)` | `review_interval_days = 7`，达到当前 mastery 阈值 |
| S5 | 第四次到期 success 后 15 天 | `S@D1, S@D2 (due), S@D5 (due), S@D12 (due)` | `review_interval_days = 15`，`next_due_local_date = D12+15` |
| S6 | failure 后 1 天 | `S@D1, F@D2` | `review_interval_days = 1`，`next_due_local_date = D2+1` |
| S7 | `mastered` 后 failure 复位 | `S@D1, S@D2, S@D3, F@D4` | interval `1`，due `D4+1` |
| S8 | `mastered` maintenance | `S@D1, S@D2, S@D3, S@D4, S@D5` | interval `15`，due `D5+15`，mastery 不变 |
| S9 | overdue 不改变 interval | 到期后 long overdue 再查询 | `review_interval_days` 不变 |
| S10 | 同一天完成复习后不再当天到期 | `S@D1`，`as_of = D1+1 08:00` → `S@D1+1 09:00`，`as_of = D1+1 09:01` | 之前 `due`，之后 `scheduled` |
| S11 | `due_count` 等于 item-level 投影 | 4 个 item（due / scheduled / overdue / new） | `due_count = 2 = due_today_count(1) + overdue_count(1)` |
| S12 | `due_count` 不是事件数 | 同一天对同一 item 多次 review | `due_count` 不因事件数变化 |
| S13 | early success 不滚动 schedule | success 时间早于 previous `next_due_at`，即使跨 local date | 保留 evidence / 成功计数，原 interval 与 due 不变 |

---

## 3. 时间 / 时区

| # | 案例 | 输入 | 期望 |
| --- | --- | --- | --- |
| T1 | 精确到期 | `as_of == next_due_at` | `due`（边界包含） |
| T2 | 到期前 1 微秒 | `as_of = next_due_at - 1µs` | `scheduled` |
| T3 | 到期后 1 微秒 | `as_of = next_due_at + 1µs` | `due` |
| T4 | overdue 起点 | `as_of` = 到期日 + 1 天的本地 00:00 | `overdue` |
| T5 | overdue 前 1 微秒 | `as_of` = 到期日本地 23:59:59.999999 | `due` |
| T6 | 同 instant 不同时区写法 | `10:00+08:00` / `02:00Z` / `03:00+01:00` | 状态完全一致 |
| T7 | UTC 等价 | 与 T6 同 | 状态完全一致 |
| T8 | 不同 `schedule_timezone` | 同一 instant，`Asia/Shanghai` vs `Europe/Berlin` | `next_due_local_date` 与 `review_status` 可不同；这是显式输入差异 |
| T9 | 同 timestamp 两条 evidence | `S`,`F` 同一 instant，不同 `evidence_id` | 按 `evidence_id` 词序应用，结果稳定 |
| T10 | 不同输入数组顺序 | 打乱 events | 结果完全一致 |
| T11 | 本地 00:00 不存在（DST gap） | `America/Santiago` 2019-09-08 | 该本地日最早存在时刻（01:00 本地），`next_due_local_date` 仍为该日 |
| T12 | 整个本地日不存在（跳过日） | `Pacific/Apia` 2011-12-30 | 返回下一个存在日的最早 instant，有效到期日由该 instant 反推 |
| T13 | `as_of` 早于 evidence | `as_of < occurred_at` | 拒绝，category `future_evidence` |
| T14 | `as_of` 等于 evidence 时刻 | `as_of == occurred_at` | 接受并应用 |
| T15 | offset 变化不改变“同一天” | 同一天内两次成功 | `d` 不变，interval 不变 |

---

## 4. Invalid / Rejection

| # | 案例 | 期望 |
| --- | --- | --- |
| R1 | naive timestamp（evidence 或 `as_of`） | `invalid_timestamp` |
| R2 | 重复 `evidence_id` | `duplicate_evidence_id` |
| R3 | 未知 outcome（如实际分数、自由文本） | `invalid_evidence_outcome` |
| R4 | 未知字段（如把 score 直接塞进 policy 输入） | `invalid_policy_input` |
| R5 | `schedule_timezone` 为 `null` / `""` / `local` / `system` / 未知名 | `invalid_timezone` |
| R6 | 非字符串 / 空 `review_item_id` | `invalid_policy_input` |
| R7 | unknown review item | P4.1 已冻结显式 item catalog；未知 item 在 replay 中按 `unknown_review_item` 拒绝，不隐式创建 |
| R8 | 缺少 source reference / 违反版权契约 | 由 P4.1 / P4.2 validator 负责，policy kernel 不接触来源字段 |
| R9 | review evidence 与 item kind 不匹配 | P4.2 contract/replay 校验；不匹配时按 `evidence_item_mismatch` 拒绝 |
| R10 | malformed / negative interval 参数 | 常量不可运行时注入；任何参数变化必须新 policy version |

---

## 5. 必须断言的性质（不变量）

```text
due_count == due_today_count + overdue_count
due_count == count(item for item in items if review_status in {due, overdue})
review_status == not_scheduled  =>  next_due_at is None and mastery_state == new
mastery_state == new            =>  evaluated_evidence_count == 0
mastery_state == mastered       =>  consecutive_success_day_count >= 3（仅首次 / due-boundary spaced success 计数）
insufficient evidence           =>  scheduling unchanged and mastery unchanged
repeatability / input-order independence / as_of determinism
```

`progress-state/v0.1` 的既有 fixture 与语义不因 Phase 4 规则设计而改变。
