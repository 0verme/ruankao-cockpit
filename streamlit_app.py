"""Single-page local Streamlit entry for the ruankao-cockpit MVP."""
from __future__ import annotations

from datetime import datetime
import os
from pathlib import Path
from typing import Any, Mapping
from zoneinfo import ZoneInfo

import streamlit as st

from cockpit_service import (
    PROJECT_ROOT,
    CockpitError,
    TodaySnapshot,
    get_today,
    get_topic_experience,
    initialize_cockpit,
    record_browser_attempt,
)
from learning_payload import LearningPayloadError, learning_source_url
from topic_experience import TopicExperience, TopicExperienceError


ERROR_CAUSES = {
    "knowledge_gap": "知识缺口",
    "reading_error": "阅读错误",
    "calculation_error": "计算错误",
    "scoring_point_expression": "得分点表达",
}


def _local_dir() -> Path:
    configured = os.environ.get("COCKPIT_LOCAL_DIR")
    return Path(configured).expanduser() if configured else PROJECT_ROOT / ".local"


def _debug_enabled() -> bool:
    return os.environ.get("COCKPIT_DEBUG", "").lower() in {"1", "true", "yes"}


def _friendly_error(exc: BaseException) -> str:
    category = getattr(exc, "category", "")
    messages = {
        "not_initialized": "Cockpit 尚未初始化。请先点击初始化。",
        "incomplete_local_data": "本地数据不完整；为避免覆盖事实，Cockpit 未自动重建。",
        "task_not_scheduled": "该任务已不属于当前 Today 计划，请刷新后重试。",
        "unknown_task": "当前 Today 计划中找不到该任务，请刷新后重试。",
        "missing_source_reference": "来源信息不完整，无法记录。",
        "invalid_source_reference": "来源引用格式不符合要求，无法记录。",
        "forbidden_path": "来源路径必须是安全的仓库相对路径，不能包含绝对路径或目录跳转。",
        "target_mismatch": "作答 Topic 与当前任务不一致，未写入记录。",
        "invalid_timestamp": "作答时间必须是有效且带时区的 ISO 8601 时间。",
        "future_evidence": "作答时间晚于当前 Today 的重放时间，请修正时间或刷新页面。",
        "invalid_event": "作答事实或来源字段不符合现有 contract，请检查引用格式。",
        "invalid_schema_version": "事件版本与当前支持的事实格式不一致，未写入记录。",
        "invalid_replay_input": "Progress / Review replay 校验未通过，记录没有写入。",
        "duplicate_event": "相同记录身份已存在；系统未重复写入，请刷新 Today 确认状态。",
        "duplicate_event_id": "Progress event ID 已存在；系统未重复写入。",
        "duplicate_review_event": "Review Context ID 已存在；系统未重复写入。",
        "duplicate_review_context": "该 Progress fact 已关联过此 Review 项，未重复写入。",
        "invalid_review_target": "复习目标缺少有效 Topic 映射，已停止记录。",
        "unsupported_execution_target": "当前任务类型不支持此记录表单。",
    }
    if category in messages:
        return messages[category]
    return "未能完成记录；事实未通过现有校验。请检查必填来源、作答时间及输入格式。"


def _task_target(task: Mapping[str, Any], snapshot: TodaySnapshot) -> str:
    review_catalog = {item["review_item_id"]: item for item in snapshot.review_items}
    if task.get("task_type") == "review":
        item = review_catalog.get(task.get("target_ref"), {})
        topic_id = item.get("canonical_ref", {}).get("topic_id")
    else:
        topic_id = task.get("target_ref")
    if isinstance(topic_id, str):
        return topic_id
    return str(task.get("target_ref", "未知目标"))


def _task_reason(task: Mapping[str, Any], planner_output: Mapping[str, Any]) -> tuple[str, str, str]:
    trace_id = task.get("explain_trace_id")
    trace = next(
        (item for item in planner_output.get("explain_traces", []) if item.get("trace_id") == trace_id),
        None,
    )
    if not isinstance(trace, Mapping):
        return "原因不可用（Planner 未提供安排说明）", "", ""
    reason_code = str(trace.get("reason_code") or "")
    display_message = str(trace.get("display_message") or "原因不可用")
    friendly_messages = {
        "next_unlearned_topic": "按学习顺序安排下一个尚未形成学习记录的知识点",
        "overdue_review": "这项内容已超过计划复习时间",
        "due_today_review": "这项内容今天到期，需要复习",
    }
    return friendly_messages.get(reason_code, display_message), reason_code, display_message


