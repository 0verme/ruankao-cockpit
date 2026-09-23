# Phase 4 Test Matrix（P4.6 / P4.7）

> 状态：`REVIEW_FIXTURE_MATRIX_FROZEN` / `P4.7_COMPLETE`
>
> P4.6 已冻结 36 个 `mastery-review-fixture/v0.1` fixtures；P4.7 已补足边界、rejection、determinism、timezone 与 aggregate invariant tests。`scripts/validate_review.py` 报告 `REVIEW_FIXTURE_MATRIX_PASS`。
>
> P4.6/P4.7 矩阵本身只验证 fixture 与测试覆盖，不改变 P4.1～P4.5 冻结契约。P4.8 Documentation / Architecture Sync、P4.9 正式验证报告已完成；Phase 4 Gate 结论见 [`docs/PHASE4_VALIDATION_REPORT.md`](PHASE4_VALIDATION_REPORT.md)。
>
> 下方矩阵表保留 PR #6 的设计条目与原始设计时状态。**最终实现状态以 `data/review/fixture-plan.json`、当前 fixtures 和 unittest 为准**；表中 `SYMBOLIC` / `BLOCKED` 是历史设计快照，不代表当前仍待 freeze。

---

## 0. 状态图例

| 状态 | 含义 |
| --- | --- |
| `READY` | 只依赖已冻结契约或跨 policy 的相对性质，现在就可以执行并通过 |
| `SYMBOLIC` | 断言形式已确定，但具体状态名 / 阈值 / 天数必须等 policy freeze 后填入 |
| `BLOCKED:P4.x` | 连断言对象（字段名、事件形态、错误 category）都尚未冻结 |

实现类型：

| 实现 | 位置 | 说明 |
| --- | --- | --- |
| `fixture` | `data/review/fixtures/<fixture_id>.json` | 事实 + `expected` / `expected_error`，由 validator 与 unittest 参数化执行 |
| `harness` | `tests/reviewkit.py` + `tests/test_review_determinism_harness.py` | 性质 / metamorphic 测试，不需要单独 fixture 文件 |
| `static` | `tests/test_review_determinism_harness.py` | 源码静态扫描（禁止 wall-clock / 隐式时间） |
| `regression` | `tests/test_progress_v01_regression.py` | Phase 3 语义冻结基线，已经可执行（manifest 中为 `implemented`） |

机器可读清单：[`data/review/fixture-plan.json`](../data/review/fixture-plan.json)。
本文档与 manifest 必须保持一致（由 `tests/test_review_fixture_plan.py` 交叉检查）。

---

## 1. 两类测试与 policy symbol 机制

### 1.1 contract-independent invariants（现在就能落地）

只依赖元性质、相对关系或已冻结契约：

```text
same canonical object      → same review_item_id
display name / 题干变化     → identity 不变
policy version 变化         → identity 不变
shuffle(events)            → same result
replay(x)                  → replay(x)
UTC 等价 instant            → same result
zero / failure / unanswered / insufficient / null 两两可区分
due_count                  == len(due projection)
Progress Replay v0.1       → 语义不漂移
```

这些断言不引用任何具体阈值、天数或状态名字面量。

### 1.2 contract-dependent expectations（已由 P4.1～P4.5 freeze）

依赖状态名、interval 或 rejection category 的断言，现在都从正式 contract / replay contract 取得 expected。manifest 中的 `policy_symbols` 已全部冻结并带 `frozen_by`；P4.6 fixture 同时记录 `policy_symbols` 与 `contract_refs`。没有新阈值或 outcome 规则在本轮加入。

### 1.3 Policy symbol 机制（当前状态）

`fixture-plan.json` 的 36 个 symbols 均为 `status: frozen`。P4.3/P4.4 值来自冻结 policy；P4.1/P4.2/P4.5 值来自 Review Model、Evidence、raw-facts adapter 和 replay contract。score adapter 继续把 supported score 映射为 `insufficient`，没有 threshold/rubric。

---

## 2. 测试矩阵

### A. Identity / Review Item

