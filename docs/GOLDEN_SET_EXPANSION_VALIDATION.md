# Phase 2 Golden Set Expansion Validation

- **阶段**：Phase 2 — Golden Set Expansion
- **分支**：`feat/golden-set-expansion`
- **验证日期**：2026-09-21
- **验证入口**：`python3 scripts/validate_taxonomy.py`

## 1. 范围与版权边界

本阶段扩充的是可复盘的真实题目索引与标注，不是第三方题库再发布。每条记录只保留：

- 来源仓库、immutable commit、仓库相对路径和题号；
- 自 authored 的短识别摘要；
- Topic / Case Capability 引用、confidence 和 review metadata。

没有把题干、选项、答案、解析、OCR、PDF 或完整案例正文写入 Golden Set。新增记录默认是 `reviewed`，并使用 `agent-assisted` 标注；没有把 AI 初审结果伪装成 `confirmed`。原有 35 条人工确认记录保持不变。

## 2. 扩量结果

| 文件 | Phase 1 基线 | Phase 2 结果 | 增量 | 说明 |
|---|---:|---:|---:|---|
| `data/golden-set/comprehensive.sample.json` | 26 | **100** | +74 | 以来源年份、题型主题和 L1 覆盖做分层抽样 |
| `data/golden-set/case.sample.json` | 11 | **48** | +37 | 优先补齐能力稀疏项，并加入多 Topic / 多 Capability 案例 |
| Golden Set 合计 | 37 | **148** | +111 | 35 `confirmed` + 113 `reviewed` |

### 2.1 综合题分层

综合题不是声称具有统计学代表性的随机样本，而是受来源可得性约束的工程分层样本：

| 时间层 | 记录数 | 选择目的 |
|---|---:|---|
| 2022–2024 | 19 | 保留较早架构、演化、治理和基础知识语境 |
| 2025 | 78 | 扩大近期真实题覆盖，覆盖架构、数据、质量、软件工程、安全和新技术 |
| 2026 | 3 | 引入另一来源仓库的最新题目，测试跨来源 provenance |

综合题最终覆盖 13/13 个 L1。100 条记录中，97 条来自 `younghong1992`，3 条来自 `wujiaming88`；2025 上半年占比较高是来源文件题目密度造成的偏斜，不能解读为考试权重。

### 2.2 案例题扩量

案例新增记录来自 2020 H2、2024 H1/H2、2025 H1/H2 和 2026 H1，覆盖缓存持久化、分布式锁、车载通信、GIS 存储、解释器、知识图谱、Redis 复制、区块链、弱网一致性、资源池和入侵检测等真实子问题。

最终案例来源分布为：`younghong1992` 44 条、`wujiaming88` 4 条。所有 48 条案例记录都有 `case_id`、`sub_question_id` 和题号级 `source_question_id`；独立题号检查为 **148/148 可定位、无重复 source question ref**。

## 3. Topic / Capability 边界验证

### 3.1 规则

- **Knowledge Topic** 只描述知识内容、层级和来源语义；
- **Case Capability** 只描述案例中要完成的识别、分析、建模、权衡或表达动作；
- 综合题的 `capabilities` 必须为空；
- 案例题至少有一个 capability，可以同时引用多个 Topic 和多个 Capability；
- 不把 `CASE.*` 放进 Topic，也不把知识 Topic 放进 Capability；
- 没有新增 `OTHER`、`UNKNOWN`、`MISC` 或 `UNCLASSIFIED` canonical ID。

### 3.2 案例能力覆盖

下表是引用该能力的案例记录数，不是 AI 生成的分数，也不代表掌握度：

| Case Capability | 案例数 | Case Capability | 案例数 |
|---|---:|---|---:|
| `CASE.PROBLEM_IDENTIFICATION` | 6 | `CASE.ROOT_CAUSE_ANALYSIS` | 6 |
| `CASE.QUALITY_ATTRIBUTE_ANALYSIS` | 7 | `CASE.ARCHITECTURE_SELECTION` | 9 |
| `CASE.ARCHITECTURE_DESIGN` | 18 | `CASE.MODELING` | 14 |
| `CASE.DATA_DESIGN` | 17 | `CASE.DISTRIBUTED_DESIGN` | 12 |
| `CASE.PERFORMANCE_ANALYSIS` | 7 | `CASE.RELIABILITY_DESIGN` | 8 |
| `CASE.SECURITY_DESIGN` | 4 | `CASE.SOLUTION_TRADEOFF` | 16 |
| `CASE.SCORING_POINT_EXPRESSION` | 10 |  |  |

13/13 个 capability 均有至少 4 条 `reviewed` 或 `confirmed` 案例引用。案例中 44 条为多 Capability，51 条 Golden Set 记录为多 Topic，说明两套维度没有被压扁成一个层级。

代表性边界样本包括：

