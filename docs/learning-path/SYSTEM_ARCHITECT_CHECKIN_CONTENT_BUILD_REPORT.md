# 系统架构设计师打卡学习单元离线构建报告

> 构建产物状态：静态草稿；生成日期：2026-09-29。

## 摘要

- 来源 Learning Path：`system-architect-checkin` v1.0.0，路径状态保持 `draft`。
- 输入归档：`系统架构设计师打卡.zip`，SHA-256 `d7e8f68374f250dab72f2a08c543cbe9cbd44533fdc8e1e32c1a0d0e67fce17a`，大小 175511 bytes。
- 原始记录 112 项：110 个学习项 + 2 个 NON_LEARNING 休息项；休息项未生成文件（`checkin-020`, `checkin-026`).
- 已生成 110 个 Markdown 文件，保留 `item_id`、Path `order`、来源日期/路径、mapping、confidence、topic_ids 和 Prompt 区块指纹。
- 归档来源完整性核验：是：归档指纹、CRC 与 110 个 Prompt 区块 SHA-256 均通过。

## Mapping 统计

| Status | Items |
|---|---:|
| EXACT | 15 |
| PARTIAL | 27 |
| SPLIT | 40 |
| MERGE | 16 |
| UNMAPPED | 12 |

以上分类从 Learning Path manifest 读取，仅记录来源映射关系；不推导 Planner 任务语义，也不改变 Taxonomy。

## 来源缺口与审核状态

| Frontmatter `review_status` | Items |
|---|---:|
| `source_gap` | 75 |
| `unreviewed` | 35 |

`source_gap` 是内容层的证据缺口标记。其余 `unreviewed` 只表示目前未记录已知缺口，不能理解为已完成审核。全部 110 个文件的 `generation.status` 都是 `draft`；没有任何一项因此获得内容批准。

所有学习单元均保留软考关注边界：缺少章节级大纲/教材证据时不作覆盖断言；Golden Set 只作 Topic 级索引，不据此生成频率结论。

## 校验与模板校准

```text
PASS: 110 static units; 2 NON_LEARNING records omitted; 75 SOURCE_GAP; 35 no-known-gap drafts
PASS: prompt SHA-256 verified against 系统架构设计师打卡.zip
```

- 前 7 项完成的是 Issue #50 范围内的**静态 Markdown 模板校准**（PASS）：包含 MERGE、SPLIT、EXACT；缺证处保留 `SOURCE_GAP`，并检查 Prompt authoring 指令泄漏与无证据考试频率断言。
- 该格式校准不推翻 PR #51 Pilot 的 `CONTENT_MODEL_GAP` 结论，也不代表 Topic-scoped Payload / Topic Experience 已能表达 sequential Learning Units 的差异化内容；本批文件不接入运行时。
- 质量抽查：批量生成后定向复核 `checkin-065`、`073`–`075`、`110`、`112`，对照来源提纲检查主题边界、`SOURCE_GAP` 标记及 UNMAPPED/多 Topic 身份；这是抽样，不代替 110 项逐条人工事实审校。
- 静态 validator 校验文件集合/数量、Learning Path 身份和顺序、来源路径/日期、mapping 与 topic_ids、Prompt hash 格式、必需内容章节、Prompt 指令泄漏和 SOURCE_GAP 标记。带 `--archive` 时额外核对 ZIP 指纹、CRC 和每项 Prompt 区块 hash。
- `UNMAPPED` 项不创建 Topic、不注入候选 ID；休息项身份仍保留在 manifest 中但没有对应 Markdown。

## 边界与未完成事项

- Learning Path 仍为 draft / MAPPING_REVIEW_REQUIRED；本次不修改该 mapping 审核结论。
- 所有内容都是离线静态草稿，仍需人工事实校对、来源审阅与逐项内容审核；构建和静态校验通过不等于内容正确性批准。
- 按 Issue #50 与 [Learning Unit v0.1 合同](LEARNING_UNIT_V01.md)，本批 Markdown 不是 runtime Learning Unit / Topic Payload / Progress / Review / completion fact；[PR #51 Pilot 报告](../content/CONTENT_AUTHORING_PILOT_01.md)记录的 `CONTENT_MODEL_GAP` 仍然有效。
- 本次不改 Learning Payload runtime schema、Planner、Progress、Review、Taxonomy、UI 或运行时 AI 依赖；不把单元接入运行时学习流程。
- 第三方教材、题库、讲义、PDF 或 Prompt 正文不随仓库发布；来源以路径和 SHA-256 指纹追踪，版权许可不由 ZIP 所有权推定。
- 索引：[`content/learning-units/system-architect-checkin/README.md`](../../content/learning-units/system-architect-checkin/README.md)。
