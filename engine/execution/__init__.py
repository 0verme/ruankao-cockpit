"""Minimal adapter from scheduled planner tasks to existing fact events."""

from .task_result import TaskResultError, record_task_result

__all__ = ["TaskResultError", "record_task_result"]
