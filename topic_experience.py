"""Frontend-independent Topic Experience read model.

The read model is derived from canonical Taxonomy, the existing validated
Learning Payload, and deterministic Progress/Review projections. It contains
no user-write behavior and never treats reading a Topic as a learning fact.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence


class TopicExperienceError(ValueError):
    """The existing Topic/read-model inputs cannot form a safe experience."""


@dataclass(frozen=True)
class TopicBreadcrumb:
    topic_id: str
    name: str


@dataclass(frozen=True)
class TopicExperience:
    topic_id: str
    topic_name: str
    taxonomy_version: str
    breadcrumb: tuple[TopicBreadcrumb, ...]
    learning_payload: Mapping[str, Any] | None
    progress_attempt_count: int
    progress_accuracy: float | None
    review_mastery_state: str | None
    review_status: str | None
    review_next_due_local_date: str | None
    review_policy_version: str | None
    verification_sources: tuple[Mapping[str, Any], ...]

    @property
    def has_learning_payload(self) -> bool:
        return self.learning_payload is not None

    @property
    def learning_payload_version(self) -> str | None:
        if self.learning_payload is None:
            return None
        version = self.learning_payload.get("version")
        return version if isinstance(version, str) else None


def _taxonomy_breadcrumb(
    topic_id: str,
    taxonomy: Mapping[str, Any],
) -> tuple[str, tuple[TopicBreadcrumb, ...]]:
    nodes = taxonomy.get("nodes")
    if not isinstance(nodes, list):
        raise TopicExperienceError("Taxonomy nodes are unavailable")
    nodes_by_id = {
        node["id"]: node
        for node in nodes
        if isinstance(node, Mapping) and isinstance(node.get("id"), str)
    }
    node = nodes_by_id.get(topic_id)
    if not isinstance(node, Mapping) or node.get("level") != 3 or node.get("status") != "active":
        raise TopicExperienceError(f"{topic_id!r} is not an active L3 Knowledge Topic")

    chain: list[TopicBreadcrumb] = []
    visited: set[str] = set()
    current: Mapping[str, Any] = node
    while True:
        current_id = current.get("id")
        current_name = current.get("name")
        if (
            not isinstance(current_id, str)
            or current_id in visited
            or not isinstance(current_name, str)
            or not current_name.strip()
        ):
            raise TopicExperienceError(f"Taxonomy has an invalid parent chain for {topic_id!r}")
        visited.add(current_id)
        chain.append(TopicBreadcrumb(current_id, current_name))
        parent_id = current.get("parent_id")
        if parent_id is None:
            break
        parent = nodes_by_id.get(parent_id) if isinstance(parent_id, str) else None
        if not isinstance(parent, Mapping):
            raise TopicExperienceError(f"Taxonomy has an invalid parent chain for {topic_id!r}")
        current = parent

    chain.reverse()
    version = taxonomy.get("taxonomy_version")
    if not isinstance(version, str) or not version:
        raise TopicExperienceError("Taxonomy version is unavailable")
    return node["name"], tuple(chain)


def _topic_progress(topic_id: str, progress_state: Mapping[str, Any]) -> tuple[int, float | None]:
    topics = progress_state.get("topics")
    metric = topics.get(topic_id) if isinstance(topics, Mapping) else None
    if not isinstance(metric, Mapping):
        raise TopicExperienceError(f"Progress projection has no Topic metric for {topic_id!r}")
    attempt_count = metric.get("attempt_count")
    accuracy = metric.get("accuracy")
    if isinstance(attempt_count, bool) or not isinstance(attempt_count, int) or attempt_count < 0:
        raise TopicExperienceError(f"Progress projection has an invalid attempt count for {topic_id!r}")
    if accuracy is not None and (
        isinstance(accuracy, bool)
        or not isinstance(accuracy, (float, int))
        or not 0 <= accuracy <= 1
    ):
        raise TopicExperienceError(f"Progress projection has invalid accuracy for {topic_id!r}")
    return attempt_count, float(accuracy) if accuracy is not None else None


def _topic_review(
    topic_id: str,
    review_state: Mapping[str, Any],
) -> tuple[str | None, str | None, str | None, str | None]:
    items = review_state.get("items")
    if not isinstance(items, Mapping):
        raise TopicExperienceError("Review projection items are unavailable")
    matches = []
    for item in items.values():
        canonical_ref = item.get("canonical_ref") if isinstance(item, Mapping) else None
        if isinstance(canonical_ref, Mapping) and canonical_ref.get("topic_id") == topic_id:
            matches.append(item)
    if len(matches) > 1:
        raise TopicExperienceError(f"Review projection contains multiple Topic states for {topic_id!r}")
    if not matches:
        return None, None, None, None

    item = matches[0]
    mastery_state = item.get("mastery_state")
    review_status = item.get("review_status")
    due_date = item.get("next_due_local_date")
    policy_version = review_state.get("review_policy_version")
    if not isinstance(mastery_state, str) or not isinstance(review_status, str):
        raise TopicExperienceError(f"Review projection has an invalid Topic state for {topic_id!r}")
    if due_date is not None and not isinstance(due_date, str):
        raise TopicExperienceError(f"Review projection has an invalid due date for {topic_id!r}")
    if not isinstance(policy_version, str):
        raise TopicExperienceError("Review policy version is unavailable")
    return mastery_state, review_status, due_date, policy_version


def build_topic_experience(
    topic_id: str,
    *,
    taxonomy: Mapping[str, Any],
    progress_state: Mapping[str, Any],
    review_state: Mapping[str, Any],
    learning_payload: Mapping[str, Any] | None,
    verification_sources: Sequence[Mapping[str, Any]] = (),
) -> TopicExperience:
    """Compose a reusable Topic read model from already validated facts."""
    topic_name, breadcrumb = _taxonomy_breadcrumb(topic_id, taxonomy)
    payload = learning_payload
    if payload is not None and payload.get("topic_id") != topic_id:
        raise TopicExperienceError("Learning Payload does not match the requested Topic")
    attempt_count, accuracy = _topic_progress(topic_id, progress_state)
    mastery_state, review_status, due_date, policy_version = _topic_review(topic_id, review_state)
    if any(not isinstance(source, Mapping) for source in verification_sources):
        raise TopicExperienceError("Indexed verification references are malformed")

    return TopicExperience(
        topic_id=topic_id,
        topic_name=topic_name,
        taxonomy_version=taxonomy["taxonomy_version"],
        breadcrumb=breadcrumb,
        learning_payload=payload,
        progress_attempt_count=attempt_count,
        progress_accuracy=accuracy,
        review_mastery_state=mastery_state,
        review_status=review_status,
        review_next_due_local_date=due_date,
        review_policy_version=policy_version,
        verification_sources=tuple(verification_sources),
    )


__all__ = [
    "TopicBreadcrumb",
    "TopicExperience",
    "TopicExperienceError",
    "build_topic_experience",
]
