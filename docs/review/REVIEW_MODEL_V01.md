# Review Model v0.1

> 状态：**FROZEN（P4.1）**。本文冻结 Review Item 的领域边界与稳定身份，不实现 Mastery State Machine 或 Review Scheduling Policy。
>
> 机器契约：[`data/review/schema.json`](../../data/review/schema.json)。Evidence 字段和投影规则见 [`REVIEW_EVIDENCE_V01.md`](REVIEW_EVIDENCE_V01.md)。

## 1. 层次边界

本阶段固定以下依赖关系：

```text
Progress Fact
  = immutable progress-event/v0.1
        ↓ + explicit review-event/v0.1 context
Review Evidence v0.1
        ↓
Mastery State                 Future: P4.3
        ↓
Review Scheduling Projection  Future: P4.4
```

四层不可互换：

- **Progress Fact** 是事件中明确记录的事实，例如 `correct: true/false` 或 `score_earned / score_possible`。
- **Review Item** 是可独立拥有后续 review state 的稳定对象，不是 aggregate metric。
- **Review Evidence** 是把一个事实关联到一个 item 和一次显式学习上下文后的 policy-neutral projection。
- **Mastery / Scheduling** 才能根据 Evidence 和各自版本化 policy 推导 success、failure、状态或到期时间。

Progress Event v0.1 仍是事实源。本阶段不修改 `data/progress/schema.json`，不把 review 字段偷偷加入既有三类 event。

## 2. Review Item 定义

Review Item 是一个具有稳定 canonical reference、source provenance 和独立 evidence stream 的最小复习对象。它必须能在 replay、展示名称变化和 policy 升级后被同一 `review_item_id` 定位。

v0.1 只接受三类：

| `item_kind` | canonical object | v0.1 是否支持 | 独立 state |
| --- | --- | --- | --- |
| `topic` | Taxonomy Knowledge Topic ID | 支持 | 是，与 capability/question 分开 |
| `question` | source-scoped question identity | 支持 | 是，与 topic/capability 分开 |
| `case_capability` | Case Capability ID | 支持 | 是，与 Knowledge Topic 分开 |

同一题可以产生一个 `question` item 的 evidence，也可以根据事件直接引用产生 topic evidence；这是两个不同 item，不能自动把一个 item 的 evidence 升级为另一个 item 的 mastery。

### 2.1 稳定身份

固定 identity namespace 为 `review`。`review-model/v0.1` 是契约版本，不拼入 item identity；未来若身份语义发生不兼容改变，应建立显式的新 identity namespace 和迁移关系，而不是静默重写旧 ID。

```text
review/topic/<stable_topic_id>
review/question/<source_id>/<source_question_id>
review/case_capability/<stable_capability_id>
```

identity 只由 `item_kind` 和 stable canonical reference 构成：

- **不包含** review model/schema version；
- **不包含** taxonomy version；taxonomy version 用于验证 canonical reference 和记录 provenance；
- **不包含** mastery/review policy version；policy 升级不能制造新 item；
- **不包含** display name、中文名称、description、题干、选项、答案、解析或 OCR；
- **不包含** source commit、source path；它们是可变的 provenance；
- `question` identity 使用 `source_id + source_question_id`，而不是题目文本。

因此，taxonomy 只改名称或 source mapping 时，ID 保持不变；只有概念边界确实改变时才允许新 canonical ID，并需记录迁移。

### 2.2 Canonical reference 与 source reference

每个 item 都必须同时有：

```text
canonical_ref = “这个逻辑对象是谁”
source_reference = “这个对象/映射从哪里可审计地定位”
```

最小 source reference：

```json
{
  "source_id": "source-or-catalog-id",
  "source_commit": "40-character-lowercase-immutable-revision",
  "source_path": "repository/relative/path"
}
```

`question` item 还必须有 `source_question_id`，且它必须同时出现在 canonical reference 和 source reference 中。可选 `source_value` / `golden_set_record_id` 仅用于索引或 provenance，不参与身份。

