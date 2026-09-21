# Golden Set v0.1

> 当前状态：已定义数据契约，并提交一小批真实综合题 / 案例子问题作为 validation sample。

## 文件

- `schema.json`：Golden Set v0.1 契约；
- `comprehensive.sample.json`：26 道综合知识样本；
- `case.sample.json`：11 道案例子问题样本。

所有机器数据统一使用 JSON。样本只保留 source reference、题号 / 子问题号、最短识别摘要和 annotation，不复制第三方题干、选项、答案、解析、OCR 或 PDF。

## Record shape

```json
{
  "id": "gs-case-2025-h2-3-q3",
  "question_type": "case",
  "source": {
    "source_id": "younghong1992",
    "source_commit": "<immutable commit>",
    "source_path": "02.历年真题-清洗版/2025年下半年-系统架构设计师-案例分析.md",
    "source_question_id": "2025-h2-case-3-q3",
    "case_id": "2025-h2-case-3",
    "sub_question_id": "q3"
  },
  "topics": [
    {"topic_id":"DATA.CACHE.CACHE_FAILURE","confidence":"high"}
  ],
  "capabilities": [
    {"capability_id":"CASE.SOLUTION_TRADEOFF","confidence":"high"}
  ],
  "annotation": {
    "status":"confirmed",
    "annotator":"human",
    "reviewed_at":"2026-09-21",
    "note":"..."
  }
}
```

## Provenance

每条记录必须能够回到：

```text
source_id → source_commit → source_path → source_question_id
```

`source_path` 永远是第三方仓库内部的相对路径。正式仓库不写 Research Evidence 的 NAS 绝对路径。

## Topic / capability 多值关系

- `topics` 是 Knowledge Topic 多值数组；同一题可以同时属于数据库、缓存、分布式一致性和质量属性；
- `capabilities` 是 Case Capability 多值数组；案例可以同时要求根因分析、方案设计、权衡和采分点表达；
- 综合知识样本在 v0.1 的 `capabilities` 为空；未来若需要跨科任务关联，应新增明确契约，不把 capability 偷塞进 topic。

## Review status

固定枚举：

- `candidate`：机器 / 人提出，尚未人工核对；
- `reviewed`：人工检查过 source reference 和映射，但保留来源冲突或边界问题；
- `confirmed`：人工确认 source reference、topic / capability 归属和 confidence；
- `rejected`：明确不采纳，保留记录以避免重复建议。

AI 只能产生建议，不能把 `candidate` 直接当作已确认事实。当前样本的 `reviewed` 条目用于保留 2024 上半年 UML、2025 上半年知识图谱等来源版本冲突。

## 选样原则

样本不是训练集，也不是 1822 题的缩小版。它主动包含：

- 跨多个 topic 的综合题；
- 架构基础与云原生事件驱动的边界；
- 数据库 / 缓存 / 分布式一致性重叠；
- 质量属性、可靠性和安全属性的相邻边界；
- UML / 解释器 / 安全关键系统等容易把 capability 误当 topic 的题；
- source 自身存在多版本或答案冲突的案例。

## Copyright boundary

允许提交：taxonomy、capability、source metadata、mapping、review annotation、短小的自有识别摘要。

禁止提交：

- 第三方 PDF；
- 教材全文；
- 大量题目全文、选项、答案或解析；
- OCR 全文；
- 第三方仓库 clone。

运行验证：

```bash
python3 scripts/validate_taxonomy.py
```
