# Planner 契约

本目录冻结 Planner v0.1 的领域输入与 projection output 契约；当前仍不包含 Planner 业务实现。

- [Planner Input Snapshot v0.1](PLANNER_INPUT_CONTRACT_V01.md)：允许输入、self-contained snapshot、一致性、时间、拒绝与 canonicalization（P5.1）。
- [User Configuration v0.1](USER_CONFIGURATION_V01.md)：最小显式用户配置及字段取舍（P5.2）。
- [Planner Output Contract v0.1](PLANNER_OUTPUT_CONTRACT_V01.md)：Today / Rolling 7-Day 容器、PlanDay、review PlanTask、UnmetDemand、ExplainTrace 与结构不变量（P5.3）。

机器契约与验证资产：

- `data/planner/planner-input.schema.json`
- `data/planner/user-configuration.schema.json`
- `data/planner/planner-output.schema.json`
- `data/planner/fixtures/`：P5.1/P5.2 input contract fixtures。
- `data/planner/output-fixtures/`：P5.3 output contract fixtures；只验证结构，不生成计划。
- `scripts/validate_planner_contract.py`：统一验证 input / output schemas 与静态 contract fixtures，不执行排程或 Planner replay。

P5.3 当前只支持 `review` task，引用现有 `MasteryReviewState` Review Item identity。`new_learning`、task ordering、priority、时长政策、capacity allocation、Curriculum Backbone 与 replay 仍未冻结 / 实现。`docs/30_DAY_CURRICULUM_DRAFT.md` 继续为 DRAFT，不是 Planner input 或 Rolling Plan。

本轮不创建 `engine/planner/`。Phase 4 的 `ProgressState`、`MasteryReviewState` 与 Review policy 契约不因 Planner output contract 改变；Planner 不重算 mastery / due / interval。
