# Planner Input Snapshot v0.1

> **范围：只冻结 Planner 能看见什么。** 本文不定义 Planner 怎么选择、排序、分配或重排任务，也不冻结 P5.3+ 的输出契约。

## 1. 版本化边界

Planner v0.1 输入仅由以下显式来源构成：

```text
ProgressState v0.1
MasteryReviewState v0.1
Taxonomy v0.1 的 canonical topic ID catalog
Case Capability v0.1 的 canonical capability ID catalog
User Configuration v0.1
Planner policy identity/version
显式 as_of
显式 IANA timezone
```

序列化根对象和 `inputs` 均采用封闭字段集合；notes、聊天记录、AI 推测、UI 临时状态、参考 UI 数字、第三方题库正文、task execution 状态和课程内容不是允许字段。`docs/30_DAY_CURRICULUM_DRAFT.md` 明确保持 DRAFT，**不是 P5.1 Planner Input**，不从中引入主题顺序、阈值、配额或规则。

Catalog snapshot 只携带该版本完整的 canonical ID 集合及其已有版本标识：`taxonomy.taxonomy_version` 和 `capabilities.taxonomy_version`。后者正是仓库 `taxonomy/capabilities.json` 的字段；其值映射到 ProgressState 已有的 `capability_version`。不复制第三方正文，也不把数组排列当作优先级。

ProgressState / MasteryReviewState 原对象内已有的 schema、replay、policy 版本字段直接复用。没有额外平行的 Progress / Review 版本字段。根 `schema_version` 是 Planner Input Snapshot 自身的契约版本；User Configuration 自有其既定版本。

### Planner v0.1 可见字段

- **ProgressState**（`progress-state/v0.1`）：`schema_version`、`replay_rule_version`、`event_schema_version`、taxonomy / capability version、`replayed_event_count`；`global` 的作答计数 / accuracy；`case` 的作答计数 / scored 计数 / earned / possible / ratio；每个 topic 的 attempt / correct / incorrect / accuracy；每个 capability 的 attempt / earned / possible / ratio / evidence_status；`errors` 计数、cause 计数和 mix；L1/L2/L3 coverage；`study.session_count` / `study_minutes`。
- **MasteryReviewState**（`mastery-review-state/v0.1`）：自身 schema / Review / Progress / mastery policy / review policy / projection / outcome-adapter versions；显式 `as_of`、`timezone`、`schedule_timezone`、`tzdata_version`、policy metadata；item map 中的稳定 target、`item_kind`、canonical ref、`mastery_state` / reason、`review_status` / reason、`next_due_at`、`next_due_local_date`、`review_interval_days`、last review、计数及 evidence trace；`review` 与 `mastery` aggregates。上述是已重放的 Phase 4 输出，不是 Planner 重算的公式。
- **Taxonomy / Capability**：版本与完整 canonical ID 集合；ID 排列无语义。P5.1 不从 name、alias、source provenance 或未冻结 curriculum 推导 priority。
- **UserConfiguration**：仅 `timezone`、`daily_available_minutes`、`study_days`；字段约束见 [User Configuration v0.1](USER_CONFIGURATION_V01.md)。
- **Planner policy**：输入 envelope 仅可见已登记 identity/version；当前保留的 input-contract identity 不含可执行规则。

以上是输入 allowlist，不是任务、priority 或 Planner Output contract。

## 2. Snapshot strategy 冻结：A — Self-contained

v0.1 的正式语义是 **self-contained snapshot**：快照内直接保存完整 ProgressState、MasteryReviewState、UserConfiguration、topic / capability ID catalog、显式 `as_of`、timezone 和 policy identity/version。Reference-only / digest-only **不是**第二种支持模式。

| 维度 | Self-contained（采用） | Reference-only（拒绝） |
|---|---|---|
| Determinism | 同一份快照可直接验证，数据不依赖隐式装载次序 | 结果依赖解析器、外部数据版本及装载时点 |
| Replayability | 状态与 catalog 身随输入保留，可离线重放输入语义 | 引用可能失效、内容可能已变；digest 不能单独还原内容 |
| Fixture isolation | 场景由现有 v0.1 replay 构造 synthetic baseline，校验时 materialize 为完整快照；不接入用户状态库 | 测试容易偷偷依赖全局仓库、数据库或当前状态 |
| Hidden dependency | 除支持版本 registry 与 IANA tzdata 验证外，无外部 state loader | ref resolver、权限、存储、缓存与源版本都成为未声明依赖 |
| Version consistency | 同一 envelope 内比对 Progress / Review / catalog / config 版本 | 分散加载时可能拼接不同代 state 或 catalog |

Self-contained 使输入较大，但优先保障 `same explicit input = self-contained deterministic replay`。验证器从快照本身读取状态，不会按 ref 重新加载；catalog allowlist 仅用于确认版本受支持和 refs 有效。

## 3. Snapshot 结构和一致性

权威 JSON Schema 为 `data/planner/planner-input.schema.json`。结构摘要：

```json
{
  "schema_version": "planner-input/v0.1",
  "as_of": "2026-01-01T00:00:00Z",
  "timezone": "Asia/Shanghai",
  "planner_policy": {
    "policy_id": "planner-policy/input-contract",
    "policy_version": "v0.1"
  },
  "inputs": {
    "progress_state": {},
    "mastery_review_state": {},
    "taxonomy": {"taxonomy_version": "0.1", "topic_ids": []},
    "capabilities": {"taxonomy_version": "0.1", "capability_ids": []},
    "user_configuration": {}
  }
}
```