`source_path` 必须是记录的来源仓库相对 POSIX 路径；绝对路径、Windows 路径、反斜杠和 `..` traversal 都拒绝。source reference 不得承载第三方题干、选项、答案、解析、PDF、OCR 或完整正文。

## 3. 三类 item 的 evidence 边界

### 3.1 Topic

- `comprehensive_attempt.topics` 直接列出的 topic 可以获得 `comprehensive_correctness` fact，每个直接 topic 一条 item evidence。
- topic evidence 只描述该次事实的 `correct`，不计算 topic accuracy，也不把累计 accuracy 直接变成 mastered。
- Progress replay 的 parent coverage closure 不会自动创建父 topic review evidence；父 topic 若要 evidence，必须被事件直接引用或由未来独立 contract 明确生成。
- `case_attempt` 的总分不是 topic 分数。v0.1 对 case→topic 显式标记 `unsupported`，绝不复制案例总分。

### 3.2 Question

- `question` item 必须使用稳定 `source_id/source_question_id`。
- 综合题可提供 `correct: true/false` fact。
- 案例题只有存在明确 aggregate score pair 时才提供 `score_earned/score_possible` fact；没有分数时是 `insufficient_evidence`，不是失败。
- item 和 evidence 均只保存 reference，不复制题干、选项、答案、解析、OCR 或 PDF。

### 3.3 Case Capability

- 只有 `case_attempt.capability_scores[]` 中明确点名该 capability 的 score pair，才能产生 capability evidence。
- `case_attempt.capabilities[]` 只有引用而没有对应 score pair 时，产生 `insufficient_evidence`；不产生零分。
- `case_attempt.score_earned/score_possible` 是案例 aggregate fact，不能复制给每个 capability。
- capability 是独立维度，不是 taxonomy topic 的子节点；二者不可互相替代。

## 4. 首次学习与 Review

现有 `comprehensive_attempt`、`case_attempt` 没有天然的 initial/review 语义；`study_session.activity_type = review` 也没有关联 item 和答案事实。因此 v0.1 **不从事件类型、自由文本、AI 判断或时间间隔猜测上下文**。

新增独立的 `review-event/v0.1`，事件类型为 `review_context`：

```json
{
  "schema_version": "review-event/v0.1",
  "event_id": "ctx-001",
  "event_type": "review_context",
  "source_event_id": "attempt-001",
  "review_item_id": "review/question/source-q/q-001",
  "attempt_context": "initial_learning",
  "occurred_at": "2026-01-01T10:00:00+08:00"
}
```

`attempt_context` 只有：

```text
initial_learning | review
```

规则：

1. 一个 context event 必须指向一个已有 immutable Progress Attempt Fact 和一个 active Review Item。
2. `occurred_at` 必须与 source progress event 的 instant 相同；Evidence 的 `occurred_at` 从 source fact 规范化得到。
3. 同一个 `source_event_id + review_item_id` 最多一个 context event，不能同时生成 initial 和 review 两条 evidence。
4. 没有 context event 的历史 Progress Fact **不被默认当作 initial learning，也不被当作 review**；它只是尚未有 Review Evidence。
5. `study_session` 只能提供 session fact；即使 activity type 是 `review`，也不能单独生成 item evidence。
6. 若产品确实知道一次操作是 initial 或 review，必须在事实采集时写入 context event；不能由“距离上次学习几天”反推。

这个设计使同一事实不会被重复计数：一个 source fact/item pair 只有一个 evidence projection，context 只是明确其语义，不复制 Progress Event。

## 5. Alias、duplicate、merge 与 active state