- `gs-case-2020-h2-1-q1`：Topic 是架构风格与性能，Capability 是架构选择、权衡和性能分析；
- `gs-case-2025-h1-5-q2`：Topic 是分布式一致性与安全属性，Capability 是安全设计、架构设计和分布式设计；
- `gs-case-2026-h1-5-q2`：Topic 是管道/过滤器、事件驱动和性能，Capability 是架构选择、架构设计、性能分析和权衡。

## 4. Taxonomy 覆盖诊断

Validator 按 Topic 引用及其 parent closure 计算覆盖，覆盖诊断不是硬性通过门槛：

| 层级 | 已覆盖 | 总数 |
|---|---:|---:|
| L1 | **13** | 13 |
| L2 | 25 | 27 |
| L3 | 75 | 110 |

尚未被 Golden Set 直接覆盖的 L2 是 `ARCH.SYSTEM_PLANNING` 和 `ARCH.INFORMATION`。没有为了填满覆盖率而创造假样本或新增占位 taxonomy。当前 taxonomy 仍为 13 L1 / 27 L2 / 110 L3 / 150 nodes。

## 5. Provenance、状态与 unresolved policy

- Golden Set 使用 source catalog 中的固定 commit：
  - `younghong1992`: `c467a7cbc16970c52cf6d723badbb22938963ae6`；
  - `wujiaming88`: `9923d3efdd99729a318ae55a1d2505cf021f3a86`。
- 148 条记录均有非空 `source_question_id`；路径为仓库相对路径，没有写入本地绝对路径。
- 状态分布：`confirmed=35`、`reviewed=113`；confidence 引用分布为 `high=336`、`medium=28`，没有用低置信度映射掩盖边界。
- 既有 9 条 unresolved mapping 原样保留，没有把不明确来源静默映射为其他类别；也没有新增 `OTHER/UNKNOWN/MISC`。
- 2024–2026 部分题目来自回忆版或整理版，答案/版本可能存在冲突，因此新增记录保持 `reviewed`，后续由独立人工复核后再升级状态。

## 6. Validator 升级

`scripts/validate_taxonomy.py` 本阶段新增或强化：

1. 去除原来只允许小样本数量的硬编码范围，允许真实扩量；
2. 要求两个 sample 文件非空、每条记录至少一个 Topic，案例至少一个 Capability；
3. 要求 record ID 非空且跨两个文件不重复；
4. 要求每条记录有非空题号级 `source_question_id`，继续校验 source catalog、commit、相对路径和 parent relationship；
5. 禁止 canonical taxonomy 出现 `OTHER`、`UNKNOWN`、`MISC`、`UNCLASSIFIED` segment；
6. 输出 L1/L2/L3、Capability、review status、confidence、source distribution、多 Topic / 多 Capability 和 unresolved 数量诊断。

同时，`data/golden-set/schema.json` 明确了案例 Capability 非空、综合题 Capability 为空、Topic 非空和 canonical 禁止占位类别等不变量。

## 7. 旧 Topic ID 迁移

`docs/30_DAY_CURRICULUM_DRAFT.md` 中的历史示例已统一到当前 canonical IDs：

- 质量属性 → `QUALITY.ATTRIBUTES`；
- 架构风格 → `ARCH.FOUNDATION.STYLES`；
- 数据库规范化 → `DATA.DATABASE.NORMALIZATION`；
- 示例 Capability 也同步使用 `CASE.*` 稳定 ID。

全仓库搜索旧的前缀式 Topic 示例、旧短横线 Topic 示例和旧示例 Capability 名称，结果为 **0**。没有保留第二套可被运行时误用的 Topic ID。

## 8. 最终验证命令与结果

在独立 worktree 执行：

```bash
python3 scripts/validate_taxonomy.py
```

结果：

```text
PASS taxonomy schema validation
PASS mapping reference validation
PASS golden-set sample validation
PASS duplicate ID validation
PASS parent relationship validation
```

诊断摘要：

```text
comprehensive: 100; case: 48; total: 148
L1 coverage: 13/13; L2 coverage: 25/27; L3 coverage: 75/110
capability coverage: 13/13
review status: confirmed=35, reviewed=113
sources: wujiaming88=7, younghong1992=141
unresolved mappings: 9
```

## 9. 后续动作

1. 对 113 条 agent-assisted `reviewed` 记录进行独立人工确认，优先处理来源冲突和多 Capability 案例；
2. 补采 `ARCH.SYSTEM_PLANNING`、`ARCH.INFORMATION` 的真实题目后再提高 L2 覆盖，不用占位 Topic；
3. 若继续扩量，维持题号级 provenance、短摘要和不复制正文的版权边界；
4. 进度、掌握度和 review_due 仍必须由可复算输入与版本化规则计算，Golden Set 标注本身不直接制造学习指标。