| ID | 测试目标 | 断言要点 | 依赖 | 实现 | 状态 |
| --- | --- | --- | --- | --- | --- |
| A1 | 同一 canonical 对象身份稳定 | 同一 `(item_kind, canonical reference)` 得到同一个 id（只比较相等/不等，不比较字面量） | P4.1 | fixture `id-same-canonical-object` | SYMBOLIC |
| A2 | display name 变化 | 仅改展示名 → id 与 state 不变（metamorphic） | P4.1 | fixture `id-display-name-change` | SYMBOLIC |
| A3 | 题干文本变化 | 同一 `source_question_id` 下文本变化 → identity 不变 | P4.1 | fixture `id-question-text-change` | SYMBOLIC |
| A4 | policy version 变化 | mastery/review policy 升级 → identity 不变，但输出记录新版本 | P4.1 / P4.5 | fixture `id-policy-version-change` | SYMBOLIC |
| A5 | unknown item | evidence 指向未注册 item → 拒绝，禁止隐式创建 | P4.1 | fixture `invalid-unknown-review-item` | BLOCKED:P4.1 |
| A6 | duplicate item | 同一 id 的重复声明 → 拒绝，不静默去重 | P4.1 | fixture `invalid-duplicate-item` | BLOCKED:P4.1 |
| A7 | alias | alias 解析到唯一 canonical item，不产生第二个 state | P4.1 | fixture `id-alias-resolution` | BLOCKED:P4.1 |
| A8 | missing canonical reference | 缺 topic / question / capability 引用 → 拒绝，不复制正文补洞 | P4.1 / P4.2 | fixture `invalid-missing-canonical-reference` | BLOCKED:P4.1 |
| A9 | unsupported item kind | 未支持 kind → 拒绝，不降级成 topic | P4.1 | fixture `invalid-unsupported-item-kind` | BLOCKED:P4.1 |
| A10 | 三类 item 隔离 | topic / question / case_capability 同名不共享 state，不跨粒度升级 | P4.1 | fixture `id-kind-isolation` | SYMBOLIC |

### B. Review Evidence

| ID | 测试目标 | 断言要点 | 依赖 | 实现 | 状态 |
| --- | --- | --- | --- | --- | --- |
| B1 | 综合题正确 | `correct: true` 是唯一的综合题 success 事实来源 | P4.2 | fixture `evidence-comprehensive-correct` | BLOCKED:P4.2 |
| B2 | 综合题错误 | `correct: false` → failure，且不等于 unanswered | P4.2 | fixture `evidence-comprehensive-incorrect` | BLOCKED:P4.2 |
| B3 | 案例总分 | score evidence 是否 success 由版本化规则决定，不复制到 capability | P4.2 | fixture `evidence-case-score` | BLOCKED:P4.2 |
| B4 | capability 分数 | 只有实际 `capability_scores` 才产生 capability evidence | P4.2 | fixture `evidence-capability-score` | BLOCKED:P4.2 |
| B5 | capability 缺证据 | 只有引用、无分数 → `insufficient_evidence`，不是 failure | P4.2 | fixture `evidence-capability-missing` | SYMBOLIC |
| B6 | insufficient evidence | 有独立表示，不伪装成 new / learning / mastered | P4.2 / P4.3 | fixture `evidence-insufficient` | BLOCKED:P4.3 |
| B7 | 真实 0 分 | 0 分是 sufficient evidence，不能与 insufficient 合并 | P4.2 | fixture `evidence-zero-score` | BLOCKED:P4.2 |
| B8 | unanswered | 未作答不产生 failure evidence，不改变 mastery | P4.2 | fixture `evidence-unanswered` | BLOCKED:P4.2 |
| B9 | unknown topic | 拒绝 | P4.2 | fixture `invalid-unknown-topic` | READY（沿用 Phase 3 语义） |
| B10 | unknown capability | 拒绝 | P4.2 | fixture `invalid-unknown-capability` | READY（沿用 Phase 3 语义） |
| B11 | kind mismatch | evidence 与 item kind 不匹配 → 拒绝 | P4.2 | fixture `invalid-evidence-kind-mismatch` | BLOCKED:P4.2 |
| B12 | duplicate source event | 同一 source event 重复计入 → 拒绝或按显式规则处理 | P4.2 | fixture `invalid-duplicate-source-event` | BLOCKED:P4.2 |
| B13 | missing source reference | 缺 source reference → 拒绝 | P4.1 / P4.2 | fixture `invalid-missing-source-reference` | BLOCKED:P4.1 |
| B14 | illegal source path | 绝对路径 / 目录穿越 / 本地路径 → 拒绝 | P4.2 | fixture `invalid-illegal-source-path` | READY（沿用 Phase 3 语义） |
| B15 | naive timestamp | timezone-naive → 拒绝 | P4.2 | fixture `invalid-naive-timestamp` | READY（沿用 Phase 3 语义） |
| B16 | 语义不可混淆 | `zero`、`failure`、`unanswered`、`insufficient_evidence`、`null` 五种表示两两不同 | P4.2 / P4.3 | fixture `evidence-null-not-conflated` | SYMBOLIC |