- active catalog 中同一稳定 identity 只能有一个 item descriptor 和一个活动 Review state。
- source-scoped alias 必须在进入 Review Item catalog 前解析为 canonical ID；alias 本身不创建第二个 item/state。
- duplicate canonical object、重复 `review_item_id` 或同一 canonical ref 的不同 ID 都是 validation error。
- taxonomy split/merge 不静默复用旧 ID：旧 item 应标记 retired，并由未来迁移记录把旧 ID 显式映射到新 item。v0.1 不执行迁移、不自动合并 evidence。
- `review/topic/X`、`review/question/...`、`review/case_capability/X` 是不同 namespace；相同字符串片段不意味着共享 state。

## 6. Decision Record

### D1 — `review_item_id` 构成

- **Decision**：使用 `review/<item_kind>/<stable canonical reference>`；question 使用 `review/question/<source_id>/<source_question_id>`。
- **Reason**：可读、可验证，且不会因展示名称、题面或策略变化而漂移。
- **Rejected Alternative**：把题干 hash、display name、source commit 或 policy version 放进 ID；这些值会变化或无法代表逻辑对象。
- **Future Extension**：若身份语义不兼容，建立新 identity namespace 和显式 migration map。

### D2 — v0.1 支持的 item kinds

- **Decision**：支持 `topic`、`question`、`case_capability`，三者各自独立。
- **Reason**：三类对象的证据事实不同，且 Issue #4 明确要求保持 Knowledge Topic 与 Case Capability 分离。
- **Rejected Alternative**：只用 topic 聚合所有对象，或将 capability 塞进 topic hierarchy；会丢失题目粒度和案例能力语义。
- **Future Extension**：essay capability、assessment 或 source collection 必须新增独立 kind 和证据 contract。

### D3 — taxonomy version 与 identity 的关系

- **Decision**：taxonomy/capability version 是 canonical reference 的校验和 provenance 字段，不进入 item ID。
- **Reason**：名称或 taxonomy 版本升级不应让同一个逻辑对象丢失历史 state。
- **Rejected Alternative**：`review/v0.1/topic/0.1/DATA...`；会把 catalog 发布版本误当成对象身份。
- **Future Extension**：概念边界变化时通过新 stable ID、retired item 和显式迁移处理。

### D4 — source reference 的最小要求

- **Decision**：每个 item/evidence 至少有 `source_id`、40 位 immutable `source_commit`、repository-relative `source_path`；question 另需 `source_question_id`。
- **Reason**：既能复盘来源，又不复制第三方正文；路径规则可防止本机路径泄漏和 traversal。
- **Rejected Alternative**：只存 URL、display name 或本地路径；无法稳定审计，且可能越过版权/安全边界。
- **Future Extension**：可增加 source catalog、license tag、line/range reference，但不得把正文带入正式资产。

### D5 — initial learning 与 review 的关系

- **Decision**：由独立 `review_context` event 显式声明 `initial_learning` 或 `review`；无 context 不生成 evidence。
- **Reason**：现有 attempt/session 没有可靠上下文，默认猜 initial 会制造事实。
- **Rejected Alternative**：用 `study_session.activity_type`、自由文本或日期间隔推断；不可审计且会随采集方式改变。
- **Future Extension**：可增加更细的 context（例如 maintenance），但必须有新版本和互斥/去重规则。

### D6 — Review Evidence 如何生成

- **Decision**：校验 Progress Event、Item 和 Context，按明确 item/source mapping 生成一条 policy-neutral evidence；按 UTC instant + stable IDs 排序。
- **Reason**：投影可删除、可重建、可测试，不依赖人工 aggregate state。
- **Rejected Alternative**：直接把 ProgressState 的 accuracy/score 拷贝成 review evidence；会丢失来源粒度和证据语义。
- **Future Extension**：P4.5 可在此投影上实现 deterministic replay，但必须保留 source event/context/evidence 链。

### D7 — comprehensive evidence 语义

