# Task Result Adapter (MVP)

`record_task_result(planner_output, task_id, result, ...)` only accepts a task scheduled in `days[0].tasks`. It does not mutate the plan or persist task state. Both paths require an explicit attempt and `review_context_event_id` supplied by the caller.

Supported paths:

- `new_learning/topic` → matching `comprehensive_attempt` → Progress Event, `review/topic/<topic_id>` Review Item, and `initial_learning` Review Context.
- `review/topic/<topic_id>` → matching `comprehensive_attempt` + `review` Review Context; no new Review Item.

For new learning, callers also provide the current taxonomy, capabilities, and Review Item catalog. The adapter validates them, fails closed if the topic item already exists, and derives the item `source_reference` from that attempt's real `question` provenance (`source_id`, `source_commit`, `source_path`, and available question identifiers). Topic identity remains `review/topic/<topic_id>`; source question identity is provenance only.

Correct and incorrect attempts both create the same Review registration facts. Existing Progress / Review replay generates Review Evidence and applies the frozen outcome/scheduling policy. The adapter does not infer success, failure, mastery, interval, or due date. Skipped tasks produce no events or items. Completion clicks and planned minutes are not facts. Study sessions and question/case-capability execution remain out of scope.