### C. Mastery State

| ID | 测试目标 | 断言要点 | 依赖 | 实现 | 状态 |
| --- | --- | --- | --- | --- | --- |
| C1 | new item | 无 evidence 的初始状态 | P4.3 | fixture `mastery-new-item` | BLOCKED:P4.3 |
| C2 | first evidence | 首次 evidence 后的状态（状态名符号化） | P4.3 | fixture `mastery-first-evidence` | BLOCKED:P4.3 |
| C3 | first success | 首次成功后的状态与计数 | P4.3 | fixture `mastery-first-success` | BLOCKED:P4.3 |
| C4 | repeated success | 连续成功推进（阈值引用 symbol，不写死数字） | P4.3 | fixture `mastery-repeated-success` | BLOCKED:P4.3 |
| C5 | learning failure | 失败后的降级、计数、transition reason | P4.3 | fixture `mastery-learning-failure` | BLOCKED:P4.3 |
| C6 | mastered | 达到 mastered 的条件 | P4.3 | fixture `mastery-mastered` | BLOCKED:P4.3 |
| C7 | mastered success | mastered 后再次成功的行为 | P4.3 | fixture `mastery-mastered-success` | BLOCKED:P4.3 |
| C8 | mastered failure | mastered 失败后的行为（降级 / 保持 / maintenance） | P4.3 | fixture `mastery-mastered-failure` | BLOCKED:P4.3 |
| C9 | insufficient evidence | 证据不足时状态与其记录方式 | P4.3 | fixture `mastery-insufficient-evidence` | BLOCKED:P4.3 |
| C10 | illegal transition | 非法跃迁被拒绝或按显式规则记录 | P4.3 | fixture `invalid-illegal-transition` | BLOCKED:P4.3 |

### D. Scheduling

| ID | 测试目标 | 断言要点 | 依赖 | 实现 | 状态 |
| --- | --- | --- | --- | --- | --- |
| D1 | first due | 首次复习基准事实时间与到期规则 | P4.4 | fixture `sched-first-due` | BLOCKED:P4.4 |
| D2 | before due | `as_of < due` → 不计入 due | P4.4 | fixture `sched-before-due` | BLOCKED:P4.4 |
| D3 | exactly due | `as_of == due` 的包含性 | P4.4 | fixture `sched-exact-due` | BLOCKED:P4.4 |
| D4 | after due | `as_of > due` → 计入 due | P4.4 | fixture `sched-after-due` | BLOCKED:P4.4 |
| D5 | overdue | overdue 的表示，以及是否改变下一次 interval | P4.4 | fixture `sched-overdue` | BLOCKED:P4.4 |
| D6 | success advance | interval 推进；`1/3/7/15` 只是 `SCHED_INTERVAL_LADDER` 的候选值 | P4.4 | fixture `sched-success-advance` | BLOCKED:P4.4 |
| D7 | failure reset | interval reset / downgrade 与 transition reason | P4.4 | fixture `sched-failure-reset` | BLOCKED:P4.4 |
| D8 | mastered maintenance | mastered 后是否仍安排 maintenance review | P4.4 | fixture `sched-mastered-maintenance` | BLOCKED:P4.4 |
| D9 | malformed interval | negative / 非整数 interval → 拒绝 | P4.4 | fixture `invalid-negative-interval` | BLOCKED:P4.4 |
| D10 | overflow interval | 越界 interval → 拒绝，不产生异常 due 时间 | P4.4 | fixture `invalid-overflow-interval` | BLOCKED:P4.4 |

### E. Determinism

| ID | 测试目标 | 断言要点 | 依赖 | 实现 | 状态 |
| --- | --- | --- | --- | --- | --- |
| E1 | repeat replay | `replay(x) == replay(x)` | P4.5 | harness `assert_replay_properties` | READY（harness 已自测） |
| E2 | shuffled input | 多个固定 seed 的 shuffle 结果一致 | P4.5 | harness | READY（harness 已自测） |
| E3 | same timestamp ordering | 同 instant 多事件由稳定 tie-breaker 决定，输入顺序无关 | P4.5 | fixture `determinism-same-timestamp-ordering` | SYMBOLIC |
| E4 | UTC equivalent timestamps | `Z` / `+08:00` / `+09:00` 表示同一 instant → 同结果 | P4.5 | harness + fixture | READY（harness 已自测） |
| E5 | same instant timezones | fixture 级验证同一 instant 的多种时区表示 | P4.5 | fixture `determinism-same-instant-timezones` | SYMBOLIC |
| E6 | derived state rebuild | 删除派生 state 后由 events + policy + `as_of` 重建一致 | P4.5 | harness | READY（harness 已自测） |
| E7 | no hidden state | 重新实例化 engine 结果一致；replay 不修改输入 | P4.5 | harness（含 input mutation 检查） | READY（harness 已自测） |

