# 当前架构方向

本阶段只记录方向，不提前设计完整软件架构，也不初始化 UI、数据库或具体服务。

```text
Sources
   ↓
Source Metadata
   ↓
Normalized Taxonomy
   ↓
Golden Set
   ↓
Progress Model
   ↓
Adaptive Planner
   ↓
Cockpit UI
```

这条链路表达项目的依赖顺序：先保留来源与版权边界，再稳定元数据和归一化模型，之后才验证进度规则与自适应计划，最后考虑控制面展示。

```text
当前阶段：
Taxonomy v0.1 + Golden Set Design + Small Validation Sample

下一阶段：
根据 validation report 决定 Golden Set 是否扩量；不进入 Progress Engine 或 UI
```

本轮已落地：

- `taxonomy/`：13 个 L1 domain、27 个 L2 topic、110 个 L3 subtopic，以及 alias、provenance、confidence 和 unresolved contract；
- `taxonomy/capabilities.json`：独立的 Case Capability v0.1；
- `data/golden-set/`：JSON schema 与 26 道综合知识、11 道案例子问题的小样本；
- `docs/TAXONOMY_SOURCE_INVENTORY.md` 与 `docs/TAXONOMY_V01_VALIDATION.md`：source schema 盘点和验证结论。

本轮未实现 Progress Engine、Adaptive Planner、30 天计划实例化、数据库或 UI。
