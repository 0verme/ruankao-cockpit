# Canonical Taxonomy v0.1

> 当前状态：第一版正式领域模型，已用小批量真实综合题和案例子问题验证。
>
> 本目录只保存自有 taxonomy、映射、审核元数据和 capability 枚举；不保存第三方教材、题库、PDF、OCR、答案或大段题干。

## 1. 文件

本目录的机器数据统一使用 **JSON**，避免 YAML 解析依赖和多套序列化格式：

- `taxonomy.json`：Knowledge Topic 节点；
- `aliases.json`：有来源、可审计的 source-scoped alias；
- `source-mappings.json`：来源分类值到 canonical topic 的映射和 source catalog；
- `unresolved-mappings.json`：不能可靠归一化的来源值；
- `capabilities.json`：独立的 Case Capability 枚举。

## 2. Topic schema

每个 topic 至少包含：

```json
{
  "id": "QUALITY.ATTRIBUTES.AVAILABILITY",
  "name": "可用性",
  "parent_id": "QUALITY.ATTRIBUTES",
  "level": 3,
  "status": "active"
}
```

`description`、权重、考试概率和主观重要度不在 v0.1 topic 节点中。任何排序应另有可追溯的统计输入，不能在 taxonomy 中写入 `87`、`0.82` 一类伪精确值。

## 3. ID convention

- 大写、机器可读：每个段使用 `[A-Z0-9_]+`；
- 层级分隔符固定为 `.`；
- 一段 = L1 Domain，二段 = L2 Topic，三段 = L3 Subtopic；
- ID 不以中文名称拼接，因此中文名称可以改进而不必随意改 ID；
- `CASE.*` 只属于 capability 文件，不得进入 topic hierarchy。

当前骨架锚定官方科目一 13 类 L1：

`SYSTEM`、`INFO`、`SEC`、`SOFTWARE`、`DATA`、`ARCH`、`QUALITY`、`RELIABILITY`、`EVOLUTION`、`EMERGING`、`GOVERNANCE`、`MATH`、`LANGUAGE`。

教材第 12–19 章和官方案例 9 类作为这些 domain 下的跨章节 topic；这避免把“案例专题”和“Knowledge Topic”混为同一层级。

## 4. Alias

Alias 是**有范围的来源别名**，不是无来源的同义词列表。每个 alias 必须带：

- `source_id`、`source_commit`、`source_path`、`source_value`；
- `canonical_topic_id`；
- `confidence`；
- 如字符串在不同来源含义不同，带 `collision_group_id`。

例如 `安全` 同时可能表示 `SEC.INFORMATION` 或 `SEC.ARCHITECTURE`。v0.1 不从字符串本身猜测，而要求使用 source path、邻近标题或题目上下文。

## 5. Provenance 与 confidence

正式 provenance 只使用：

```text
source_id
source_commit
source_path
source_value
```

`source_path` 是该仓库快照内的相对路径，不是本机路径。

confidence 枚举固定为：

- `high`：source value 与 canonical boundary 有直接、稳定证据；
- `medium`：需要跨字段、跨章节或语义解释，但候选边界明确；
- `low`：来源分类过宽、版本冲突或证据不足，只能作为候选索引，不应直接驱动事实型统计。

## 6. Topic 与 Case Capability

Knowledge Topic 描述“学什么”：数据库、缓存、架构风格、质量属性、安全、分布式等。

Case Capability 描述“在案例中做什么”：识别问题、分析根因、架构选型、方案设计、建模、权衡、采分点表达等。

二者是独立维度。案例记录可以同时引用：

```json
{
  "topics": ["DATA.CACHE.CACHE_FAILURE", "QUALITY.ATTRIBUTES.AVAILABILITY"],
  "capabilities": ["CASE.ROOT_CAUSE_ANALYSIS", "CASE.SOLUTION_TRADEOFF"]
}
```

不能把 `数据库`、`缓存`、`安全` 或 `微服务` 定义成 capability，也不能把 `ROOT_CAUSE_ANALYSIS` 塞进 topic hierarchy。

## 7. 如何新增节点

1. 先在 source inventory 中确认来源的真实分类和证据路径；
2. 检查已有节点是否可以表达；优先增加 mapping 或 alias，不要为每个新题目建节点；
3. 只有当新概念具有稳定边界、跨至少一个真实 source 或样本、且现有父节点过粗时，才增加 L2/L3；
4. 给新节点分配唯一 ID，补充 parent、level、status；
5. 添加 source mapping、confidence 和 validation sample；
6. 运行 `python3 scripts/validate_taxonomy.py`。

## 8. 何时允许改 ID

- 只改中文 `name` / 描述：不需要改 ID，但应保留 changelog 说明；
- 发现原 ID 的概念边界错误、两个节点必须合并，或一个节点必须拆成不同概念：才允许改 ID；
- 改 ID 前须在 `unresolved-mappings.json` 或 validation report 记录旧 ID、影响范围、替代 ID 和理由；
- 不因为来源中文名称变化、翻译偏好或一题新技术出现而改 stable ID。

v0.1 不引入 migration framework；只要求把变更理由和受影响 mapping / golden records 写清楚。

## 9. 约束

- 不使用 `OTHER` 掩盖无法归类的问题；未决值进入 `unresolved-mappings.json`；
- 不把 source 的频次、红黄绿标记或个人重点转换成考试权重；
- 不复制第三方题面、教材正文、答案、OCR 或 PDF；
- 不实现 Progress Engine、mastery、review interval、planner 或 UI。