### F. as_of

| ID | 测试目标 | 断言要点 | 依赖 | 实现 | 状态 |
| --- | --- | --- | --- | --- | --- |
| F1 | before all evidence | 早于全部事件：按冻结语义拒绝或排除，不得泄漏未来事实 | P4.5 | fixture `determinism-asof-before-all-evidence` | SYMBOLIC |
| F2 | exactly at event | `as_of == occurred_at` 的包含性 | P4.5 | fixture `determinism-asof-exactly-at-event` | BLOCKED:P4.5 |
| F3 | after event | 晚于事件 → 证据必须计入 | P4.5 | fixture `determinism-asof-after-event` | SYMBOLIC |
| F4 | before future event | `as_of` 位于已发生与未来事件之间：未来事实不得泄漏 | P4.5 | fixture `determinism-asof-before-future-event` | SYMBOLIC |
| F5 | future evidence rejection | 拒绝语义下必须报错；exclude 语义下必须等价于过滤后 replay | P4.2 / P4.5 | fixture `invalid-future-evidence` + harness 双模式 | SYMBOLIC |
| F6 | no system clock leakage | 静态扫描 replay / policy 路径不得出现 wall-clock API | P4.5 | static `scan_for_wall_clock` | READY |

### G. Timezone

| ID | 测试目标 | 断言要点 | 依赖 | 实现 | 状态 |
| --- | --- | --- | --- | --- | --- |
| G1 | UTC | UTC 基线结果 | P4.5 | fixture `time-utc-baseline` | SYMBOLIC |
| G2 | Asia/Shanghai | 显式 `timezone` 参数，不依赖本机时区 | P4.4 / P4.5 | fixture `time-same-instant-timezones` | BLOCKED:P4.4 |
| G3 | Asia/Tokyo | 同上，东九区边界 | P4.4 / P4.5 | 同上 | BLOCKED:P4.4 |
| G4 | UTC equivalent instants | 同一 instant 的三种表示结果一致 | P4.5 | 同上 + harness | READY（harness 已自测） |
| G5 | local date boundary | 同一 instant 在不同 timezone 可能属于不同 local day | P4.4 | fixture `time-local-date-boundary` | BLOCKED:P4.4 |
| G6 | 23:59:59 | 当日末尾边界 | P4.4 | fixture `time-end-of-day` | BLOCKED:P4.4 |
| G7 | 00:00:00 | 次日起点边界 | P4.4 | fixture `time-start-of-day` | BLOCKED:P4.4 |
| G8 | DST-sensitive | 含夏令时的 timezone 不产生隐式本机依赖 | P4.4 | fixture `time-dst-sensitive` | BLOCKED:P4.4 |

### H. due_count

| ID | 测试目标 | 断言要点 | 依赖 | 实现 | 状态 |
| --- | --- | --- | --- | --- | --- |
| H1 | 数量一致性 | `due_count == len(items where due projection ∈ due/overdue)` | P4.4 | harness | SYMBOLIC |
| H2 | item 级计数 | 同一 item 多条 evidence 只计一次，不按事件计数 | P4.4 | fixture `sched-due-count-item-level` | BLOCKED:P4.4 |
| H3 | as_of 语义 | due_count 是截至 `as_of` 的 item 数，不是事件数或未来项 | P4.4 | fixture `sched-due-count-as-of` | BLOCKED:P4.4 |
| H4 | projection 一致性 | 不存在只在计数里出现的 due item（无孤立计数） | P4.4 | harness | SYMBOLIC |

### I. Backward Compatibility（Phase 3 回归矩阵）

| ID | 测试目标 | 断言要点 | 依赖 | 实现 | 状态 |
| --- | --- | --- | --- | --- | --- |
| I1 | existing fixtures | 9 个合法 fixture 的 ProgressState projection + digest 冻结 | — | `tests/test_progress_v01_regression.py` | READY |
| I2 | case score | 加权案例分数 7/10 语义不变 | — | 同上 | READY |
| I3 | errors | error mix / unclassified 语义不变 | — | 同上 | READY |
| I4 | study minutes | 时长事实语义不变 | — | 同上 | READY |
| I5 | ordering | `UTC(occurred_at) + event_id` 排序不变 | — | 同上 | READY |
| I6 | duplicate ID / zero / null | 拒绝与 null 语义不变 | — | 同上 | READY |
| I7 | unknown refs / naive timestamp | 拒绝 category 不变 | — | 同上 | READY |
| I8 | state 不含 Phase 4 字段 | ProgressState 不得出现 mastery / review_* / due_* | — | 同上 | READY |
| I9 | validators | `validate_progress.py`、`validate_taxonomy.py` 继续 PASS | — | 同上 | READY |

