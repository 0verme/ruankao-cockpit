"""Minimal adapter from scheduled planner tasks to existing fact events."""

from .task_result import (
    TaskResultError,
    build_topic_review_item_from_attempt,
    record_task_result,
)

__all__ = [
    "TaskResultError",
    "build_topic_review_item_from_attempt",
    "record_task_result",
]
