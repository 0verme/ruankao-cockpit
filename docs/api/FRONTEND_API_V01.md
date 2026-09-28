# Frontend API v0.1 — FastAPI Transport

状态：Slice 1 最小稳定 contract。本文描述仓库现有 Python service/domain 输出，不承诺完整领域 schema 的长期冻结；未列出的 endpoint 不属于本 Slice。

```text
Browser → FastAPI transport → cockpit_service → Planner / Progress / Review / TopicExperience
```

FastAPI 仅负责 HTTP、request shape、JSON 序列化和错误映射。它不拥有学习状态，不在 route 计算计划、Topic/Capability 关系、Progress、Review、mastery、到期状态、provenance 或 attempt identities。

## Local data 配置

启动进程时，`COCKPIT_LOCAL_DIR` 可指定唯一 `.local` 目录，且必须是绝对路径；未设置时固定使用 `PROJECT_ROOT/.local`。相对环境变量配置会拒绝启动。API 每次调用现有 service 时都显式传入该绝对路径，不跟随服务器启动或请求时的 cwd。

```bash
python3 -m pip install -r requirements.txt
uvicorn api:app --host 127.0.0.1 --port 8000
```

GET 不初始化、不创建缺失的本地状态。若本地目录已有 service 的 pending transaction，`get_today(...)` 仍按现有 service 行为执行恢复；这不是初始化或新建 `.local`。

该 API 仍是本地单用户服务：没有用户系统、鉴权、云同步或 CORS 配置；默认应只绑定 loopback（例如 `127.0.0.1`），不要直接暴露到不可信网络。

所有时间 query/body 值使用 ISO 8601。凡要求 instant 的输入都必须带 `Z` 或显式 UTC offset。planner 的 `as_of` 输出为现有 Planner canonical UTC 表示；`timezone` 来自本地 User Configuration。`review.next_due_local_date` 是配置时区下的日历日期，不是 UTC instant。

## 通用错误响应

```json
{
  "error": {
    "category": "not_initialized",
    "message": "Cockpit 尚未初始化。请先初始化本地数据。"
  }
}
```

`category` 是前端分支依据；`message` 仅供诊断/友好显示，前端不可从文案解析业务状态。

| HTTP | category（常见） | 含义 |
|---|---|---|
| 422 | `invalid_request`, `invalid_timestamp`, `invalid_attempt`, `invalid_source_reference`, `forbidden_path`, `invalid_source_provenance`, `invalid_learning_payload`, `non_active_topic`, `future_evidence`, `target_mismatch` | 请求 shape 或现有领域校验拒绝；没有把不可验证内容转成成功状态 |
| 404 | `unknown_topic`, `unknown_task` | Topic 不存在，或任务 ID 不在可用计划中 |
| 409 | `not_initialized`, `incomplete_local_data`, `task_not_scheduled`, `duplicate_event`, `pending_transaction`, `conflicting_transaction` | 本地状态或当前计划冲突；客户端应刷新/显式初始化，不应重试写成新的“完成状态” |
| 500 | `storage_error`, `invalid_local_data`, `invalid_catalog`, `invalid_learning_catalog`, `invalid_topic_experience` | 本地数据、静态目录或服务 read model 无法安全使用 |

未知的 request body 字段会返回 `422 invalid_request`。server error 不代表可以用空状态替代失败数据。

## `POST /api/init`

唯一初始化入口。调用 `initialize_cockpit(local_dir)`；重复调用不覆盖已存在数据。

### Request

无 body。

### Response `200`

首次创建：

```json
{"state":"created"}
```

目录已存在（不论是否由本次调用创建）：

```json
{"state":"already_exists"}
```

`already_exists` 不保证已有目录完整；若缺少文件，后续读取会返回 `incomplete_local_data`，不会静默重建或覆盖。

## `GET /api/today`

可选 query：`as_of=<ISO-8601 aware timestamp>`。不提供时使用现有 service 的当前时钟处理。显式 `as_of` 会原样交由 `cockpit_service.get_today(...)`，非法或无时区值由 service 拒绝。

### Response `200`

```json
{
  "planner": { "...": "完整的 PlannerOutput 原样结果" },
  "task_topics": {
    "<task_id>": {
      "topic_id": "ARCH.CLOUD_NATIVE.CONTAINERS_SERVERLESS",
      "topic_name": "容器与 Serverless",
      "taxonomy_version": "0.1",
      "breadcrumb": [
        {"topic_id":"ARCH","name":"系统架构设计基础知识"},
        {"topic_id":"ARCH.CLOUD_NATIVE","name":"云原生架构设计"},
        {"topic_id":"ARCH.CLOUD_NATIVE.CONTAINERS_SERVERLESS","name":"容器与 Serverless"}
      ],
      "learning_payload_status": "available",
      "learning_payload_version": "1.0.0"
    }
  },
  "progress": { "...": "Progress replay state 原样结果" },
  "review": {
    "state": { "...": "Review replay state 原样结果" },
    "items": []
  }
}
```

`planner` 是 `TodaySnapshot.planner_output` 原样输出（保留其完整 horizon；Today 在 `planner.days[0]`）。`task_topics` 只为当天可映射到 Knowledge Topic 的 Planner task 提供 Python service 已解析的显示 metadata，key 是原 `task_id`；并不重新排序或改写 Planner task。Capability、无法映射为 Knowledge Topic 的任务不会伪装成 Topic。

