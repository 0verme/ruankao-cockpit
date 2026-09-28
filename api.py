"""Minimal FastAPI transport for the existing local Cockpit application service."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from fastapi import Depends, FastAPI, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, StrictBool

from cockpit_service import (
    PROJECT_ROOT,
    TodaySnapshot,
    get_today,
    get_today_topic_display_metadata,
    get_topic_experience,
    initialize_cockpit,
    record_browser_attempt,
)
from topic_experience import TopicExperience


def _configured_local_dir() -> Path:
    configured = os.environ.get("COCKPIT_LOCAL_DIR")
    if configured is None:
        return PROJECT_ROOT / ".local"
    if not configured.strip():
        raise RuntimeError("COCKPIT_LOCAL_DIR cannot be empty")
    path = Path(configured).expanduser()
    if not path.is_absolute():
        raise RuntimeError("COCKPIT_LOCAL_DIR must be an absolute path")
    return path.resolve()


# Resolve once at process startup so request cwd changes cannot select another .local.
LOCAL_DATA_DIR = _configured_local_dir()


def get_local_dir() -> Path:
    """FastAPI dependency, overridable by isolated transport tests."""
    return LOCAL_DATA_DIR


class StrictRequestModel(BaseModel):
    class Config:
        extra = "forbid"


class QuestionReferenceRequest(StrictRequestModel):
    source_id: str = Field(min_length=1)
    source_commit: str = Field(min_length=1)
    source_path: str = Field(min_length=1)
    source_question_id: str = Field(min_length=1)
    golden_set_record_id: str | None = None


class AttemptRequest(StrictRequestModel):
    task_id: str = Field(min_length=1)
    occurred_at: str = Field(min_length=1)
    question: QuestionReferenceRequest
    correct: StrictBool
    error_cause: str | None = None


app = FastAPI(
    title="ruankao-cockpit local API",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

_CONFLICT_CATEGORIES = {
    "not_initialized",
    "incomplete_local_data",
    "duplicate_event",
    "task_not_scheduled",
    "pending_transaction",
    "conflicting_transaction",
}
_NOT_FOUND_CATEGORIES = {"unknown_topic", "unknown_task"}
_SERVER_ERROR_CATEGORIES = {
    "invalid_local_data",
    "invalid_catalog",
    "invalid_source_catalog",
    "invalid_learning_catalog",
    "invalid_topic_experience",
    "invalid_planner_output",
    "storage_error",
    "invalid_configuration",
}


def _error_response(category: str, message: str, status_code: int) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"error": {"category": category, "message": message}},
    )


def _service_error_response(exc: BaseException) -> JSONResponse:
    category = getattr(exc, "category", None)
    if not isinstance(category, str) or not category:
        category = "domain_error"
    if category in _SERVER_ERROR_CATEGORIES:
        status_code = 500
    elif category in _NOT_FOUND_CATEGORIES:
        status_code = 404
    elif category in _CONFLICT_CATEGORIES:
        status_code = 409
    else:
        status_code = 422
    return _error_response(category, str(exc) or category, status_code)


@app.exception_handler(RequestValidationError)
async def request_validation_error_handler(
    _request: Request,
    _exc: RequestValidationError,
) -> JSONResponse:
    return _error_response(
        "invalid_request",
        "Request does not match the endpoint contract.",
        422,
    )


@app.exception_handler(ValueError)
async def domain_value_error_handler(_request: Request, exc: ValueError) -> JSONResponse:
    return _service_error_response(exc)


@app.exception_handler(OSError)
async def storage_error_handler(_request: Request, exc: OSError) -> JSONResponse:
    return _error_response("storage_error", str(exc) or "Local storage operation failed.", 500)


def _topic_experience_response(experience: TopicExperience) -> dict[str, Any]:
    payload = experience.learning_payload
    return {
        "topic": {
            "topic_id": experience.topic_id,
            "name": experience.topic_name,
            "taxonomy_version": experience.taxonomy_version,
            "breadcrumb": [
                {"topic_id": crumb.topic_id, "name": crumb.name}
                for crumb in experience.breadcrumb
            ],
        },
        "learning_payload_status": "available" if experience.has_learning_payload else "unavailable",
        "learning_payload_version": experience.learning_payload_version,
        "learning_payload": payload,
        "progress": {
            "attempt_count": experience.progress_attempt_count,
            "accuracy": experience.progress_accuracy,
        },
        "review": {
            "mastery_state": experience.review_mastery_state,
            "status": experience.review_status,
            "next_due_local_date": experience.review_next_due_local_date,
            "policy_version": experience.review_policy_version,
        },
        "verification_sources": list(experience.verification_sources),
    }


def _snapshot_read_model(snapshot: TodaySnapshot) -> dict[str, Any]:
    return {
        "planner": snapshot.planner_output,
        "progress": snapshot.progress_state,
        "review": {
            "state": snapshot.review_state,
            "items": snapshot.review_items,
        },
    }


@app.post("/api/init")
def post_init(local_dir: Path = Depends(get_local_dir)) -> dict[str, str]:
    created = initialize_cockpit(local_dir)
    return {"state": "created" if created else "already_exists"}


@app.get("/api/today")
def get_api_today(
    as_of: str | None = Query(default=None, min_length=1),
    local_dir: Path = Depends(get_local_dir),
) -> dict[str, Any]:
    snapshot = get_today(as_of=as_of, local_dir=local_dir)
    return {
        **_snapshot_read_model(snapshot),
        "task_topics": get_today_topic_display_metadata(snapshot),
    }


@app.get("/api/topics/{topic_id}")
def get_api_topic(
    topic_id: str,
    as_of: str | None = Query(default=None, min_length=1),
    local_dir: Path = Depends(get_local_dir),
) -> dict[str, Any]:
    snapshot = get_today(as_of=as_of, local_dir=local_dir)
    experience = get_topic_experience(topic_id, snapshot)
    return _topic_experience_response(experience)


@app.post("/api/attempts")
def post_attempt(
    request: AttemptRequest,
    local_dir: Path = Depends(get_local_dir),
) -> dict[str, Any]:
    if hasattr(request.question, "model_dump"):
        question = request.question.model_dump(exclude_none=True)
    else:  # Pydantic v1 compatibility for supported FastAPI installations.
        question = request.question.dict(exclude_none=True)
    result = record_browser_attempt(
        request.task_id,
        occurred_at=request.occurred_at,
        question=question,
        correct=request.correct,
        error_cause=request.error_cause,
        local_dir=local_dir,
    )
    return {
        "recorded": {
            "progress_event_count": result.progress_event_count,
            "review_item_count": result.review_item_count,
            "review_context_count": result.review_context_count,
        },
        "today": _snapshot_read_model(result.today),
    }