---

## 3. Fixture 结构与命名

### 3.1 目录边界

```text
data/review/                       ← Phase 4 独立域，不与 progress fixture 混放
├── TEST_ASSETS.md                 ← 本目录边界与当前状态
├── fixture-plan.json              ← P4.6/P4.7 冻结 manifest
├── fixture-schema.v0.1.json       ← mastery-review-fixture/v0.1 正式 schema
└── fixtures/                      ← 36 个 ready synthetic replay fixtures
    └── <fixture_id>.json
```

选择 `data/review/` 而不是 `data/progress/review-fixtures/` 的理由：review 域有独立的
policy version、`as_of` 和 fixture schema；放在 progress 目录下会被误认为
`progress-model/v0.1` 的一部分。

### 3.2 fixture 字段（正式 `mastery-review-fixture/v0.1`）

正式 schema 位于 `data/review/fixture-schema.v0.1.json`。fixture 包含显式 `as_of` / IANA timezone、frozen policy identities、`contract_refs`、Progress / Review events 与 Review Items；`expected` 是 `MasteryReviewState` 的递归子集，`expected_error` 是正式 rejection category，二者互斥。`variants` 可改变 `as_of` / timezone 或完整 replay input，以覆盖共享事实下的边界。

P4.1/P4.2 的 contract fixtures 仍独立使用 `review-fixture/v0.1`，不与本 schema 混用。

### 3.3 命名规则

```text
<fixture_id>.json
<prefix>-<kebab-slug>
```

| prefix | 覆盖范围 |
| --- | --- |
| `id-` | A. Identity |
| `evidence-` | B. Review evidence |
| `mastery-` | C. Mastery state |
| `sched-` | D. Scheduling / H. due_count |
| `determinism-` | E. Determinism / F. as_of |
| `time-` | G. Timezone |
| `compat-` | I. Backward compatibility |
| `invalid-` | 跨 section 的拒绝矩阵 |

`invalid-*` 可承载任一 section 的拒绝样本；其余 prefix 必须与 matrix section 一致。
该规则由 `tests/test_review_fixture_plan.py` 强制。

### 3.4 内容约束

所有 fixture 必须 synthetic：

```text
不复制第三方题干
不复制选项 / 答案 / 解析
不放 OCR / PDF 正文
只使用最小 canonical / source reference
```

loader 会拒绝 `stem` / `prompt` / `options` / `answer` / `analysis` /
`reference_answer` / `ocr_text` / `full_text` 等字段。

---

## 4. Determinism 测试（本窗口重点）

`tests/reviewkit.py::assert_replay_properties` 保留用于 harness 自测；真实 Review replay 由 `assert_review_replay_properties` 检查：

```text
1. input immutability       replay 不得修改输入事件
2. repeatability            replay(x) == replay(x)
3. order independence       shuffle(events, seed) → same result（多个 seed）
4. as_of echo               结果必须记录请求的 as_of
5. future evidence          reject: 必须报错；exclude: 必须等于过滤后 replay
6. UTC equivalence          改写 offset 后结果不变
```

失败时汇总**全部**问题再抛出 `DeterminismViolation`，而不是只报第一个。

harness 自身由 `tests/test_review_determinism_harness.py` 用 test double 验证：

| 测试 | 验证目标 |
| --- | --- |
| `test_reference_stub_satisfies_every_property` | 合规 stub 必须通过全部检查 |
| `test_harness_rejects_order_dependent_replay` | 顺序依赖会被抓到 |
| `test_harness_rejects_hidden_state` | 隐藏状态 / 计数残留会被抓到 |
| `test_harness_rejects_input_mutation` | 修改输入会被抓到 |
| `test_harness_rejects_missing_as_of_echo` | 不记录 `as_of` 会被抓到 |
| `test_harness_rejects_string_sorted_timestamps` | 字符串排序 timestamp 会被抓到 |
| `test_harness_checks_as_of_is_honoured` | 忽略 `as_of` 会被抓到 |
| `test_harness_exclude_mode_detects_future_leak` | exclude 语义下的未来事实泄漏会被抓到 |
| `test_harness_reject_mode_detects_missing_rejection` | reject 语义下不报错会被抓到 |