`planner-policy/input-contract/v0.1` 是本输入边界的**非执行 identity token**：仅供 P5.1 校验 snapshot policy 槽位，不代表 P5.4 排程策略，不规定任何 Planner 行为，也不能用来生成计划。v0.1 只接受这一 identity/version；其他值以仓库沿用的 `invalid_policy_input` 拒绝。真正可执行的 Planner Policy identity 与规则仍须由 P5.4 冻结。

Validator 至少核对：

- Snapshot / User Configuration / ProgressState / MasteryReviewState 所支持的 schema 与 replay 版本；
- ProgressState 自带的 `taxonomy_version`、`capability_version` 与 catalog manifest；ReviewState 自带的 Progress event / replay 版本与 ProgressState；ReviewState 的 `progress_replayed_event_count` 与 ProgressState event count；
- Review item map key、`item_order` target、item kind、canonical ref、review item identity 和对应 catalog；
- snapshot、User Configuration、MasteryReviewState 的 timezone 一致；snapshot 与 MasteryReviewState 的 `as_of` 必须是同一 instant。

失败即 fail closed：拒绝整个 snapshot，不忽略错误项、不自动修复、不猜引用、不产生 partial input。拒绝类别复用仓库已存在的风格，例如 `invalid_schema_version`、`invalid_catalog_version`、`invalid_policy_input`、`invalid_timestamp`、`invalid_timezone`、`unknown_topic_id`、`unknown_capability_id`、`unknown_review_item`；配置使用 `invalid_user_configuration`，跨输入冲突使用 `inconsistent_input`。

## 4. as_of、时区与 replay 限制

- `as_of` 必须由调用方显式提供；必须是带 UTC offset 的 ISO 8601 instant。naive、格式错误均以 `invalid_timestamp` 拒绝。
- Canonical form 将 instant 规范化为 UTC `Z`。Planner 不读取墙上时钟、机器本地时区或浏览器时区。
- `timezone` 必须是显式有效 IANA timezone；无默认值。snapshot、User Configuration、ReviewState 的 `timezone` / `schedule_timezone` 必须一致。
- ReviewState 的 `as_of` 必须与 Planner `as_of` 为同一 UTC instant。Planner **只消费**其 `mastery_state`、`review_status`、`next_due_at`、`next_due_local_date`、`review_interval_days`、reason 和 policy metadata；Planner validator / consumer 不从 evidence 重新计算 mastery、due、overdue 或 interval。Phase 4 是唯一正式来源。
- `America/New_York` 等含 DST 的 IANA zone 按显式 zone 验证；DST 不引入机器本地时间或隐式时钟。

### ProgressState 的时间限制

实际 `progress-state/v0.1` 输出包含 schema/replay/catalog 版本及聚合字段，**没有** replay `as_of`、事件集合 digest 或精确事件时间上界。故 Planner 不能从 ProgressState 单独证明其 facts 截止于本 snapshot 的 `as_of`；本契约不伪造该一致性保证。`replayed_event_count` 与 ReviewState 的 count 相等只能校验数量，不能证明两者由完全相同的 event set 生成。调用方负责提供适用的 ProgressState；若未来要证明精确时间截面 / event identity，必须由 Progress 合同显式补充，而非 Planner 猜测。

MasteryReviewState 已携带显式 `as_of`、timezone、`tzdata_version` 与 policy metadata；Planner 核对其 envelope 一致性但不重算其 policy 投影。Replay 时区规则受所记录的 tzdata 版本限制，遵循 Phase 4 既有说明。

## 5. Reference 与 Phase 4 消费边界

- ProgressState 的 topic / capability map 必须对应其携带 catalog 的完整 canonical ID 集合。未知 topic / capability 分别以 `unknown_topic_id` / `unknown_capability_id` 拒绝。
- MasteryReviewState 的 active items 是 Review Item catalog 的状态投影；`item_order` 必须恰好引用 `items` 中的 item，item key、内部 `review_item_id` 和由 `item_kind + canonical_ref` 得出的稳定 identity 必须一致。未知 / 不一致 target 以 `unknown_review_item` 拒绝；不支持 `item_kind` 以 `unknown_item_kind` 拒绝。
- 不存在未知 ref 的 fallback、topic alias 猜测、自动迁移或 partial state。
- `MasteryReviewState` 内的 due / mastery 值是上游已计算结果；Planner 不重新计算，也不把它们合并到 ProgressState。

## 6. 顺序与 canonical representation

JSON 数组 / map 的序列化顺序不是 Planner priority。v0.1 对以下集合按无序语义处理：

```text
taxonomy.topic_ids
capabilities.capability_ids
ProgressState topics / capabilities maps
MasteryReviewState items map / item_order
UserConfiguration study_days
```

`study_days` 在 canonical form 中按 ISO weekday 升序。Review evidence 如存在，按 UTC `occurred_at`、`evidence_id` canonicalize；这保留既有事实标识，不把其输入次序解释为任务优先级。Object keys 以 Unicode key 升序序列化。Policy interval ladder 等本身有顺序语义的数据不重排。

逻辑等价输入通过 `scripts/validate_planner_contract.py` 的 canonical API 得到相同 canonical JSON。Topic、Capability、Review item 的 JSON 排列不得影响其业务含义或暗示 priority；真正的 Planner priority 属于 P5.4。

## 7. 明确不包含

Planner Input Snapshot v0.1 不接收自由文本 note、聊天 / UI 状态、AI 推测、参考 UI 数字、题库正文、Assessment / Essay / task-execution 状态、未冻结 curriculum 规则或未来 Planner Output。这里不定义 task、priority、duration allocation、TodayPlan、RollingPlan、completion、replanning 或 Planner replay 行为。
