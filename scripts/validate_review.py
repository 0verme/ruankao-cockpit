#!/usr/bin/env python3
"""Validate and replay the frozen P4.6/P4.7 Review fixture matrix.

P4.8 documentation sync and P4.9 Gate report are separate deliverables. This
validator reports fixture-matrix status only and never judges the full Phase 4 Gate.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import sys
from typing import Any, Callable, Mapping

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "tests") not in sys.path:
    sys.path.insert(0, str(ROOT / "tests"))

import reviewkit  # noqa: E402

FIXTURE_PASS_STATUS = "REVIEW_FIXTURE_MATRIX_PASS"


def load_review_replay(root: Path) -> Callable[..., Any] | None:
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    try:
        from engine.review.replay import replay as review_replay  # type: ignore[import-not-found]
    except ImportError:
        return None
    return review_replay


def _replay_case(
    replay_fn: Callable[..., Any],
    input_data: Mapping[str, Any],
    fixture: Mapping[str, Any],
    *,
    as_of: Any,
    timezone_name: str,
    taxonomy: Mapping[str, Any],
    capabilities: Mapping[str, Any],
) -> Any:
    policies = fixture["policies"]
    return replay_fn(
        input_data["progress_events"],
        input_data["review_events"],
        input_data["items"],
        taxonomy,
        capabilities,
        as_of=as_of,
        timezone=timezone_name,
        mastery_policy=policies["mastery"],
        review_policy=policies["review"],
    )


def verify_fixture(
    entry: Mapping[str, Any],
    fixture_dir: Path,
    replay_fn: Callable[..., Any],
    *,
    root: Path,
    fixture_schema: Mapping[str, Any],
    state_schema: Mapping[str, Any],
    taxonomy: Mapping[str, Any],
    capabilities: Mapping[str, Any],
) -> dict[str, int]:
    path = fixture_dir / entry["file"]
    fixture = reviewkit.load_review_fixture(path, schema=fixture_schema)
    if fixture["fixture_id"] != entry["fixture_id"]:
        raise reviewkit.FixtureContractError(f"{path.name}: fixture id does not match manifest")
    if fixture.get("policy_symbols", []) != entry.get("policy_symbols", []):
        raise reviewkit.FixtureContractError(f"{path.name}: policy_symbols differ from the frozen manifest")
    if fixture.get("contract_refs") != entry.get("contract_refs"):
        raise reviewkit.FixtureContractError(f"{path.name}: contract_refs differ from the frozen manifest")
    for ref in fixture["contract_refs"]:
        if not (root / ref.split("#", 1)[0]).is_file():
            raise reviewkit.FixtureContractError(f"{path.name}: missing contract reference {ref!r}")

    outcomes = {"expected-matched": 0, "expected-error-matched": 0}
    for case in reviewkit.fixture_cases(fixture):
        label = f"{entry['fixture_id']}[{case['case_id']}]"
        try:
            state = _replay_case(
                replay_fn,
                case["input"],
                fixture,
                as_of=case["as_of"],
                timezone_name=case["timezone"],
                taxonomy=taxonomy,
                capabilities=capabilities,
            )
        except Exception as exc:  # noqa: BLE001 - category is the frozen rejection contract
            category = getattr(exc, "category", None)
            if case["expected_error"] is None:
                raise reviewkit.FixtureContractError(
                    f"{label}: replay raised {exc.__class__.__name__} [{category}]: {exc}"
                ) from exc
            if category != case["expected_error"]:
                raise reviewkit.FixtureContractError(
                    f"{label}: expected error {case['expected_error']!r}, got {category!r}"
                ) from exc
            outcomes["expected-error-matched"] += 1
            continue

        if case["expected_error"] is not None:
            raise reviewkit.FixtureContractError(
                f"{label}: expected rejection {case['expected_error']!r}, but replay succeeded"
            )
        reviewkit.validate_mastery_review_state(
            state,
            as_of=case["as_of"],
            timezone_name=case["timezone"],
            state_schema=state_schema,
        )
        reviewkit.assert_expected_projection(state, case["expected"], label)
        reviewkit.assert_review_replay_properties(
            replay_fn,
            case["input"],
            as_of=case["as_of"],
            timezone_name=case["timezone"],
            policies=fixture["policies"],
            taxonomy=taxonomy,
            capabilities=capabilities,
            label=label,
        )
        outcomes["expected-matched"] += 1
    return outcomes


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    root = args.root.resolve()

    try:
        plan = reviewkit.load_fixture_plan(root)
        errors = reviewkit.validate_fixture_plan(plan, root)
        if errors:
            for error in errors:
                print(f"FAIL: {error}", file=sys.stderr)
            return 1

        fixture_schema_path = root / "data/review/fixture-schema.v0.1.json"
        fixture_schema = reviewkit.load_json(fixture_schema_path)
        if (
            fixture_schema.get("title") != "Mastery / Review Fixture v0.1"
            or fixture_schema.get("schema_version") != reviewkit.FIXTURE_SCHEMA_VERSION
            or fixture_schema.get("contract") != "mastery-review-fixture"
            or fixture_schema.get("status") != "FROZEN"
            or fixture_schema.get("frozen") is not True
            or fixture_schema.get("owner") != "P4.6"
            or fixture_schema.get("properties", {}).get("schema_version", {}).get("const")
            != reviewkit.FIXTURE_SCHEMA_VERSION
        ):
            raise reviewkit.FixtureContractError("formal mastery-review-fixture/v0.1 schema metadata is missing or inconsistent")

        state_schema_path = root / "data/review/mastery-review-state.schema.json"
        state_schema = reviewkit.load_json(state_schema_path)
        if (
            state_schema.get("title") != "MasteryReviewState v0.1"
            or state_schema.get("properties", {}).get("schema_version", {}).get("const")
            != "mastery-review-state/v0.1"
        ):
            raise reviewkit.FixtureContractError("MasteryReviewState v0.1 schema is missing or inconsistent")

        design_doc = root / plan["design_doc"]
        if not design_doc.is_file():
            raise reviewkit.FixtureContractError(f"design doc {design_doc} is missing")
        missing_refs = reviewkit.cross_check_matrix_refs(plan, design_doc.read_text(encoding="utf-8"))
        if missing_refs:
            raise reviewkit.FixtureContractError("undocumented matrix refs: " + "; ".join(missing_refs))

        replay_fn = load_review_replay(root)
        if replay_fn is None:
            raise reviewkit.FixtureContractError("engine.review.replay is required for a frozen fixture matrix")
        taxonomy = reviewkit.load_json(root / "taxonomy/taxonomy.json")
        capabilities = reviewkit.load_json(root / "taxonomy/capabilities.json")
        fixture_dir = root / plan["fixture_root"]
        ready = [entry for entry in plan["fixtures"] if entry.get("implementation") == "fixture"]

        totals = {"expected-matched": 0, "expected-error-matched": 0}
        for entry in ready:
            try:
                outcomes = verify_fixture(
                    entry,
                    fixture_dir,
                    replay_fn,
                    root=root,
                    fixture_schema=fixture_schema,
                    state_schema=state_schema,
                    taxonomy=taxonomy,
                    capabilities=capabilities,
                )
            except (reviewkit.FixtureContractError, reviewkit.DeterminismViolation) as exc:
                print(f"FAIL: {exc}", file=sys.stderr)
                return 1
            for key, count in outcomes.items():
                totals[key] += count

        print("PASS frozen Review fixture schema and manifest")
        print(f"  policy symbols frozen: {len(plan['policy_symbols'])}")
        print(f"  fixtures replayed: {len(ready)}")
        print(f"  expected states matched: {totals['expected-matched']}")
        print(f"  expected rejection categories matched: {totals['expected-error-matched']}")
        print("PASS output schema, version metadata, as_of/timezone, evidence trace and aggregate invariants")
        print("PASS repeatability, input-order independence, same-instant offsets and future-evidence rejection")
        print(f"{FIXTURE_PASS_STATUS}: P4.6/P4.7 fixture matrix only; P4.8/P4.9 status is recorded in docs/PHASE4_VALIDATION_REPORT.md")
        return 0
    except reviewkit.FixtureContractError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
