# Content Authoring Pilot 01：前 7 个打卡项离线内容生产实验

> **Pilot 状态：`CONTENT_MODEL_GAP`，并发现若干 `SOURCE_GAP`。** 本报告只覆盖 `checkin-001`–`checkin-007`；不代表其余 103 个学习项。
>
> Pilot 起点：用户 preflight 同步的 PR #45 merge commit `8974f5f3c49131beedb8127a6e4e58a1425e4c28`。并行窗口随后合并了 #49 与 Learning Unit v0.1 PR #48；本分支在 PR 前 rebase 到最新 `origin/main` `9d250e49f65b234da48f2131e345fde11eadc7eb`。关联 [#47](https://github.com/0verme/ruankao-cockpit/issues/47)、[#46](https://github.com/0verme/ruankao-cockpit/issues/46)、[#48](https://github.com/0verme/ruankao-cockpit/pull/48)、[#44](https://github.com/0verme/ruankao-cockpit/issues/44)、[#45](https://github.com/0verme/ruankao-cockpit/pull/45)、[#33](https://github.com/0verme/ruankao-cockpit/issues/33)、[#27](https://github.com/0verme/ruankao-cockpit/issues/27)。Learning Unit v0.1 identity/mapping/completion 语义已冻结；runtime 未实现，本 Pilot 未修改该 contract。

## Scope

严格依照 [`system-architect-checkin-v1.json`](../../data/learning-paths/system-architect-checkin-v1.json) 的来源身份、原顺序及 mapping，只处理前 7 个学习项。Learning Path 仍是 draft；本 Pilot 不重排、不修改 Path、Learning Unit、Progress 或 Planner Schema，也不处理 `checkin-008` 以后内容。

原始归档由用户提供。本轮只按上述七项的 `source_file` 从 ZIP 提取七个 Markdown 到临时目录进行读取，随后清理；不提交 ZIP、全量原始 Markdown、图片、刷题地址或完整 Prompt。归档 SHA-256 和大小只沿用 Learning Path 已登记的来源指纹，本 Pilot 未重新计算。

## Input

### Prompt 与知识点提纲

七份输入都含 `wh-plain-explainer` 形式的“根据知识点列表讲解 [软件工程]”指令，配有当日知识点标题与分层提纲。该 Prompt 在此仅作为 **offline authoring aid**：不是 runtime prompt、domain truth、source evidence 或 Progress fact；不调用 OpenAI / Claude / Gemini 或其他模型 API，也不配置 API Key。

知识点范围按原档案提纲归纳为：

1. 软件工程概念、生命周期与三要素；
2. 瀑布、演化/原型、螺旋、RAD、喷泉、形式化方法；
3. RUP；
4. 敏捷开发与方法；
5. V/W 模型与质量左移；
6. 基于构件的软件开发（CBSD/CBSE）；
7. 模型驱动开发（CIM/PIM/PSM）。

知识点标题决定“今天准备讲什么”，不自动成为已核实知识事实。原提纲、Prompt、图片和答案均没有作为 payload 来源证据。

### Path mapping 与仓库来源