def _render_topic_experience(experience: TopicExperience) -> None:
    payload = experience.learning_payload
    st.markdown(f"### {experience.topic_name}")
    st.caption(" › ".join(item.name for item in experience.breadcrumb))
    if experience.has_learning_payload:
        st.caption(f"学习材料：已整理 · Learning Payload {experience.learning_payload_version}")
    else:
        st.caption("学习材料：材料尚未整理")

    progress_label = f"验证 attempt：{experience.progress_attempt_count} 次"
    if experience.progress_accuracy is not None:
        progress_label += f" · accuracy {experience.progress_accuracy:.0%}"
    st.caption(progress_label)
    if experience.review_status is not None:
        mastery_labels = {
            "new": "新建",
            "learning": "学习中",
            "mastered": "达到当前 Review Policy 阈值",
        }
        review_labels = {
            "not_scheduled": "尚未排期",
            "scheduled": "已安排",
            "due": "今日到期",
            "overdue": "已逾期",
        }
        review_text = (
            f"复习：{mastery_labels.get(experience.review_mastery_state, experience.review_mastery_state)}"
            f" · {review_labels.get(experience.review_status, experience.review_status)}"
        )
        if experience.review_next_due_local_date:
            review_text += f" · 下次复习 {experience.review_next_due_local_date}"
        if experience.review_policy_version:
            review_text += f" · {experience.review_policy_version}"
        st.caption(review_text)

    with st.expander("Topic 详情"):
        st.caption(f"Canonical Topic ID：{experience.topic_id}")
        st.caption(f"Taxonomy version：{experience.taxonomy_version}")

    if payload is None:
        st.info("材料尚未整理。不会自动生成内容；你仍可使用已有外部资料学习。")
        return

    references = {item["reference_id"]: item for item in payload["source_references"]}
    st.markdown("**今天学会什么**")
    for item in payload["objectives"]:
        st.markdown(f"- {item['text']}")

    st.markdown("**核心知识**")
    for point in payload["core_points"]:
        st.markdown(f"**{point['heading']}**\n\n{point['text']}")

    st.markdown("**软考关注点**")
    for item in payload["exam_focus"]:
        st.markdown(f"- {item['text']}")
        evidence_titles = [references[ref_id]["display_title"] for ref_id in item["evidence_refs"]]
        st.caption("依据：" + "；".join(evidence_titles))

    st.markdown("**学习来源**")
    for reference in payload["source_references"]:
        url = learning_source_url(reference)
        st.markdown(f"- [{reference['display_title']}]({url})")
    with st.expander("查看来源信息"):
        st.caption(f"Learning Payload {payload['version']} · schema {payload['schema_version']}")
        for reference in payload["source_references"]:
            details = [
                f"source_id: {reference['source_id']}",
                f"source_commit: {reference['source_commit']}",
                f"source_path: {reference['source_path']}",
                f"confidence: {reference['confidence']}",
            ]
            if "source_value" in reference:
                details.append(f"source_value: {reference['source_value']}")
                details.append(f"source_anchor: {reference['source_anchor']}")
            if "source_question_id" in reference:
                details.append(f"source_question_id: {reference['source_question_id']}")
                details.append(f"golden_set_record_id: {reference['golden_set_record_id']}")
            st.markdown(f"**{reference['display_title']}**")
            st.code("\n".join(details), language=None)


