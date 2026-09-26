# Planner 契约

本目录记录 Planner v0.1 的领域输入与 projection output contract。Product Validation Slice 已在其上实现 Today-only MVP；完整 Phase 5 policy 与 Rolling 7-Day 排程仍未完成。

- [Planner Input Snapshot v0.1](PLANNER_INPUT_CONTRACT_V01.md)：允许输入、self-contained snapshot、一致性、时间、拒绝与 canonicalization（P5.1）。
- [User Configuration v0.1](USER_CONFIGURATION_V01.md)：最小显式用户配置及字段取舍（P5.2）。
- [Planner Output Contract v0.1](PLANNER_OUTPUT_CONTRACT_V01.md)：Today / Rolling 7-Day 容器、PlanDay、PlanTask、UnmetDemand、ExplainTrace 与结构不变量（P5.3，MVP 最小扩展支持 new_learning topic target）。

机器契约与验证资产：

- `data/planner/planner-input.schema.json`
- `data/planner/user-configuration.schema.json`
- `data/planner/planner-output.schema.json`
- `data/planner/fixtures/`：P5.1/P5.2 input contract fixtures。
- `data/planner/output-fixtures/`：P5.3 output contract fixtures；只验证结构，不生成计划。
- `scripts/validate_planner_contract.py`：验证 input / output schema 与静态 contract fixtures；不生成计划。
- [`engine/planner/README.md`](../../engine/planner/README.md)：MVP policy、new-learning source 和实际示例。

`engine/planner/replay.py` 复用 `PlannerOutput.days[0]`，只生成今天的 review + new_learning；days[1:7] 保留为 output contract 的空占位，不运行 Rolling 7-Day selection。MVP new-learning source 为无有效 topic evidence 的 L3 taxonomy IDs，按 canonical ID 升序选一个。task duration、priority 和 capacity 规则仅为该 MVP 的确定性实现规则，不宣称完整 P5.4/P5.5 已冻结。`docs/30_DAY_CURRICULUM_DRAFT.md` 继续为 DRAFT，不作为输入。

Planner 仍消费而不重算 ProgressState、MasteryReviewState；不改 Progress / Review schema，不重算 mastery / due / interval。User Configuration v0.1 尚无 `exam_date`，MVP 不按考试倒计时改变 policy。
