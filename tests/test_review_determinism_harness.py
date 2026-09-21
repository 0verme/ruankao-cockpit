"""P4.7 determinism harness self-tests and static wall-clock guard.

这里用 test double 验证 harness 本身：

* 一个合规的 reference stub 必须通过全部性质检查；
* 故意破坏顺序独立性 / 可重复性 / 输入不可变性 / as_of 回显 / UTC 等价性 /
  future-evidence 语义的 stub 必须被 harness 抓到。

reference stub 只是 test double，**不是** production mastery / scheduling policy，
也不得被复制到 `engine/`。
"""
from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from reviewkit import (
    DeterminismViolation,
    assert_replay_properties,
    parse_instant,
    replay_path_python_files,
    scan_for_wall_clock,
)

ROOT = Path(__file__).resolve().parents[1]


def review_events() -> list[dict]:
    """Synthetic review evidence facts; no mastery or scheduling semantics attached."""
    return [
        {
            "event_id": "evt-early-instant",
            "occurred_at": "2026-01-01T09:00:00+09:00",
            "review_item_id": "SYNTHETIC.ITEM.A",
            "fact": "correct",
        },
        {
            "event_id": "evt-late-instant",
            "occurred_at": "2026-01-01T04:00:00Z",
            "review_item_id": "SYNTHETIC.ITEM.A",
            "fact": "incorrect",
        },
        {
            "event_id": "evt-other-item",
            "occurred_at": "2026-01-02T10:00:00Z",
            "review_item_id": "SYNTHETIC.ITEM.B",
            "fact": "correct",
        },
    ]


class ReferenceStubReplay:
    """Order-independent, pure test double used only to exercise the harness."""

    def __init__(self, *, future_mode: str = "reject") -> None:
        self.future_mode = future_mode

    def __call__(self, events, *, as_of, timezone="UTC", **kwargs):
        as_of_instant = parse_instant(as_of)
        indexed = [
            (parse_instant(event["occurred_at"]), event["event_id"], event)
            for event in events
        ]
        future = [item for item in indexed if item[0] > as_of_instant]
        if future and self.future_mode == "reject":
            raise ValueError("future evidence rejected")
        visible = [item for item in indexed if item[0] <= as_of_instant]
        ordered = sorted(visible, key=lambda item: (item[0], item[1]))
        return {
            "as_of": as_of_instant.isoformat(),
            "timezone": timezone,
            "ordered_event_ids": [item[1] for item in ordered],
            "items": sorted({item[2]["review_item_id"] for item in ordered}),
        }


class OrderDependentStub(ReferenceStubReplay):
    def __call__(self, events, *, as_of, **kwargs):
        result = super().__call__(events, as_of=as_of, **kwargs)
        result["input_head"] = events[0]["event_id"] if events else None
        return result


class HiddenStateStub(ReferenceStubReplay):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.calls = 0

    def __call__(self, events, *, as_of, **kwargs):
        self.calls += 1
        result = super().__call__(events, as_of=as_of, **kwargs)
        result["call_index"] = self.calls
        return result


class MutatingStub(ReferenceStubReplay):
    def __call__(self, events, *, as_of, **kwargs):
        for event in events:
            event["seen"] = True
        return super().__call__(events, as_of=as_of, **kwargs)


class NoAsOfEchoStub(ReferenceStubReplay):
    def __call__(self, events, *, as_of, **kwargs):
        result = super().__call__(events, as_of=as_of, **kwargs)
        result.pop("as_of")
        return result


class StringSortedStub(ReferenceStubReplay):
    """Naive stub that orders by the raw timestamp string instead of the UTC instant."""

    def __call__(self, events, *, as_of, **kwargs):
        result = super().__call__(events, as_of=as_of, **kwargs)
        as_of_instant = parse_instant(as_of)
        visible = [event for event in events if parse_instant(event["occurred_at"]) <= as_of_instant]
        result["ordered_event_ids"] = [
            event["event_id"] for event in sorted(visible, key=lambda event: event["occurred_at"])
        ]
        return result


class FutureLeakingStub(ReferenceStubReplay):
    """Echoes as_of but counts future evidence anyway (exclude-mode leak)."""

    def __call__(self, events, *, as_of, timezone="UTC", **kwargs):
        as_of_instant = parse_instant(as_of)
        ordered = sorted(events, key=lambda event: (parse_instant(event["occurred_at"]), event["event_id"]))
        return {
            "as_of": as_of_instant.isoformat(),
            "timezone": timezone,
            "ordered_event_ids": [event["event_id"] for event in ordered],
        }


