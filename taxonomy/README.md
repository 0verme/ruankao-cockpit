# Taxonomy 边界

本目录本轮只定义未来边界，不实施 Taxonomy v0.1，不创建正式 topic 映射表，也不批量标注题目。

## 未来最小字段

未来的 Knowledge Topic 至少需要：

```text
topic_id
name
parent_id
aliases
source mappings
taxonomy version
confidence
```

示意（仅用于说明字段，不代表已冻结的 taxonomy）：

```yaml
topic_id: ARCH.QUALITY.ATTR
name: 质量属性
parent_id: ARCH.QUALITY

aliases:
  - 软件质量属性
  - 架构质量属性

sources:
  - syllabus
  - textbook

confidence: high
```

## 维度分离

```text
topic
```

和：

```text
capability
```

不能混为一个层级。Topic 用于描述知识内容、来源和层级；Capability 用于描述案例任务中的分析与作答能力。一个案例题可以关联多个 topic，也可以关联一个或多个 capability。

## 后续入口

下一阶段先通过小规模归一化演练确定 ID、别名、来源映射和置信度规则，再决定 Taxonomy v0.1 的具体数据格式。
