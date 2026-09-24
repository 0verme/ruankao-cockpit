# Planner 契约

本目录只冻结 Planner v0.1 **可以读取的输入**，不定义任何任务选择、优先级、容量分配、重排或输出行为。

- [Planner Input Snapshot v0.1](PLANNER_INPUT_CONTRACT_V01.md)：允许输入、self-contained snapshot、一致性、时间、拒绝与 canonicalization。
- [User Configuration v0.1](USER_CONFIGURATION_V01.md)：最小显式用户配置及字段取舍。

机器契约与验证资产：

- `data/planner/planner-input.schema.json`
- `data/planner/user-configuration.schema.json`
- `data/planner/fixtures/`：少量输入契约场景；validator 将场景 patch 应用于由现有 Progress / Review v0.1 replay 构造的 synthetic baseline，再校验完整 snapshot。
- `scripts/validate_planner_contract.py`

本轮不创建 `engine/planner/`。`docs/30_DAY_CURRICULUM_DRAFT.md` 仍为 DRAFT，不是 P5.1 输入；课程接入留给 P5.5。Phase 4 的 `ProgressState`、`MasteryReviewState` 与 Review policy 契约不因本目录改变。
