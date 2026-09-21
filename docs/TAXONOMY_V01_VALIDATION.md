# Taxonomy v0.1 Validation Report

> 验证范围：Canonical Taxonomy v0.1、Case Capability v0.1、Golden Set contract 和 Phase 1 baseline sample。
>
> 本报告不是 1822 道题的全量清洗报告，也不把第三方回忆版答案升级为官方事实。
>
> **历史快照说明**：本文中的 26 道综合题 / 11 道案例是 Phase 1 基线；Phase 2 扩量后的 100 / 48 结果、覆盖率和 validator 变化见 [GOLDEN_SET_EXPANSION_VALIDATION.md](GOLDEN_SET_EXPANSION_VALIDATION.md)。

## 1. Recommendation

# PASS_WITH_CHANGES

依据（Phase 1 快照）：模型已经能在合理粒度下表达官方大纲、现行教材、主要 source schema、26 道综合题和 11 道案例子问题；没有使用 canonical `OTHER`，Topic / Capability 已分离，所有 mapping 和样本都能通过 source commit/path 追溯。

`PASS_WITH_CHANGES` 的“changes”是进入下一阶段前需要继续保留和收敛的有限边界：

1. 分解 `zhang-986: other`、`wujiaming88: 新技术专题` 和旧版安全章节时，继续依赖题目级上下文，不把候选直接转成确定统计；
2. 对 `QUALITY.ATTRIBUTES`、`DATA.CACHE` 这类上位 topic 保留 parent-level annotation，扩量时只在重复出现稳定边界后再增加 L3；
3. 对有多版本题面冲突的案例继续使用 `reviewed`，不能因为 Golden Set 要扩量而改写 source provenance。

这些事项不会阻塞 Phase 1 contract；Phase 2 已在独立 worktree 完成扩量，后续仍必须继续运行 validator 和人工 review。

## 2. Inventory / source coverage

### 2.1 Official outline

- 科目一 13 个官方知识领域：**13/13 可映射**，每个都有 `high` 的 outline domain mapping；
- 科目二 9 个官方案例专题：**9/9 可映射**；
- 科目三论文 5 个选题范围：已在 source inventory 和论文专题 mapping 中作为交叉证据保留，未把写作能力伪装成 topic。

### 2.2 Textbook

- 现行第 2 版教材 20 章：**20/20 有 chapter mapping**；
- 第 5 章同时映射软件工程与建模；第 6 章同时映射数据库与分布式数据；第 12、16、17 章保留基础 / 架构实践的一对多关系；
- 第 20 章是跨主题论文写作指导，当前挂在 `ARCH.FOUNDATION`，confidence 为 `medium`，并在 mapping note 中明确它不是独立知识域。

### 2.3 Major source taxonomy

| source | 已记录的直接 mapping | unresolved | 结论 |
|---|---:|---:|---|
| `younghong1992` | 42 | 0 | 大纲 / 教材锚点最稳定；题面仍保留非官方和版本冲突属性 |
| `wujiaming88` | 9 | 1 | 专题、案例模板和论文分类可作为归一化证据，不能直接作为权重 |
| `zhang-986` | 12 | 2 | module 可作 source metadata；`other` 和抽取占位值不能直接聚合 |
| `xiaomabenten` | 2 | 2 | PDF 目录主要是索引线索，不足以做题目级分类 |
| `altria1979` | 3 | 1 | 旧版章节和个人重点可作低置信结构参考 |
| `nye-2` | 11 | 3 | M01–M10 多数可映射；M00/M11/M12/M14 暴露 Topic 与学习 / 能力维度边界 |

另有 `longyi-xw`、`sobermh`、`xxlllq`、`ruankaodaren` 的结构或版权信息已纳入 inventory；它们没有被伪造为题目级 canonical mapping。

## 3. Taxonomy shape

- L1 Domain：**13**
- L2 Topic：**27**
- L3 Subtopic：**110**
- Topic 总数：**150**
- Alias 记录：**34**
- Source mapping：**79**
- Unresolved mapping：**9**
- Case Capability：**13**

L1 主要 Domain：

```text
SYSTEM / INFO / SEC / SOFTWARE / DATA / ARCH / QUALITY /
RELIABILITY / EVOLUTION / EMERGING / GOVERNANCE / MATH / LANGUAGE
```

这 13 个 L1 与官方科目一大类对齐；教材与案例的额外结构通过 L2/L3 进入，而不是新建与官方大纲平行、无法聚合的第二套根节点。

## 4. Golden Set sample coverage

| 样本 | 数量 | 至少一个 topic | 至少一个 capability | 跨 topic |
|---|---:|---:|---:|---:|
| 综合知识 | 26 | 26/26 | 0（按 contract 为空） | 7/26 |
| 案例子问题 | 11 | 11/11 | 11/11 | 9/11 |

案例样本使用了 21 个 unique topic 和 10 个 unique capability；11/11 个案例都需要两个或更多 capability，说明 capability 不能压缩成一个单标签。

样本主动覆盖的边界包括：

- `SYSTEM.COMPUTER.PERFORMANCE` 与 `QUALITY.ATTRIBUTES.PERFORMANCE` 的基础性能 / 架构质量语境；
- `DATA.DATABASE`、`DATA.CACHE`、`DATA.DISTRIBUTED` 的重叠；
- `ARCH.FOUNDATION.STYLES` 与 `ARCH.CLOUD_NATIVE.EVENT_DRIVEN` 的不要误合并；
- `SEC.INFORMATION`、`SEC.ARCHITECTURE` 与安全关键系统的区别；
- UML / 解释器 / 故障树等知识主题与 `CASE.MODELING`、`CASE.ROOT_CAUSE_ANALYSIS` 的分离；
- 2024 上半年 UML、2025 上半年知识图谱的来源版本 / 回忆冲突。