参考 stub 只是 test double，**不是** production policy，不得进入 `engine/`。

### 静态守卫

`scan_for_wall_clock` 扫描 `engine/progress/`、`engine/review/` 以及
`replay*` / `policy*` / `scheduler*` / `mastery*` / `review*` 模块，禁止：

```text
datetime.now()  datetime.utcnow()  datetime.today()
date.today()    time.time()        time.monotonic()
datetime.fromtimestamp()
```

当前扫描目标包含 `engine/progress/`、`engine/review/` 与 policy modules；P4.5 Review replay 已在静态 wall-clock guard 覆盖范围内。

---

## 5. Time / Timezone 测试

```text
instant 语义     : 所有时间必须是 timezone-aware instant，UTC 归一化后比较
UTC 等价         : 2026-09-21T10:00:00+00:00 == 2026-09-21T18:00:00+08:00
timezone 输入    : 显式参数（fixture 的 timezone 字段），禁止读取本机时区
local date 语义  : P4.4 冻结为本地日历日边界，fixtures 覆盖 due 前 / exact / overdue
DST             : America/Santiago 的 midnight gap 有 fixture，timezone 显式传入
```

测试不假设产品主要时区；`Asia/Shanghai`、`Asia/Tokyo`、`America/New_York`
都是显式输入。`TZ` 环境变量不得影响结果（可在未来加一条子进程测试）。

---

## 6. 非法输入与拒绝

机器可读清单见 manifest 中 `expected_kind: error` 的条目。共性要求：

```text
1. 拒绝必须是显式 validation error，不得静默跳过或去重
2. validation error 必须使用 P4.1/P4.2/P4.5 冻结的稳定 category
3. 拒绝时不得产出部分 state
4. null / insufficient / unanswered / zero / failure 不得互相伪装
```

v0.1 选择 `reject`；未来 evidence fixture 验证 category=`future_evidence`。Harness 支持 exclude test double，但 production contract 不提供 exclude 模式。

---

## 7. Backward Compatibility

`tests/test_progress_v01_regression.py` 冻结 Phase 3 语义（Phase 4 全量验证继续运行）：

* 基线文件 `tests/baselines/progress_v01_semantics.json`
  记录每个 fixture 的 canonical digest + 无损语义 projection + 拒绝 category；
* projection 会剔除默认 topic/capability 模板，并单独断言被剔除项确实等于默认值；
* 同时校验 repeatability 与 3 个固定 seed 的 shuffle 一致性；
* ProgressState 不得出现 `mastery` / `review_*` / `due_*` 等字段；
* `validate_progress.py` 与 `validate_taxonomy.py` 必须继续 PASS。

重新生成基线只允许在语义变更经过独立评审时进行：

```bash
REGEN_PROGRESS_BASELINE=1 python3 -m unittest discover -s tests -p 'test_progress_v01_regression.py'
```

---

## 8. Validator 策略

决定：**新增** `scripts/validate_review.py`，不扩展 `scripts/validate_progress.py`。

理由：review 域有独立 contract / policy version 和 fixture schema；
塞进 progress validator 会让 `progress-model/v0.1` 的边界模糊。

当前 `scripts/validate_review.py` 的职责：

```text
1. 校验 frozen fixture schema、manifest、contract refs 与盘上 fixture 一致
2. 用 P4.5 replay 执行每个 fixture / variant，精确验证 expected state 子集或 rejection category
3. 校验 MasteryReviewState schema、版本/as_of/timezone、evidence trace 与 item/aggregate invariants
4. 对成功 fixture 验证 repeatability、输入顺序、同 instant offset 与 future evidence rejection
5. 仅报告 `REVIEW_FIXTURE_MATRIX_PASS`；不宣布 Phase 4 Gate PASS
```

P4.8 documentation sync 与 P4.9 validation report 不属于本 validator 的检查范围；二者已单独完成，Phase 4 Gate 结论见 [`docs/PHASE4_VALIDATION_REPORT.md`](PHASE4_VALIDATION_REPORT.md)。

---

## 9. P4.6 / P4.7 收口记录

```text
1. 36 个 policy symbols 均冻结并记录 frozen_by
2. 36 个 ready fixtures 已落盘，fixture schema 为 mastery-review-fixture/v0.1
3. success / rejection expected 均由 P4.1～P4.5 frozen contract 支撑
4. validator 已对 fixtures/variants 执行 schema、expected、category 与 determinism 检查
5. P4.7 补足 due/calendar/timezone/DST/tie-order/failure/score/aggregate edge tests
6. Progress v0.1 regression 保持独立执行；本矩阵不单独判定 Phase 4 Gate（最终结论见 P4.9 report）
```

