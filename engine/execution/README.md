# Task Result Adapter (MVP)

`record_task_result(planner_output, task_id, result)` only accepts a task scheduled in `days[0].tasks`. It does not mutate the plan and does not persist task state.

Supported paths:

- `new_learning` → topic-matched, caller-supplied `comprehensive_attempt` → Progress Event.
- `review/topic/<topic_id>` → matching `comprehensive_attempt` + explicit Review Context Event (`attempt_context: review`) → Progress and Review Events.

Event identities and the actual `correct` fact come from the caller. Full event/catalog validation, duplicate rejection, Review Evidence, success/failure, and scheduling remain owned by existing replay layers. Completion clicks and planned minutes are not facts. Study sessions, question/case-capability review, and new-learning Review Item registration are out of scope. In particular, new-learning registration needs a genuine source reference; this adapter does not invent one.