`progress`、`review.state` 和 `review.items` 是现有 service/domain read model，不是供前端重算的输入材料。Today task 的 Payload 内容通过下一个 endpoint 读取。

未初始化返回 `409 not_initialized`，GET 不创建目录。

## `GET /api/topics/{topic_id}`

可选 query：与 Today 相同的 `as_of`。调用 `get_today(...)` 与统一 `get_topic_experience(...)`。

### Response `200`

```json
{
  "topic": {
    "topic_id":"ARCH.CLOUD_NATIVE.CONTAINERS_SERVERLESS",
    "name":"容器与 Serverless",
    "taxonomy_version":"0.1",
    "breadcrumb":[{"topic_id":"ARCH","name":"系统架构设计基础知识"}]
  },
  "learning_payload_status":"available",
  "learning_payload_version":"1.0.0",
  "learning_payload": { "...": "现有、已校验的 learning-payload/v0.1 object" },
  "progress":{"attempt_count":0,"accuracy":null},
  "review":{
    "mastery_state":null,
    "status":null,
    "next_due_local_date":null,
    "policy_version":null
  },
  "verification_sources": []
}
```

状态语义：

- 有合法 Payload：`learning_payload_status="available"`，Payload object 与版本非空。
- 合法 active Topic 但没有文件：HTTP `200`，`learning_payload_status="unavailable"`、`learning_payload_version=null`、`learning_payload=null`。这不是错误，也不生成占位知识。
- 不存在的 ID：`404 unknown_topic`。
- 已知但不是 active L3 Knowledge Topic（例如层级节点）：`422 non_active_topic`。Topic 与 Capability 不互相转换。
- Payload/schema/provenance 内容无法验证：返回 `422 invalid_learning_payload` 或 `invalid_source_provenance`；静态 Taxonomy/source catalog 本身不可用则返回 `500 invalid_learning_catalog`。**绝不把校验失败降级为 `unavailable` 或返回未经验证的正文**。

`progress` 与 `review` 的 nullable 值表示现有 read model 没有该派生状态，不表示前端可以自行估算。`verification_sources` 是现有 source index 中不含题干正文的引用元数据。

## `POST /api/attempts`

调用 `record_browser_attempt(...)`。客户端提交实际 attempt 与来源引用；服务从当前计划解析目标、校验来源、按现有 deterministic identity 规则构造事实、持久化并 replay。

### Request

```json
{
  "task_id":"<当前 Today Planner task_id>",
  "occurred_at":"2026-09-27T09:00:00+08:00",
  "question":{
    "source_id":"<真实来源 ID>",
    "source_commit":"<40 位小写不可变 commit>",
    "source_path":"<来源仓库内安全相对路径>",
    "source_question_id":"<真实题目引用 ID>",
    "golden_set_record_id":"<可选：已索引的 Golden Set record ID>"
  },
  "correct":true,
  "error_cause":null
}
```

`question` 只能是来源引用 metadata，不得提交题干、选项、答案、解析或第三方正文。`occurred_at` 是实际作答 instant，按提交的 ISO 8601 offset 保存在 fact；Review/Planner replay 由 server-side service clock 确定。`error_cause` 可选，只有答错时现有 attempt builder 才会把它写入 fact。未知字段会拒绝；禁止 `mastered`、`completed`、`review_due`、`topic_progress`、客户端 event ID、客户端 policy 或 planner 输出。客户端不提交 `as_of`，避免客户端选择 replay 时间。

### Response `200`

```json
{
  "recorded": {
    "progress_event_count":1,
    "review_item_count":1,
    "review_context_count":1
  },
  "today": {
    "planner": {"...":"更新后的 PlannerOutput"},
    "progress": {"...":"service replay state"},
    "review": {"state":{"...":"service replay state"},"items":[]}
  }
}
```

响应中的 replay 与持久化结果来自同一次 `record_browser_attempt(...)` 返回值。前端可随后 GET `/api/today` 获取 task display metadata。

相同 attempt 输入由现有 service 构造相同 deterministic event/context identity；重复记录会被拒绝，不会覆盖或静默去重。当前计划在重试前可能已变化，因此可能先返回 `task_not_scheduled`，否则由 service 返回 `duplicate_event`；两者都不是成功写入，客户端应 GET Today 并检查状态。HTTP adapter 不接收或构造 event identity。

非法 attempt/provenance 必须 fail closed；service 校验失败时不得新增 Progress / Review facts。

## Truth / Presentation 边界

**Domain Truth / service read model（只读消费，不重算）**：

- `planner` 的 task 顺序、`planned_minutes`、容量与 unmet demand；
- `progress`、`review.state/items`，Topic `progress` / `review` 字段；
- `learning_payload_status`、已返回 Payload 与 provenance validation 结果；
- 当前 task 到 Topic 的 service 解析结果；
- `recorded` 计数与 attempt 是否成功。

**UI presentation / navigation metadata**：

- `task_topics` 是供卡片展示的 Python 组合视图；`topic.name`、breadcrumb 本身来自版本化 Taxonomy，不是 React 自己的目录事实；
- loading、表单字段状态、错误展示、打开哪个页面等仅为 UI 状态，不构成学习事实。

前端不得以 `planned_minutes` 累加重算容量，不按 `review_status` 自己推算 due/overdue，不以 `accuracy` 推断 mastery，不从 attempt body 写入 completion/progress，不用 localStorage 标记已学习。所有学习状态以 Python service/domain 的 immutable facts + deterministic replay 为准。