- **Decision**：综合题只把上游 `correct: true/false` 作为 `comprehensive_correctness` fact；不在 Evidence 层写 success/failure。
- **Reason**：这是 Progress Event v0.1 已冻结的不可争议事实，且保留 zero/incorrect/null 的区别。
- **Rejected Alternative**：在 evidence 中直接写 `success`，或由 topic accuracy 阈值生成结果；阈值属于 P4.3 policy。
- **Future Extension**：Mastery policy 可基于 question/topic evidence 定义 success，但必须版本化并说明样本/transition。

### D8 — case/capability evidence 语义

- **Decision**：case question 使用明确 aggregate score pair；case capability 只使用点名该 capability 的 score pair；Evidence 保存 `score_earned` 与 `score_possible`。
- **Reason**：实际 score 是事实，成功阈值和状态是后续政策；防止案例总分污染每个能力。
- **Rejected Alternative**：把案例总分复制给全部 capability，或把没有 score 的 capability 当 0 分。
- **Future Extension**：可增加采分点/评分来源 contract，但必须保持 capability-level attribution 可审计。

### D9 — insufficient evidence 语义

- **Decision**：缺少所需事实时使用 `evidence_status=insufficient_evidence`、`evidence_value=null`；不等同于 failure、zero 或 mastered。
- **Reason**：没有 score 不是得零分，没有 capability score 也不是能力失败。
- **Rejected Alternative**：用 `false`、`0` 或空 score 补洞；会伪造学习事实。
- **Future Extension**：P4.3 可定义无 evidence item 的 mastery 初态，但不能把它改写成失败。

### D10 — duplicate/alias/merge 语义

- **Decision**：一个 canonical object 一个 active item/state；alias 先解析，duplicate 拒绝，merge/split 使用 retired + 显式 migration，v0.1 不自动迁移 evidence。
- **Reason**：避免一个逻辑对象产生多个无法解释的 review state。
- **Rejected Alternative**：按 display name、source path 自动去重或把两个 item 的 history 静默合并；这些信号不稳定。
- **Future Extension**：新增 versioned migration manifest，保留旧 replay 可解释性。

### D11 — copyright/source boundary

- **Decision**：Review Item、Progress Event 和 Evidence 只保存 canonical IDs、source references、事实数值和短 metadata；不保存第三方题干、选项、答案、解析、PDF/OCR。
- **Reason**：项目边界优先 index/metadata/mapping/source reference，GitHub 可访问不等于可复制发布。
- **Rejected Alternative**：为了 question identity/evidence 缺口复制原题或答案；这既无必要也违反仓库约束。
- **Future Extension**：受许可的本地导入可有独立 source asset contract，但不能改变本契约的最小 reference 边界。

### D12 — 留给 P4.3/P4.4 的问题

- **Decision**：本窗口不冻结 mastery states、success/failure threshold、interval、due、overdue、maintenance 或 1/3/7/15。
- **Reason**：Evidence 应 policy-neutral；这些规则依赖 Evidence 之后的独立状态机和 scheduling policy。
- **Rejected Alternative**：在 Review Evidence 中写 `success`、`mastery` 或 `review_due`，或把旧课程草案升级为 formal rule。
- **Future Extension**：P4.3/P4.4 必须把 policy/mastery version、as_of、transition reason 和 evidence trace 作为下游 contract。综合题 boolean 可由显式 adapter 映射为 outcome；案例/能力 score 的 success mapping 尚未冻结，属于 P4.5 的 `BLOCKING_DECISION`，不得把阈值写回 Evidence。若需要本窗口未提供的字段，应先记录阻塞后再扩展。

## 7. 明确留给后续阶段

以下内容不是本窗口的实现，也不是 v0.1 的隐含承诺：

- `new / learning / due / mastered` 是否采用及其互斥定义；
- success/failure 的阈值、连续成功次数和失败降级；
- `review_due_at`、interval、overdue、maintenance review；
- `as_of` 驱动的 MasteryReview replay；
- Planner、due count、UI、AI 自动评分。

若 P4.3/P4.4 需要改变 Item 或 Evidence 语义，必须先提交上游 contract 变更，不能在下游实现中隐式补定义。
