# User Configuration v0.1

> UserConfiguration 是用户显式输入；它不是 Progress Event、Review Evidence、Planner Output，也不是 AI 推测结果。本契约不提供隐藏默认值。

## 字段取舍

| 候选字段 | 决定 | v0.1 理由 |
|---|---|---|
| `timezone` | **IN（required）** | 决定 local date / horizon 的日期语义；必须可验证且与 ReviewState 对齐。 |
| `daily_available_minutes` | **IN（required）** | 是 Planner 可见的容量输入；显式 `0` 支持 zero-capacity case。 |
| `study_days` | **IN（required）** | 明确学习日 / 非学习日输入；数组顺序无语义。 |
| `exam_date` | **OUT / FUTURE** | P5.4 尚未冻结是否按考试日期改变行为；本轮不把潜在倒计时用途升级为 required/optional 输入。将来由明确 policy 证明消费价值后再纳入。 |
| `subject preference` | **OUT / FUTURE** | 尚无统一、版本化的科目偏好 / 权重模型；不创建主观优先级。 |

v0.1 没有 optional fields：任何未冻结配置均不可携带，`additionalProperties: false`。例如 subject preference 不能以自由对象绕过边界。

## 正式字段

```json
{
  "schema_version": "user-configuration/v0.1",
  "timezone": "Asia/Shanghai",
  "daily_available_minutes": 0,
  "study_days": [1, 3, 5]
}
```

### `timezone`

- required string；必须是显式有效 IANA timezone，如 `Asia/Shanghai`、`Asia/Tokyo`、`America/New_York`。
- 不读机器本地时区；不设置隐藏默认值；`local` / `system` 等机器别名无效。
- Planner snapshot 顶层 `timezone`、User Configuration `timezone`、MasteryReviewState `timezone` 与 `schedule_timezone` 必须一致。
- `America/New_York` 等具 DST 规则的 IANA timezone 合法；本字段只声明 timezone，不定义 DST 日如何补课或分配任务。

### `daily_available_minutes`

| 项 | 冻结值 |
|---|---|
| type | JSON integer（布尔值不算整数） |
| unit | 分钟 |
| min | `0` |
| max | `1440`（一天分钟总量上限） |
| zero | **合法，保留为 `0`，不得替换为默认值** |

此值只是用户声明容量；本轮不决定 Review / New Learning 之间如何分配。

### `study_days`

- required JSON array，使用 ISO weekday：`1 = Monday` 至 `7 = Sunday`。
- 值域为整数 `1..7`；拒绝重复值；接受空集合，也接受 7 天全集。
- 输入顺序无语义，canonical form 升序排列。
- 空集合明确表示用户没有声明学习日；不得自动补日。如何补休、错过一天后如何追赶、是否重新规划均不在本契约范围。

## 机器 Schema

权威 schema：`data/planner/user-configuration.schema.json`。实际 IANA 数据库校验由 Planner contract validator 使用显式 zone 名称完成；JSON Schema 单独无法证明 zone 是否存在。
