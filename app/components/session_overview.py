from typing import Any, Dict, List

import streamlit as st

from app.styles.theme import render_metric_card


def render_session_overview(
    workflow_result: Dict[str, Any],
    final_candidates: List[Dict[str, Any]],
    override_history: List[Dict[str, Any]],
) -> None:
    metadata = workflow_result.get("workflow_metadata", {}) if isinstance(workflow_result, dict) else {}
    metrics = build_session_metrics(metadata, final_candidates, override_history)
    columns = st.columns(3, gap="small")

    for index, metric in enumerate(metrics):
        with columns[index % 3]:
            render_metric_card(metric["label"], metric["value"], metric["help"])


def build_session_metrics(
    metadata: Dict[str, Any],
    final_candidates: List[Dict[str, Any]],
    override_history: List[Dict[str, Any]],
) -> List[Dict[str, str]]:
    return [
        {
            "label": "Candidates Analyzed",
            "value": str(metadata.get("candidate_count", len(final_candidates))),
            "help": "Ranked workflow candidates",
        },
        {
            "label": "Shortlisted",
            "value": str(_shortlisted_count(final_candidates)),
            "help": "Final recruiter-visible status",
        },
        {
            "label": "Overrides",
            "value": str(len(override_history)),
            "help": "Recorded human review events",
        },
        {
            "label": "LinkedIn Profiles",
            "value": str(_source_count(final_candidates, "linkedin")),
            "help": "Candidate source mix",
        },
        {
            "label": "Resume Profiles",
            "value": str(_source_count(final_candidates, "resume")),
            "help": "Candidate source mix",
        },
        {
            "label": "Workflow Timestamp",
            "value": str(metadata.get("execution_timestamp", "not_provided")),
            "help": str(metadata.get("workflow_id", "Current session")),
        },
    ]


def _shortlisted_count(candidates: List[Dict[str, Any]]) -> int:
    return len([
        candidate
        for candidate in candidates
        if candidate.get("is_shortlisted") is True
        or str(candidate.get("shortlist_status", "")).strip().lower() in (
            "shortlisted",
            "include",
            "included",
            "yes",
        )
    ])


def _source_count(candidates: List[Dict[str, Any]], source_name: str) -> int:
    return len([
        candidate
        for candidate in candidates
        if str(candidate.get("source", "")).strip().lower() == source_name
    ])