class DeterminismHarnessTests(unittest.TestCase):
    as_of = "2026-01-03T00:00:00Z"

    def test_reference_stub_satisfies_every_property(self) -> None:
        for mode in ("reject", "exclude"):
            with self.subTest(future_mode=mode):
                assert_replay_properties(
                    ReferenceStubReplay(future_mode=mode),
                    review_events(),
                    as_of=self.as_of,
                    future_evidence_mode=mode,
                    label=f"reference stub ({mode})",
                )

    def test_harness_accepts_equivalent_instant_representations(self) -> None:
        baseline = assert_replay_properties(
            ReferenceStubReplay(), review_events(), as_of="2026-01-03T08:00:00+08:00", label="instant variants"
        )
        self.assertEqual(baseline["items"], ["SYNTHETIC.ITEM.A", "SYNTHETIC.ITEM.B"])

    def assert_violation(self, stub, *, needle: str, mode: str = "reject") -> str:
        with self.assertRaises(DeterminismViolation) as context:
            assert_replay_properties(
                stub,
                review_events(),
                as_of=self.as_of,
                future_evidence_mode=mode,
                label="broken stub",
            )
        message = str(context.exception)
        self.assertIn(needle, message)
        return message

    def test_harness_rejects_order_dependent_replay(self) -> None:
        self.assert_violation(OrderDependentStub(), needle="input-order independence")

    def test_harness_rejects_hidden_state(self) -> None:
        self.assert_violation(HiddenStateStub(), needle="repeatability")

    def test_harness_rejects_input_mutation(self) -> None:
        self.assert_violation(MutatingStub(), needle="mutated its input")

    def test_harness_rejects_missing_as_of_echo(self) -> None:
        self.assert_violation(NoAsOfEchoStub(), needle="as_of echo missing")

    def test_harness_rejects_string_sorted_timestamps(self) -> None:
        message = self.assert_violation(StringSortedStub(), needle="UTC equivalence")
        self.assertNotIn("repeatability", message)

    def test_harness_checks_as_of_is_honoured(self) -> None:
        class IgnoresAsOfStub(ReferenceStubReplay):
            def __call__(self, events, *, as_of, **kwargs):
                return super().__call__(events, as_of="2999-01-01T00:00:00Z", **kwargs)

        self.assert_violation(IgnoresAsOfStub(), needle="as_of echo mismatch")

    def test_harness_exclude_mode_detects_future_leak(self) -> None:
        self.assert_violation(FutureLeakingStub(), needle="leaked", mode="exclude")

    def test_harness_reject_mode_detects_missing_rejection(self) -> None:
        self.assert_violation(FutureLeakingStub(), needle="was not rejected", mode="reject")


class WallClockGuardTests(unittest.TestCase):
    def test_existing_replay_path_is_scanned_and_clean(self) -> None:
        files = replay_path_python_files(ROOT)
        relative = {path.relative_to(ROOT).as_posix() for path in files}
        self.assertIn("engine/progress/replay.py", relative)
        self.assertIn("engine/progress/model.py", relative)
        self.assertEqual(scan_for_wall_clock(files), [])

    def test_scanner_covers_future_review_engine_and_flags_violations(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            review_replay = root / "engine/review/replay.py"
            review_replay.parent.mkdir(parents=True)
            review_replay.write_text(
                "from datetime import datetime\n\n\ndef replay(events, *, as_of):\n"
                "    return {'as_of': as_of, 'now': datetime." + "now()}\n",
                encoding="utf-8",
            )
            clean = root / "engine/progress/replay.py"
            clean.parent.mkdir(parents=True)
            clean.write_text("def replay(events, *, as_of):\n    return {'as_of': as_of}\n", encoding="utf-8")
            outside = root / "engine/notes/scratch.py"
            outside.parent.mkdir(parents=True)
            outside.write_text("from datetime import datetime\nNOW = datetime." + "now()\n", encoding="utf-8")

            files = replay_path_python_files(root)
            relative = [path.relative_to(root).as_posix() for path in files]
            self.assertEqual(relative, ["engine/progress/replay.py", "engine/review/replay.py"])

            violations = scan_for_wall_clock(files)
            self.assertEqual([path.name for path, _, _ in violations], ["replay.py"])
            self.assertEqual(violations[0][0].parent.name, "review")
            self.assertIn("now", violations[0][2])

    def test_scanner_detects_utcnow_and_time_time(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "engine/review/policy.py"
            path.parent.mkdir(parents=True)
            path.write_text(
                "from datetime import datetime\nimport time\nA = datetime.utc" + "now()\nB = time." + "time()\n",
                encoding="utf-8",
            )
            violations = scan_for_wall_clock([path])
            self.assertEqual(len(violations), 2)
            self.assertIn("utc", violations[0][2])
            self.assertIn("time.time", violations[1][2])

    def test_this_module_is_wall_clock_free(self) -> None:
        self.assertEqual(scan_for_wall_clock([Path(__file__)]), [])


if __name__ == "__main__":
    unittest.main()
