# AGENTS.md

本文件定义 `ruankao-cockpit` 的长期项目约束。

## Project Boundary

本项目不负责重新生产完整软考教材。

默认优先：

```text
index
metadata
mapping
source reference
```

而不是复制第三方资料。第三方正文、题库、教材、讲义和 PDF 默认通过来源引用、索引或本地导入处理，不作为正式仓库的默认内容资产。

## Copyright

禁止假设：

```text
GitHub 可以访问
=
可以复制并重新发布
```

对第三方内容必须区分：

```text
A. code reusable
B. structure / model reference
C. index / link only
D. no redistribution
```

License 不明确时，默认不复制原文。仓库自有代码的许可证选择不能自动覆盖第三方正文、题库、图片、PDF 或衍生资料。

## Taxonomy

未来 taxonomy 必须具备：

```text
stable id
versioned
aliases
source provenance
confidence
```

必须明确：

```text
Knowledge Topic
!=
Case Capability
```

Knowledge Topic 描述知识内容及其层级；Case Capability 描述案例中需要完成的分析、建模、权衡或表达能力。二者是不同维度，不能混为一个层级。

## Progress

以下指标原则上必须 deterministic：

```text
score
accuracy
coverage
completion
streak
review_due
weak_modules
mastery
```

AI 可以用于：

```text
classification assistance
explanation
essay feedback
error summarization
```

但 AI 不应该凭感觉直接制造事实型学习指标。任何可影响计划的指标都必须能从明确的输入、版本化规则和可复盘记录中计算出来。

## Architecture Priority

优先顺序：

```text
domain correctness
>
data contract
>
rule correctness
>
UI
```

在 Domain / Progress Model 稳定前，不主动初始化大型前端技术栈，也不以 UI 反推尚未确定的数据模型。

## Testing

使用风险分级测试：

普通改动先跑最小相关测试。

以下情况扩大测试：

- domain model
- shared contract
- taxonomy migration
- parser
- progress engine
- final merge
- release

测试应优先验证领域不变量、数据契约和确定性规则，而不是只验证展示层快照。