def _render_verification(
    task: Mapping[str, Any],
    snapshot: TodaySnapshot,
    local_dir: Path,
    verification_sources: tuple[Mapping[str, Any], ...],
) -> bool:
    """Render the existing optional attempt form for a Today task."""
    planner_output = snapshot.planner_output
    task_type = task.get("task_type")
    prefix = f"record-{task['task_id']}"
    if task_type == "new_learning":
        st.markdown("##### 学完后验证")
        st.caption("学习与答题记录是两件事；只有实际作答后才记录 attempt。")
    else:
        st.markdown("##### 复习后验证")

    source_options: dict[str, Mapping[str, Any]] = {}
    for record in verification_sources:
        label_text = str(record.get("display_title") or "已索引综合题")
        source_reference = record.get("source_reference")
        if isinstance(source_reference, Mapping):
            source_options[label_text] = source_reference
    manual_choice = "其他来源（手动填写引用）"
    choices = ["请选择验证题", *source_options, manual_choice]
    if not source_options:
        choices = [manual_choice]
        st.caption("当前 Topic 没有已索引验证题；如使用了外部题目，可在备用引用中填写来源。")
    source_choice = st.selectbox(
        "验证题来源（只选择你实际使用过的题目）",
        choices,
        key=f"{prefix}-source-choice",
    )
    question: dict[str, Any] | None = dict(source_options[source_choice]) if source_choice in source_options else None
    if question is not None:
        st.caption(f"已选择：{source_choice}")
        with st.expander("查看题目来源信息"):
            st.code(
                "\n".join(
                    f"{key}: {question[key]}"
                    for key in ("source_id", "source_commit", "source_path", "source_question_id", "golden_set_record_id")
                    if key in question
                ),
                language=None,
            )

    source_id = source_commit = source_path = source_question_id = ""
    if source_choice == manual_choice:
        with st.expander("备用：手动填写未索引题目引用", expanded=not bool(source_options)):
            source_id = st.text_input("来源 ID", key=f"{prefix}-source-id")
            source_commit = st.text_input(
                "来源不可变版本（40 位小写 commit）", key=f"{prefix}-source-commit"
            )
            source_path = st.text_input(
                "来源相对路径", key=f"{prefix}-source-path", help="必须是来源仓库内的相对路径，不含绝对路径或目录跳转。"
            )
            source_question_id = st.text_input("来源题目 ID", key=f"{prefix}-source-question-id")

    timezone_name = planner_output["timezone"]
    local_zone = ZoneInfo(timezone_name)
    occurred_at_key = f"{prefix}-occurred-at"
    default_occurred_at_key = f"{prefix}-default-occurred-at"
    if occurred_at_key not in st.session_state:
        default_occurred_at = datetime.now(local_zone).isoformat(timespec="seconds")
        st.session_state[occurred_at_key] = default_occurred_at
        st.session_state[default_occurred_at_key] = default_occurred_at
    occurred_at = st.text_input(
        f"实际作答时间（默认 {timezone_name} 当前时间，可修改）",
        key=occurred_at_key,
        help="保存为带显式时区的 ISO 8601 时间；默认时区来自本地 User Configuration，不读取服务器时区。未修改时按点击记录的时间写入。",
    )
    outcome = st.selectbox(
        "作答结果（必选）", ["请选择", "答对", "答错"], key=f"{prefix}-outcome"
    )
    cause_label = "不填写"
    if outcome == "答错":
        cause_label = st.selectbox(
            "错误原因（可选；不确定可不填）",
            ["不填写", *ERROR_CAUSES.values()],
            key=f"{prefix}-error-cause",
        )
    st.caption("只记录事实和来源引用；请勿粘贴题干、选项、答案或解析。")
    submitted = st.button("记录本次结果", key=f"{prefix}-submit", type="primary", use_container_width=True)

    if not submitted:
        return False
    if outcome == "请选择":
        st.error("请明确选择答对或答错。")
        return False
    if source_choice == manual_choice:
        question = {
            "source_id": source_id.strip(),
            "source_commit": source_commit.strip(),
            "source_path": source_path.strip(),
            "source_question_id": source_question_id.strip(),
        }
    if question is None or any(
        not isinstance(question.get(key), str) or not question[key].strip()
        for key in ("source_id", "source_commit", "source_path", "source_question_id")
    ):
        st.error("请明确选择已索引来源或填写完整备用引用；信息不完整时不会写入事实。")
        return False
    if not occurred_at.strip():
        st.error("请填写实际作答时间；信息缺失时不会写入事实。")
        return False

    error_cause = None
    if outcome == "答错" and cause_label != "不填写":
        error_cause = next(key for key, value in ERROR_CAUSES.items() if value == cause_label)
    occurred_at_to_record = occurred_at.strip()
    if occurred_at_to_record == st.session_state.get(default_occurred_at_key):
        occurred_at_to_record = datetime.now(local_zone).isoformat(timespec="seconds")
    try:
        record_as_of = datetime.now(local_zone).isoformat(timespec="seconds")
        result = record_browser_attempt(
            task["task_id"],
            occurred_at=occurred_at_to_record,
            question=question,
            correct=outcome == "答对",
            error_cause=error_cause,
            as_of=record_as_of,
            local_dir=local_dir,
        )
    except (CockpitError, LearningPayloadError, OSError, ValueError, KeyError, TypeError) as exc:
        st.error(_friendly_error(exc))
        if _debug_enabled():
            with st.expander("诊断详情"):
                st.exception(exc)
        return False

    # Flash metadata only; every rerun reloads domain state from .local via get_today().
    st.session_state["cockpit_record_notice"] = {
        "progress": result.progress_event_count,
        "review_items": result.review_item_count,
        "review_contexts": result.review_context_count,
    }
    st.rerun()
    return True