- Path 映射状态：`checkin-001`–`004` 为 `MERGE` 到 `SOFTWARE.ENGINEERING.PROCESS`（同一 mapping group）；`checkin-005` 为 `SPLIT` 到 `SOFTWARE.ENGINEERING.PROCESS` 与 `SOFTWARE.ENGINEERING.TESTING`；`checkin-006` 精确映射到 `SOFTWARE.ENGINEERING.COMPONENTS`；`checkin-007` 精确映射到 `SOFTWARE.MODELING.FORMAL_MODELING`。
- 教材来源映射登记了不可变版本 `younghong1992` @ `c467a7cbc16970c52cf6d723badbb22938963ae6` 的第 5 章，映射到软件工程/建模父 Topic；章节中可定位到软件工程定义、过程模型、敏捷、RUP、测试和 `5.6` 基于构件的软件工程。构件 payload 只引用可追踪的教材章节/小节索引，没有复制正文。
- 考试大纲来源将“软件工程基础知识”映射到 `SOFTWARE` 父级；只能支持大纲覆盖声明，不能推导考频。
- Learning Unit v0.1（[#46](https://github.com/0verme/ruankao-cockpit/issues/46) / [PR #48](https://github.com/0verme/ruankao-cockpit/pull/48)）现已冻结：每个 Path Item 独立使用 `(path_id, path.version, item_id)`；MERGE 项不合并，SPLIT 项仍为一个 Unit 并关联全部 Topic；Unit 可关联一个或多个现有 Topic-scoped Payload。契约没有实现运行时或决定 Unit 如何呈现/选择 Payload。
- Golden Set 中有已确认的综合知识软件过程模型样本 `2024-h2-comprehensive-q20`、软件测试基础样本 `2024-h2-comprehensive-q55`，以及形式化模型表示样本 `2025-h2-comprehensive-q42`（嵌入式语境）。后者不支持完整的 MDA/CIM/PIM/PSM 定义。以上记录只能证明对应索引样本存在；本 Pilot 不将单题说成高频，也未把未经确认的 reviewed 样本作正式题源。
- 相关索引详见 [`taxonomy/source-mappings.json`](../../taxonomy/source-mappings.json)、[`CONTENT_SOURCE_AUDIT.md`](../CONTENT_SOURCE_AUDIT.md) 及 [`comprehensive.sample.json`](../../data/golden-set/comprehensive.sample.json)。

## Per-item Result

| item | title | mapping | payload fit | source fit | verdict |
|---|---|---|---|---|---|
| `checkin-001` | 软件工程概述、生命周期、三要素 | `MERGE` → `SOFTWARE.ENGINEERING.PROCESS` | Unit identity 已由 LU v0.1 区分；但 Topic Payload/Experience 无法选择此 Unit 专属的三要素/生命周期内容片段 | 部分：第 5 章支持软件工程/生命周期；当前已审计索引没有为“三要素及关系”提供精确证据锚点，需补来源或人工核验 | `CONTENT_MODEL_GAP`（兼有 SOURCE_GAP） |
| `checkin-002` | 软件开发过程模型 | `MERGE` → `SOFTWARE.ENGINEERING.PROCESS` | Unit identity 已独立；但 Topic Payload/Experience 无法选择此 Unit 专属的过程模型内容片段 | 部分：来源支持瀑布、原型、螺旋及净室软件工程；当前索引来源没有支持提纲中的 RAD、喷泉模型具体事实 | `CONTENT_MODEL_GAP`（兼有 SOURCE_GAP） |
| `checkin-003` | 统一过程 RUP | `MERGE` → `SOFTWARE.ENGINEERING.PROCESS` | Unit identity 已独立；但没有 Unit-specific Payload 选择/定位 | 有：教材第 5 章 `5.1.4 RUP` 支持该主题；本结论不表示每个提纲细项都已逐条二次校核 | `CONTENT_MODEL_GAP` |
| `checkin-004` | 敏捷开发 | `MERGE` → `SOFTWARE.ENGINEERING.PROCESS` | Unit identity 已独立；但没有 Unit-specific Payload 选择/定位 | 有：教材第 5 章 `5.1.3` 有敏捷模型/方法来源；不使用“高频”表述 | `CONTENT_MODEL_GAP` |
| `checkin-005` | V/W 模型与质量左移 | `SPLIT` → `SOFTWARE.ENGINEERING.PROCESS` + `SOFTWARE.ENGINEERING.TESTING` | LU v0.1 已定义一个 Unit 关联两个 Topic；但当前 TopicExperience 一次只呈现一个 Topic，没有 Unit 级多 Topic 体验 | `SOURCE_GAP`：已审计的第 5 章/大纲 mapping 未提供 V/W 模型与“质量左移”提纲的精确证据锚点 | `CONTENT_MODEL_GAP`（兼有 SOURCE_GAP） |
| `checkin-006` | 基于构件的软件开发 | `EXACT` → `SOFTWARE.ENGINEERING.COMPONENTS` | 是：一个 active L3 可由当前 Topic-level Payload 正确标识；产出 1 条静态 Payload | 有：教材第 5 章 `5.6.1`–`5.6.3` 覆盖构件模型、CBSE 过程和构件组装；大纲引用只支持领域覆盖 | `READY` |
| `checkin-007` | 模型驱动开发 | `EXACT` → `SOFTWARE.MODELING.FORMAL_MODELING` | 结构上可放进单 Topic 文件，但因来源缺口不生成 | `SOURCE_GAP`：虽有软件建模父级的第 5 章映射，当前审计锚点没有覆盖 MDA、CIM、PIM、PSM 的来源证据；Golden Set 的形式化模型样本也不足以支持该层级定义 | `SOURCE_GAP` |

`checkin-003/004` 的来源匹配与 Payload 内容选择是两回事：来源足以支持写作，不代表当前 Topic Experience 能按不同 Unit 呈现不同学习片段。

## Model Findings

### Repeated Topic：Learning Unit identity 已解；Unit-specific 内容选择仍是 `CONTENT_MODEL_GAP`

Learning Unit v0.1（[#46](https://github.com/0verme/ruankao-cockpit/issues/46)、[PR #48](https://github.com/0verme/ruankao-cockpit/pull/48)）已明确每个 Path Item 都是独立 Unit，identity 为 `(path_id, path.version, item_id)`；MERGE group 不折叠 Unit。这一部分不再是未决身份问题。

Learning Payload 仍然是 **one active L3 Topic → one Payload**：文件路径为 `data/learning-payloads/<topic_id>.json`；`load_learning_payload(topic_id)` 按 Topic ID 加载，并要求 payload 的 `topic_id` 与请求一致。`TopicExperience` 只接受一个 `learning_payload`，也只验证它属于所请求 Topic；没有 unit/item 输入，也没有选择 Topic Payload 内某日片段的机制。

因此 `checkin-001`–`004` 可以按 LU v0.1 成为四个不同 Unit，但当前内容体验不能表达“此 Unit 显示自己的不同知识提纲/片段”。Unit contract 允许多个 Unit 关联同一个 Topic Payload；若只要求反复展示完整的同一张 Topic 卡，结构上可关联，但那不能验证这四个来源项的连续、差异化学习内容。不能给 Topic ID 加日期、复制 Taxonomy、覆盖 Payload，或把四天的提纲压成一张卡。**结论：`CONTENT_MODEL_GAP: 现有 Topic-level Learning Payload / Topic Experience 无法表达 sequential Learning Units 的差异化内容选择`。**

### SPLIT item：Unit 语义已定义，Topic Experience 尚无 Unit 级组合展示

Learning Unit v0.1 已明确 `checkin-005` 是一个 Unit，关联 PROCESS 与 TESTING 两个 Topic，不拆成两个任务。当前 Payload 可以分别按两个 Topic 提供内容，但 `TopicExperience` 一次只构建一个 Topic；没有以 `learning_unit/<path_id>/<version>/<item_id>` 为入口并组合多个 Topic Payload 的体验。不得在本 Pilot 自行定义呈现/顺序/完成行为。

### Topic Experience 兼容性

当前 Topic Experience 已能承载 `objectives`、短 `core_points`、`exam_focus` 和逐条来源引用；缺少材料时会明确呈现 unavailable，不运行时生成。`checkin-006` 是本批唯一同时满足单 Topic 身份与已审计来源支持的可提交样本：新增 Payload 有 3 个目标、2 个核心点、1 个考纲语境项，正文均链接到同 Topic 可验证来源，不声称题目频率。契约没有学习单元身份与估算时长字段，本 Pilot 不新增字段。

### Prompt 与来源结论

现有 Prompt 对“给定提纲、离线写简短解释”的生产流程有用；`checkin-006` 证明能收敛为当前 Topic Experience 结构。但 Prompt 自身不能补足来源证据，也不能解决 Path item 与 Topic Payload 身份不一致。基于仅 7 个样本，不能据此认定所有 Prompt 输出均稳定、所有提纲均有来源，或其余路径均能表达。

## Recommendation

**不建议直接扩大到下一批内容。** Learning Unit v0.1 的 identity、MERGE/SPLIT 关系和 completion semantics 已由 #46 / PR #48 冻结；本 Pilot 不重做这些决定。复评下一批前应等待/确认后续内容体验与运行时边界：

1. 对同 Topic 的多个 Units，是接受每个 Unit 关联并重复呈现完整 Topic Payload，还是需要 Unit-specific 内容片段/选择；当前 `learning_payload/v0.1` 与 `TopicExperience` 没有该选择机制。
2. SPLIT Unit 如何在一个 Unit 入口下定位/呈现多个 Topic Payload；LU contract 定义关联及“一 Unit”，但 Topic Experience 仍是单 Topic read model，运行时未实现。
3. 只有 Path 经 mapping review/approved 且独立 completion fact、版本化 Planner target/integration 等门槛实现后，才可讨论将这些 Unit 接入计划；本 Pilot 不改变 Planner。
4. 对 `SOURCE_GAP` 补充经审计来源锚点或明确保留待核验草稿；不能把原始 Prompt 当来源。

以上建议只根据这 7 个样本，不推广到 110 个学习项。

## Deliverables and verification

- Added static Payload: [`SOFTWARE.ENGINEERING.COMPONENTS.json`](../../data/learning-payloads/SOFTWARE.ENGINEERING.COMPONENTS.json)，仅对应 `checkin-006` 可安全表达部分。
- PASS：Learning Payload loader/schema tests（8 项）；Topic Experience tests（4 项）；`apps.test.tsx` 最小前端渲染测试（12 项）。本机 `jsonschema` 不在环境中，测试依赖临时安装到 `/tmp`；前端 `npm ci` 默认 postinstall 遇到 esbuild `EACCES`，在忽略安装脚本并修复本地忽略目录中的二进制执行位后以 Vitest 直接运行。未改动任何依赖清单或运行时代码。
- PASS：`git diff --check`。
- `Runtime AI Dependency: NONE` · `Schema Changes: NONE`。
