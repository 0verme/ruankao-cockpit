# Minimal Today Planner MVP

`plan_today(planner_input, as_of)` in `replay.py` returns the existing `PlannerOutput` contract. Only `days[0]` is planned; required `days[1:7]` are empty structural placeholders and do not implement Rolling 7-Day selection.

## MVP rules

- **Review source:** consume only `MasteryReviewState` items already marked `overdue` or `due`; never recompute mastery or due dates.
- **Review priority:** overdue → due today → new learning. Within each review class, sort by `next_due_at`, then canonical `review_item_id`.
- **New-learning source:** taxonomy L3 topic IDs with no positive Progress topic attempts and no supported topic Review evidence/schedule. Incorrect attempts still count as evidence. Select one topic by ascending canonical ID; do not infer learning state from accuracy or use the DRAFT curriculum.
- **Fixed MVP durations:** `MVP_REVIEW_MINUTES = 15`, `MVP_NEW_LEARNING_MINUTES = 25`.
- **Capacity:** use `daily_available_minutes` on a configured study day; otherwise capacity is zero. Allocate whole tasks in priority order, never exceed capacity, and expose unallocated valid demand in `unmet_demand`.
- **Identity and time:** policy is `planner-policy/minimal-today/v0.1`; task, demand and trace IDs are deterministic semantic hashes. Caller-provided `as_of` must match the snapshot. No wall clock, randomness, implicit timezone or AI ranking is used.

This is a narrow implementation policy for Product Validation Slice #16, not a complete P5.4/P5.5 freeze. `exam_date` is an important future input for sprint strategy, but User Configuration v0.1 does not include it and this MVP does not change policy based on days remaining until the exam.

## Example: 60 minutes

```text
capacity: 60 min
planned: 55 min
remaining: 5 min

1. Review review/topic/DATA.CACHE.CACHE_FAILURE      15 min  overdue
2. Review review/topic/QUALITY.ATTRIBUTES.PERFORMANCE 15 min  due_today
3. New learning ARCH.CLOUD_NATIVE.CONTAINERS_SERVERLESS 25 min  next_unlearned_topic
```

The example is built from synthetic Progress / Review replays in `tests/planner_replay_fixtures.py`; no third-party question content is bundled.