综合样本和案例样本的**记录级 topic mapping rate 均为 100%**，但这不等于 source 全量可归一；9 条 unresolved source value 仍明确保留在单独文件中。

## 5. Ambiguity findings

### 5.1 One-to-many

Source mapping 中有 **27 条一对多映射**。典型例子：

- `zhang-986: architecture` → `ARCH.FOUNDATION`、`ARCH.CLOUD_NATIVE`、`ARCH.SOA`、`QUALITY`；
- `zhang-986: database` → `DATA.DATABASE`、`DATA.CACHE`、`DATA.DISTRIBUTED`；
- `Nye-2: M07 计算机网络与分布式系统` → 网络、分布式数据、通信架构；
- 案例 `Redis` 锁 / 缓存失效题 → 数据、分布式一致性、可用性和多个 capability。

因此 source category 不被设计成单值 `module` 替换，Golden Set 的 `topics[]` 和 `capabilities[]` 都是数组。

### 5.2 Unresolved

9 条 unresolved：

- `zhang-986` 的 `other` 和 `PDF自动抽取`：2；
- `nye-2` 的导学、案例能力、论文素材模块：3；
- `wujiaming88` 的 `新技术专题`：1；
- `altria1979` 的旧版安全性 / 保密性章节：1；
- `xiaomabenten` 的 PDF 资料集合和错误版本文件名：2。

它们都包含 reason、candidate topics（可为空）和 evidence；没有一条被替换为 canonical `OTHER`。

### 5.3 Alias collision

发现并显式记录 1 组 collision：`安全` → `SEC.INFORMATION` 或 `SEC.ARCHITECTURE`。解决策略不是猜，而是读取 `source_path`、`source_value` 和邻近上下文；真正跨越两者的题目可以保留两个 topic。

### 5.4 Capability ambiguity

`CASE.QUALITY_ATTRIBUTE_ANALYSIS`、`CASE.RELIABILITY_DESIGN`、`CASE.SOLUTION_TRADEOFF` 经常在同一小问共存，但它们分别描述分析对象、可靠性方案和推理动作；它们没有进入 Topic hierarchy。`CASE.SCORING_POINT_EXPRESSION` 只描述答案表达要求，也没有被误写成“案例专题”。

## 6. Structural assessment

### Not too coarse

- 仅有 13 个 L1 不足以表达题目，但 27 个 L2 / 110 个 L3 已能区分关系数据库、规范化、NoSQL、缓存失效、分布式锁、质量属性、ATAM、架构风格、微服务、嵌入式安全关键等稳定骨架；
- 26 道综合题中只使用 7 条跨 topic 记录，11 道案例中 9 条跨 topic，且没有被迫归入 `OTHER`；
- source-level 宽分类仍允许挂在 L2，避免为每个题目制造 L3。

### Not too fine

- 样本没有出现“每题一个独立 topic”；重复考点能回到同一 L3；
- `DATA.CACHE`、`QUALITY.ATTRIBUTES` 等 parent-level mapping 是有意保留的粒度，不是临时兜底；
- `CONTAINERS_SERVERLESS`、`5G_SDN` 等未来若在扩量中出现稳定分裂证据，再考虑 v0.2 拆分。

### Hierarchy / ID

- parent relationship validator 通过，无循环；
- stable ID 使用大写段和点分隔，未依赖中文名称；
- 本轮没有发现必须修改既有 ID 才能表达样本的情况；
- 旧版章节号只出现在 source value / unresolved，不污染现行 canonical ID。

## 7. Golden Set contract assessment

当前 contract 足以表达：

```text
source reference
→ one or more Knowledge Topics
→ (case only) one or more Case Capabilities
→ human review state + confidence + note
```

它为未来的 `question → topic → capability → learning progress` 留出了稳定的多值引用和版本化入口，同时没有越界实现 score、accuracy、mastery、review_due 或 planner。后续 Progress Model 仍需另行定义 attempt / score evidence；不能把当前 annotation 当成学习指标。

Review status `candidate → reviewed → confirmed / rejected` 已能阻断 AI 建议直接变成确认事实。当前样本中的 `reviewed` 专门保留来源冲突，不用清洗动作抹平证据差异。

## 8. Gate checklist

- [x] 大纲主要分类可映射（13/13）
- [x] 教材 20 章可映射（20/20）
- [x] 主要 source taxonomy 已盘点并可部分归一
- [x] stable topic_id 规范明确
- [x] alias 能处理主要命名差异，并有 collision 机制
- [x] provenance 可追溯
- [x] confidence 是固定枚举并有语义
- [x] unresolved 可显式保存
- [x] Topic 与 Capability 分离
- [x] 26 道综合样本可表达
- [x] 11 道案例子问题可表达
- [x] 没有被迫塞进 `OTHER`
- [x] 样本不需要频繁修改既有 topic_id

## 9. Next recommendation

可以进入 **Golden Set Expansion**，但应优先扩充“难标”题而不是机械扩充数量：

1. 先扩充案例 capability 的 reviewed 样本；
2. 再按 source 分层增加综合题，验证 `module → topic[]` 的稳定性；
3. 对 `other`、新技术、旧版安全分类保持 unresolved，直到有题目级 source context；
4. 在扩量完成前不实现 Progress Engine、30-Day Plan 实例化或 UI。
