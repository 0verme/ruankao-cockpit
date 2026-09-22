# Review / Mastery 测试资产（Phase 4）

本目录属于 **Phase 4：Mastery / Review Scheduling v0.1** 的验证资产，与
`data/progress/`（Phase 3 Progress Model v0.1）保持独立边界。

```text
data/progress/   Progress Event v0.1 / ProgressState v0.1 / deterministic replay
data/review/     Review evidence / Mastery state / Review scheduling 的 fixtures
```

分开的原因：review 域有独立的 policy version、`as_of` 语义和 fixture schema；
混入 progress fixture 会让 `progress-model/v0.1` 的边界变得含糊。

## 当前状态

```text
TEST_DESIGN_READY
WAITING_FOR_FIXTURE_MATRIX_FINALIZATION（P4.6 / P4.7）
```

本目录当前**不包含**任何 fixture 文件，因为 P4.6/P4.7 的 policy-dependent
expected、edge-case matrix 与 synthetic asset 仍未收口。P4.1～P4.5 的
`review_item_id`、evidence contract、状态名、interval ladder、failure reset
和 replay schema 已由对应 contract / engine 实现；fixture 不得再定义一套规则。

## 文件

| 文件 | 作用 |
| --- | --- |
| `fixture-plan.json` | 机器可读测试 / fixture 设计 manifest，含 policy symbol 注册表 |
| `fixture-schema.draft.json` | draft fixture contract；`frozen: false`，freeze 后升级版本 |
| `fixtures/` | fixture matrix freeze 后按 manifest 填充 synthetic fixture |

## 关联文档与骨架

* [`docs/PHASE4_TEST_MATRIX.md`](../../docs/PHASE4_TEST_MATRIX.md)：完整测试矩阵与 contract gap 清单
* [`tests/reviewkit.py`](../../tests/reviewkit.py)：fixture loader + determinism 性质 harness + 静态守卫
* [`tests/test_review_fixture_plan.py`](../../tests/test_review_fixture_plan.py)：manifest / draft schema 一致性
* [`tests/test_review_determinism_harness.py`](../../tests/test_review_determinism_harness.py)：harness 自测与 wall-clock 扫描
* [`tests/test_progress_v01_regression.py`](../../tests/test_progress_v01_regression.py)：Phase 3 语义冻结基线
* [`scripts/validate_review.py`](../../scripts/validate_review.py)：review 域 validator（fixture matrix 未收口时输出 PENDING）

## 运行

```bash
python3 scripts/validate_review.py
python3 -m unittest discover -s tests -v
```

`validate_review.py` 输出 `PENDING_REVIEW_FIXTURE_MATRIX` 是当前预期结果，不代表 Phase 4 已完成。
