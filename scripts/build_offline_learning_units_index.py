#!/usr/bin/env python3
"""Build the static Markdown index and content-build report from Path + units."""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data/learning-paths/system-architect-checkin-v1.json"
UNITS = ROOT / "content/learning-units/system-architect-checkin"
INDEX = UNITS / "README.md"
REPORT = ROOT / "docs/learning-path/SYSTEM_ARCHITECT_CHECKIN_CONTENT_BUILD_REPORT.md"


def frontmatter_value(text: str, key: str) -> str:
    match = re.search(r"(?m)^" + re.escape(key) + r":\s*(.*?)\s*$", text[:text.find("\n---\n", 4)])
    if not match:
        raise ValueError(f"missing frontmatter field {key}")
    return match.group(1).strip().strip('"')


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, help="source ZIP; verifies archive and all prompt fingerprints")
    args = parser.parse_args()
    validator = ROOT / "scripts/validate_offline_learning_units.py"
    command = [sys.executable, str(validator)]
    if args.archive:
        command += ["--archive", str(args.archive)]
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    if result.returncode:
        sys.stderr.write(result.stdout + result.stderr)
        return result.returncode
    validation_output = result.stdout.strip()

    path = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if args.archive:
        validation_output = validation_output.replace(str(args.archive), path["source"]["archive_name"])
    learning = [item for item in path["items"] if item["mapping_status"] != "non_learning"]
    rest = [item for item in path["items"] if item["mapping_status"] == "non_learning"]
    mapping_counts = collections.Counter(x["mapping_status"] for x in learning)
    review_counts: collections.Counter[str] = collections.Counter()
    rows: list[str] = []
    for item in learning:
        filename = f"{item['item_id']}.md"
        text = (UNITS / filename).read_text(encoding="utf-8")
        title = frontmatter_value(text, "title")
        review = frontmatter_value(text, "review_status")
        review_counts[review] += 1
        topics = ", ".join(f"`{topic}`" for topic in item["topic_ids"]) or "—"
        safe_title = title.replace("|", "\\|")
        rows.append(
            f"| {item['order']:03d} | {item['source_date']} | [`{item['item_id']}`]({filename}) "
            f"| {safe_title} | {item['mapping_status'].upper()} | {item['mapping_confidence'] or '—'} | {topics} | {review} |"
        )

    index_lines = [
        "# 系统架构设计师打卡学习单元索引",
        "",
        "> 静态 Markdown authoring artifacts；不接入 Planner、Progress、Review 或运行时 AI。",
        "> 每个文件保留原始 `item_id` / `order`。休息记录不生成学习单元。",
        "",
        "## 来源与状态",
        "",
        f"- Learning Path：`{path['path_id']}` v{path['version']}（当前仍为 `{path['status']}`）。",
        f"- 来源归档：`{path['source']['archive_name']}`；SHA-256：`{path['source']['archive_sha256']}`。原始正文未作为归档副本加入仓库。",
        f"- 学习单元：{len(learning)}；休息/非学习项：{len(rest)}（" + ", ".join(f"`{x['item_id']}`" for x in rest) + ").",
        f"- Mapping：" + ", ".join(f"{k.upper()} {mapping_counts[k]}" for k in ("exact", "partial", "split", "merge", "unmapped")) + ".",
        f"- 内容缺证标记：`source_gap` {review_counts['source_gap']}；未标记已知缺口：{review_counts['unreviewed']}。所有文件仍为 `generation.status: draft`，生成/校验通过不等于人工内容审核通过。",
        "- `UNMAPPED` 项保持空 `topic_ids`；SPLIT/MERGE 不合并成 Topic 文件，文件仍按 Path Item 身份生成。",
        "- 依 Issue #50 范围，这些 Markdown 是离线 authoring artifacts，不是 runtime Learning Unit、Learning Payload 或 completion facts。",
        "- [Learning Unit v0.1 合同](../../../docs/learning-path/LEARNING_UNIT_V01.md)保持冻结；[#51 Pilot 报告](../../../docs/content/CONTENT_AUTHORING_PILOT_01.md)中的 `CONTENT_MODEL_GAP` 仍未解决。",
        "",
        "## 学习单元（按原始 order）",
        "",
        "| Order | 来源日期 | Item | 标题 | Mapping | Confidence | Topic IDs | Review marker |",
        "|---:|---|---|---|---|---|---|---|",
        *rows,
        "",
        "## 使用边界",
        "",
        "- 学习路径日期/order 是来源追踪与排列信息，不是学习完成事实或学习日程。",
        "- `source_gap` 表示来源未支持的知识部分已显式留缺，不表示已完成内容审校。",
        "- `content_version: offline-learning-unit/v0.1` 只标识这些静态 Markdown 文件格式；按 Issue #50，它们不是 runtime Learning Unit、Topic-scoped Learning Payload、Progress/Review evidence 或 completion facts。",
        "- Learning Unit v0.1 语义保持冻结；[#51 Pilot 报告](../../../docs/content/CONTENT_AUTHORING_PILOT_01.md)中的 `CONTENT_MODEL_GAP` 仍未解决。本批仅校准了静态 Markdown 模板，不声称解决 Unit-specific Payload / Topic Experience 选择。",
        "- Golden Set 仅做主题级索引，不推断本学习日细目的考试频率。",
        "- 参见 [`SYSTEM_ARCHITECT_CHECKIN_CONTENT_BUILD_REPORT.md`](../../../docs/learning-path/SYSTEM_ARCHITECT_CHECKIN_CONTENT_BUILD_REPORT.md)、[`SYSTEM_ARCHITECT_CHECKIN_MAPPING_AUDIT.md`](../../../docs/learning-path/SYSTEM_ARCHITECT_CHECKIN_MAPPING_AUDIT.md) 与 [`LEARNING_UNIT_V01.md`](../../../docs/learning-path/LEARNING_UNIT_V01.md)。",
        "",
    ]
    INDEX.write_text("\n".join(index_lines), encoding="utf-8")

    mapping_summary = "\n".join(f"| {status.upper()} | {mapping_counts[status]} |" for status in ("exact", "partial", "split", "merge", "unmapped"))
    review_summary = "\n".join(f"| `{status}` | {review_counts[status]} |" for status in ("source_gap", "unreviewed"))
    source_verified = "是：归档指纹、CRC 与 110 个 Prompt 区块 SHA-256 均通过。" if args.archive else "否：仅检查静态文件和 manifest 对齐；要核验归档与每条 Prompt 指纹，请传入 `--archive`。"
    report_lines = [
        "# 系统架构设计师打卡学习单元离线构建报告",
        "",
        f"> 构建产物状态：静态草稿；生成日期：{__import__('datetime').date.today().isoformat()}。",
        "",
        "## 摘要",
        "",
        f"- 来源 Learning Path：`{path['path_id']}` v{path['version']}，路径状态保持 `{path['status']}`。",
        f"- 输入归档：`{path['source']['archive_name']}`，SHA-256 `{path['source']['archive_sha256']}`，大小 {path['source']['archive_size_bytes']} bytes。",
        f"- 原始记录 112 项：{len(learning)} 个学习项 + {len(rest)} 个 NON_LEARNING 休息项；休息项未生成文件（" + ", ".join(f"`{x['item_id']}`" for x in rest) + ").",
        f"- 已生成 {len(learning)} 个 Markdown 文件，保留 `item_id`、Path `order`、来源日期/路径、mapping、confidence、topic_ids 和 Prompt 区块指纹。",
        f"- 归档来源完整性核验：{source_verified}",
        "",
        "## Mapping 统计",
        "",
        "| Status | Items |",
        "|---|---:|",
        mapping_summary,
        "",
        "以上分类从 Learning Path manifest 读取，仅记录来源映射关系；不推导 Planner 任务语义，也不改变 Taxonomy。",
        "",
        "## 来源缺口与审核状态",
        "",
        "| Frontmatter `review_status` | Items |",
        "|---|---:|",
        review_summary,
        "",
        "`source_gap` 是内容层的证据缺口标记。其余 `unreviewed` 只表示目前未记录已知缺口，不能理解为已完成审核。全部 110 个文件的 `generation.status` 都是 `draft`；没有任何一项因此获得内容批准。",
        "",
        "所有学习单元均保留软考关注边界：缺少章节级大纲/教材证据时不作覆盖断言；Golden Set 只作 Topic 级索引，不据此生成频率结论。",
        "",
        "## 校验与模板校准",
        "",
        "```text",
        validation_output,
        "```",
        "",
        "- 前 7 项完成的是 Issue #50 范围内的**静态 Markdown 模板校准**（PASS）：包含 MERGE、SPLIT、EXACT；缺证处保留 `SOURCE_GAP`，并检查 Prompt authoring 指令泄漏与无证据考试频率断言。",
        "- 该格式校准不推翻 PR #51 Pilot 的 `CONTENT_MODEL_GAP` 结论，也不代表 Topic-scoped Payload / Topic Experience 已能表达 sequential Learning Units 的差异化内容；本批文件不接入运行时。",
        "- 质量抽查：批量生成后定向复核 `checkin-065`、`073`–`075`、`110`、`112`，对照来源提纲检查主题边界、`SOURCE_GAP` 标记及 UNMAPPED/多 Topic 身份；这是抽样，不代替 110 项逐条人工事实审校。",
        "- 静态 validator 校验文件集合/数量、Learning Path 身份和顺序、来源路径/日期、mapping 与 topic_ids、offline-agent/draft 元数据、Prompt hash 格式、必需内容章节、Prompt 指令泄漏和 SOURCE_GAP 标记。带 `--archive` 时额外核对 ZIP 指纹、CRC 和每项 Prompt 区块 hash。",
        "- `UNMAPPED` 项不创建 Topic、不注入候选 ID；休息项身份仍保留在 manifest 中但没有对应 Markdown。",
        "",
        "## 边界与未完成事项",
        "",
        "- Learning Path 仍为 draft / MAPPING_REVIEW_REQUIRED；本次不修改该 mapping 审核结论。",
        "- 所有内容都是离线静态草稿，仍需人工事实校对、来源审阅与逐项内容审核；构建和静态校验通过不等于内容正确性批准。",
        "- 按 Issue #50 与 [Learning Unit v0.1 合同](LEARNING_UNIT_V01.md)，本批 Markdown 不是 runtime Learning Unit / Topic Payload / Progress / Review / completion fact；[PR #51 Pilot 报告](../content/CONTENT_AUTHORING_PILOT_01.md)记录的 `CONTENT_MODEL_GAP` 仍然有效。",
        "- 本次不改 Learning Payload runtime schema、Planner、Progress、Review、Taxonomy、UI 或运行时 AI 依赖；不把单元接入运行时学习流程。",
        "- 第三方教材、题库、讲义、PDF 或 Prompt 正文不随仓库发布；来源以路径和 SHA-256 指纹追踪，版权许可不由 ZIP 所有权推定。",
        "- 索引：[`content/learning-units/system-architect-checkin/README.md`](../../content/learning-units/system-architect-checkin/README.md)。",
        "",
    ]
    REPORT.write_text("\n".join(report_lines), encoding="utf-8")
    print(f"WROTE {INDEX.relative_to(ROOT)} ({len(learning)} rows)")
    print(f"WROTE {REPORT.relative_to(ROOT)}")
    sys.stdout.write(validation_output + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