P4.8 architecture/documentation sync 与 P4.9 validation report 已完成；本文件保留矩阵设计历史，最终 Gate 证据见 [`docs/PHASE4_VALIDATION_REPORT.md`](PHASE4_VALIDATION_REPORT.md)。

---

## 10. CONTRACT GAP 清单（历史设计登记，按 P4.1～P4.7 结论更新）

PR #6 合并时登记的 GAP-01～GAP-17 原始描述保留作审计历史，不再代表当前阻塞。状态汇总：

- GAP-01～04、06：P4.1/P4.2 已冻结 Review Item identity/catalog、context/evidence projection 与去重边界。
- GAP-05：综合题 boolean 已有 raw-facts adapter；case/capability score 保持 `insufficient`，score threshold/rubric 有意留给未来 adapter，未猜测规则。
- GAP-07～13：P4.3/P4.4 policy、interval、failure、timezone、due projection 与 aggregate 字段已冻结。
- GAP-14～16：P4.5 已冻结 `as_of`、版本 metadata、tie-break 与 rejection categories。
- GAP-17：P4.6 已冻结 `mastery-review-fixture/v0.1`，contract fixtures 仍保持独立 schema。
- Alias catalog input 与 runtime interval override 不属于 frozen v0.1 replay API；manifest 标记为 `not_applicable`，不发明额外业务规则。

### GAP-01 review_item_id 组成未冻结

* Gap：`review_item_id` 的 namespace / 组成 / 版本前缀未定义。
* Why it prevents deterministic test：A1–A4、A7、A10 只能做相对断言，无法写出稳定 id；
  跨 fixture 复用与身份迁移无法验证。
* Required decision：id 组成规则、是否含 model/version namespace、迁移策略。
* Owner：P4.1 / P4.2。

### GAP-02 review item registry 来源未定义

* Gap：合法 item 从哪里注册（taxonomy / golden set / 新 catalog 文件）。
* Why it prevents deterministic test：fixture 的 `items` / `references` 字段无法确定；
  unknown item 与 duplicate item 的判定对象不存在。
* Required decision：注册来源、字段结构、与 taxonomy / golden set 的引用方式。
* Owner：P4.1。

### GAP-03 alias / 合并 / 重复 item 语义未定义

* Gap：alias 是否允许、是否一对多、合并后历史 evidence 如何归属。
* Why it prevents deterministic test：A7、A6 的 expected 无法确定。
* Required decision：alias 解析规则与冲突处理。
* Owner：P4.1。

### GAP-04 review evidence 的来源形态未冻结

* Gap：evidence 是既有 progress event 的投影，还是新 `review_attempt` event type。
* Why it prevents deterministic test：fixture 的 `events` 结构、event schema version、
  是否与 `progress-event/v0.1` 兼容都未知。
* Required decision：source 形态、是否升级 event schema version、与既有 attempt 的关联。
* Owner：P4.2。

### GAP-05 success / failure 推导与 insufficient 边界未冻结

* Gap：案例总分与 capability 分数在什么条件下算 success；样本数要求；
  无 evidence 与真实 0 分的边界。
* Why it prevents deterministic test：B1–B8、C2–C8 的 expected 无法确定。
* Required decision：按 item kind 的成功判定规则、样本要求、insufficient 定义。
* Owner：P4.2（阈值参数由 P4.4 确认）。

### GAP-06 同一 source event 的重复计入规则未冻结

* Gap：一次 attempt 能否同时作为 initial evidence 与 review evidence。
* Why it prevents deterministic test：B12 的 expected_error 与计数语义未知；
  时间/Scheduling 矩阵可能重复计数。
* Required decision：去重键与计入规则。
* Owner：P4.2。

### GAP-07 mastery 状态枚举与字段名未冻结

* Gap：`new / learning / due / mastered` 是否采用；`due` / `overdue` 是否为
  scheduling projection 而非 mastery state；state 字段 nesting 未知。
* Why it prevents deterministic test：所有 C / D / H 的 expected 无法书写。
* Required decision：mastery state 枚举（互斥、初始状态）与 `due` / `overdue` 分层。
* Owner：P4.3。

### GAP-08 mastered 持久性与失败行为未冻结

