#!/usr/bin/env python3
"""Validate Review / Mastery scaffolding and report replay capability honestly.

当前职责：

1. 校验 `data/review/fixture-plan.json` 与 `fixture-schema.draft.json` 自洽；
2. 校验盘上 fixture 与 planned / ready 状态一致；
3. 识别 P4.5 replay 与 `MasteryReviewState` schema 是否存在；
4. 只有正式 ready fixture 到位后才执行 fixture replay / expected 比对。

本脚本不会打印 `PASS Phase 4`：PENDING 只表示 fixture / edge-case / validation
收口仍未完成，不代表 Phase 4 完成。
"""
from __future__ import annotations

import argparse
from pathlib import Path
import sys
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "tests") not in sys.path:
    sys.path.insert(0, str(ROOT / "tests"))

import reviewkit  # noqa: E402  (tests/ 下的共享测试工具)

PENDING_STATUS = "PENDING_REVIEW_FIXTURE_MATRIX"
REPLAY_PENDING_STATUS = "PENDING_REPLAY_IMPLEMENTATION"
TEST_DESIGN_STATUS = "TEST_DESIGN_READY"


def load_review_replay(root: Path) -> Callable[..., Any] | None:
    """Load the P4.5 replay entry point when the implementation is present."""
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    try:
        from engine.review.replay import replay as review_replay  # type: ignore[import-not-found]
    except ImportError:
        return None
    return review_replay


def verify_fixture(entry: dict[str, Any], fixture_dir: Path, replay_fn: Callable[..., Any] | None) -> str:
    fixture = reviewkit.load_review_fixture(fixture_dir / entry["file"])
    if replay_fn is None:
        return "shape-only"

    as_of = fixture["as_of"]
    timezone_name = fixture["timezone"]
    events = fixture.get("events", [])

    if "expected_error" in fixture:
        # 拒绝样本：只验证“必须失败且 category 稳定”，不跑确定性性质检查。
        try:
            replay_fn(events, as_of=as_of, timezone=timezone_name)
        except Exception as exc:  # noqa: BLE001 - category naming is policy-dependent
            category = getattr(exc, "category", None)
            if category is None:
                raise reviewkit.FixtureContractError(
                    f"{entry['fixture_id']}: replay raised {exc.__class__.__name__} without a stable category; "
                    "error categories must freeze before expected_error can be verified"
                ) from exc
            if category != fixture["expected_error"]:
                raise reviewkit.FixtureContractError(
                    f"{entry['fixture_id']}: expected error {fixture['expected_error']!r}, got {category!r}"
                ) from exc
            return "expected-error-matched"
        raise reviewkit.FixtureContractError(
            f"{entry['fixture_id']}: expected_error {fixture['expected_error']!r} but replay succeeded"
        )

    result = reviewkit.assert_replay_properties(
        replay_fn,
        events,
        as_of=as_of,
        timezone_name=timezone_name,
        label=entry["fixture_id"],
    )
    if "expected" in fixture:
        expected = reviewkit.canonical_json(fixture["expected"])
        actual = reviewkit.canonical_json(result)
        if expected != actual:
            raise reviewkit.FixtureContractError(f"{entry['fixture_id']}: expected mismatch")
        return "expected-matched"
    return "replay-only"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    root = args.root.resolve()

    try:
        plan = reviewkit.load_fixture_plan(root)
        draft = reviewkit.load_fixture_schema_draft(root)
        errors = reviewkit.validate_fixture_plan(plan, root)
        if errors:
            for error in errors:
                print(f"FAIL: {error}", file=sys.stderr)
            return 1
        if draft.get("status") != "draft" or draft.get("frozen") is not False:
            print("FAIL: fixture schema draft must stay draft until fixture matrix freeze", file=sys.stderr)
            return 1

        state_schema = root / "data/review/mastery-review-state.schema.json"
        if not state_schema.is_file():
            print(f"FAIL: missing MasteryReviewState schema {state_schema}", file=sys.stderr)
            return 1
        state_schema_doc = reviewkit.load_json(state_schema)
        if (
            state_schema_doc.get("title") != "MasteryReviewState v0.1"
            or state_schema_doc.get("properties", {}).get("schema_version", {}).get("const")
            != "mastery-review-state/v0.1"
        ):
            print(f"FAIL: invalid MasteryReviewState schema {state_schema}", file=sys.stderr)
            return 1
        design_doc = root / plan["design_doc"]
        if not design_doc.is_file():
            print(f"FAIL: design doc {design_doc} is missing", file=sys.stderr)
            return 1
        missing_refs = reviewkit.cross_check_matrix_refs(plan, design_doc.read_text(encoding="utf-8"))
        if missing_refs:
            for item in missing_refs:
                print(f"FAIL: {item}", file=sys.stderr)
            return 1

        entries = plan["fixtures"]
        fixture_dir = root / plan["fixture_root"]
        shipped = sorted(fixture_dir.glob("*.json"))
        ready = [entry for entry in entries if entry.get("status") == "ready"]
        replay_fn = load_review_replay(root)

        print(f"PASS review test scaffolding consistency: {len(entries)} planned entries")
        print(f"  implementation mix: {_mix(entries)}")
        print(f"  contract-independent: {sum(1 for e in entries if e['contract_independence'] == 'contract_independent')}"
              f" / policy-dependent: {sum(1 for e in entries if e['contract_independence'] == 'policy_dependent')}")
        print(f"  policy symbols registered: {len(plan['policy_symbols'])}"
              f" (unfrozen: {sum(1 for s in plan['policy_symbols'].values() if s['status'] == 'unfrozen')})")
        print(f"  fixtures on disk: {len(shipped)} (ready in plan: {len(ready)})")
        print(f"  replay capability: {'available' if replay_fn is not None else 'missing'}")
        print("  MasteryReviewState schema: available")

        outcomes: dict[str, int] = {}
        for entry in ready:
            try:
                outcome = verify_fixture(entry, fixture_dir, replay_fn)
            except (reviewkit.FixtureContractError, reviewkit.DeterminismViolation) as exc:
                print(f"FAIL: {entry['fixture_id']}: {exc}", file=sys.stderr)
                return 1
            outcomes[outcome] = outcomes.get(outcome, 0) + 1
        for outcome, count in sorted(outcomes.items()):
            print(f"  verified {outcome}: {count}")

        if replay_fn is None:
            print(f"{REPLAY_PENDING_STATUS}: engine.review replay is not available yet")
            return 0
        if not ready:
            print(f"{PENDING_STATUS}: replay exists; P4.6/P4.7 ready fixtures are not complete")
            return 0
        print("PASS ready review fixtures replayed deterministically")
        return 0
    except reviewkit.FixtureContractError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


def _mix(entries: list[dict[str, Any]]) -> str:
    counts: dict[str, int] = {}
    for entry in entries:
        counts[entry["implementation"]] = counts.get(entry["implementation"], 0) + 1
    return ", ".join(f"{key}={value}" for key, value in sorted(counts.items()))


if __name__ == "__main__":
    raise SystemExit(main())