def _render_task(task: Mapping[str, Any], snapshot: TodaySnapshot, local_dir: Path) -> bool:
    planner_output = snapshot.planner_output
    task_type = task.get("task_type")
    label = {"review": "REVIEW", "new_learning": "NEW LEARNING"}.get(task_type, str(task_type))
    topic_id = _task_target(task, snapshot)
    reason, reason_code, raw_reason = _task_reason(task, planner_output)

    with st.container(border=True):
        st.markdown(f"#### {label}")
        st.caption(f"计划 {task['planned_minutes']} 分钟")
        st.caption(reason)
        with st.expander("查看安排依据"):
            if reason_code:
                st.caption(f"原始安排说明：{raw_reason}")
                st.code(reason_code, language=None)
            else:
                st.write("Planner 未提供结构化 reason code。")
            st.caption(f"Topic ID：{topic_id}")

        if task_type not in {"review", "new_learning"}:
            return False

        try:
            experience = get_topic_experience(topic_id, snapshot)
        except LearningPayloadError as exc:
            st.error("学习材料来源校验未通过，已停止展示该材料。")
            if _debug_enabled():
                with st.expander("学习材料诊断详情"):
                    st.exception(exc)
            return False
        except TopicExperienceError as exc:
            st.error("无法从现有 Taxonomy / Progress / Review 状态构建 Topic Experience。")
            if _debug_enabled():
                with st.expander("Topic Experience 诊断详情"):
                    st.exception(exc)
            return False

        _render_topic_experience(experience)
        st.divider()
        return _render_verification(
            task,
            snapshot,
            local_dir,
            experience.verification_sources,
        )


def _render_today(snapshot: TodaySnapshot, local_dir: Path) -> None:
    planner_output = snapshot.planner_output
    day = planner_output["days"][0]
    st.subheader(f"今天 · {day['local_date']}")
    st.caption(f"按现有 Today Planner 输出 · as_of {planner_output['as_of']} · {planner_output['timezone']}")

    available, planned, remaining = st.columns(3)
    available.metric("今日可用", f"{day['capacity_minutes']} min")
    planned.metric("已安排", f"{day['planned_minutes']} min")
    remaining.metric("剩余容量", f"{day['remaining_minutes']} min")

    unmet_demand = day.get("unmet_demand", [])
    if unmet_demand:
        st.info(f"还有 {len(unmet_demand)} 项今天无法安排。")

    tasks = day.get("tasks", [])
    if not tasks:
        st.info("Today Planner 当前没有安排任务。")
        return
    for task in tasks:
        _render_task(task, snapshot, local_dir)


def main() -> None:
    st.set_page_config(page_title="ruankao-cockpit", page_icon="📚", layout="wide")
    st.markdown(
        """
        <style>
        [data-testid="stAppViewContainer"] { background: #f8f7f4; }
        .block-container { max-width: 1080px; padding-top: 2rem; }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.title("ruankao-cockpit")
    st.caption("本地单用户备考工作台 · 数据保存在本机 · 不托管题库正文")

    local_dir = _local_dir()
    if not local_dir.exists():
        st.warning("Cockpit 尚未初始化")
        st.write("初始化只会在本地创建必要配置和空事实文件，不会覆盖已有事实。")
        if st.button("初始化", type="primary"):
            try:
                initialize_cockpit(local_dir)
            except (CockpitError, OSError, ValueError, TypeError) as exc:
                st.error(_friendly_error(exc))
                if _debug_enabled():
                    with st.expander("诊断详情"):
                        st.exception(exc)
            else:
                st.session_state["cockpit_initialized_notice"] = True
                st.rerun()
        return

    try:
        snapshot = get_today(local_dir=local_dir)
    except (CockpitError, OSError, ValueError, KeyError, TypeError) as exc:
        st.error(_friendly_error(exc))
        if _debug_enabled():
            with st.expander("诊断详情"):
                st.exception(exc)
        return

    if st.session_state.pop("cockpit_initialized_notice", False):
        st.success("Cockpit 已初始化。")
    notice = st.session_state.pop("cockpit_record_notice", None)
    if isinstance(notice, Mapping):
        st.success(
            "记录成功：Progress fact 已写入；Review Context 已写入，Review / Progress 已重放并更新。"
        )
        if notice.get("review_items"):
            st.caption(f"已注册 {notice['review_items']} 个 Review Item。")

    _render_today(snapshot, local_dir)


if __name__ == "__main__":
    main()