* Gap：mastered 是否永久；mastered 失败后降到哪个状态；是否影响 maintenance。
* Why it prevents deterministic test：C6–C8、D8 的 expected 无法确定。
* Required decision：mastered 语义与 maintenance 策略。
* Owner：P4.3 / P4.4。

### GAP-09 非法状态跃迁处理方式未冻结

* Gap：非法跃迁是 validation error、记录 transition reason，还是不可能发生。
* Why it prevents deterministic test：C10 的 `expected_error` 与错误 category 未知。
* Required decision：非法跃迁语义。
* Owner：P4.3。

### GAP-10 interval ladder 与首次 due 基准未冻结

* Gap：`1/3/7/15` 是否采用；first due 以哪个事实时间为基准；何时到期。
* Why it prevents deterministic test：D1、D6 的 expected 无法确定。
* Required decision：policy id / version、参数语义与 first-due 规则。
* Owner：P4.4。

### GAP-11 failure / overdue / 同日重复 review 规则未冻结

* Gap：failure 后 reset 或 downgrade；overdue 是否改变下一次 interval；
  同一天多次 review 是否全部计入。
* Why it prevents deterministic test：D5、D7、D8 的 expected 无法确定。
* Required decision：失败与 overdue 转移规则、同日重复处理。
* Owner：P4.4。

### GAP-12 due_count 定义与 projection 字段名未冻结

* Gap：`due_count` 是 item 数还是事件数；due / overdue 的状态名与字段名。
* Why it prevents deterministic test：H1–H4 的性质断言无法引用具体 projection 字段。
* Required decision：due projection 结构与 `due_count` 定义。
* Owner：P4.4。

### GAP-13 due 粒度与日期边界 timezone 未冻结

* Gap：`review_due_at` 是 instant、local date 还是两者；日期边界使用哪个 timezone。
* Why it prevents deterministic test：D2–D4、G2–G8 的边界断言无法确定。
* Required decision：due 粒度与 calendar/timezone 语义。
* Owner：P4.4。

### GAP-14 replay API 的 as_of / version 输出未冻结

* Gap：`as_of` 参数形态与必填性；输出中 contract / policy version 与 `as_of` 字段名。
* Why it prevents deterministic test：harness 的 echo 检查与版本断言无法确定。
* Required decision：replay 入口签名与输出 metadata。
* Owner：P4.5。

### GAP-15 同 timestamp tie-breaker 在 review 域未确认

* Gap：是否沿用 `UTC(occurred_at) + event_id`；同一 item 在同一 instant 的
  多次 evidence 的转移顺序如何定义。
* Why it prevents deterministic test：E3 无法确定 expected 顺序；
  相同 instant 的 success + failure 可能产生不同 mastery。
* Required decision：显式确认 tie-breaker 并声明 per-item 转移顺序。
* Owner：P4.5（与 P4.2 对齐）。

### GAP-16 validation error category 命名未冻结

* Gap：review 域的拒绝 category 命名（沿用 progress category 还是新命名空间）。
* Why it prevents deterministic test：所有 `invalid-*` fixture 的 `expected_error` 未知。
* Required decision：错误 category 命名与复用规则。
* Owner：P4.5。

### GAP-17 fixture schema 版本命名与最终字段（历史 gap，已关闭）

* 原 Gap：`review-fixture/v0.1-draft` 的最终名称、`expected` vs `expected_state`、
  `events_by_case` / `variants` 是否保留。
* Resolution：P4.6/P4.7 冻结独立的 `mastery-review-fixture/v0.1` schema，contract fixtures 仍使用 `review-fixture/v0.1`；字段以 `data/review/fixture-schema.v0.1.json` 为准。
* Status：CLOSED（P4.6/P4.7）；原始登记仅作历史审计记录。

---

## 11. 运行方式

```bash
# 新增测试（开发阶段最小集）
python3 -m unittest tests  # 或：
python3 -m unittest discover -s tests -p 'test_review_*.py' -v
python3 -m unittest discover -s tests -p 'test_progress_v01_regression.py' -v

# 全量（P4.6 / P4.7 正式收口前）
python3 scripts/validate_review.py
python3 scripts/validate_progress.py
python3 scripts/validate_taxonomy.py
python3 -m unittest discover -s tests -v
```

当前 fixture matrix 状态以 manifest 和 `scripts/validate_review.py` 为准；该 validator 仅报告矩阵状态，不单独判定 Phase 4 Gate。P4.9 的正式验证报告已创建，Phase 4 Gate 结论为 PASS，详见 [`docs/PHASE4_VALIDATION_REPORT.md`](PHASE4_VALIDATION_REPORT.md)。
