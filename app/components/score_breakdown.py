from html import escape
from typing import Any, Dict, List

import streamlit as st


def render_score_breakdown(candidate: Dict[str, Any]) -> None:
    st.markdown(
        """
        <div class="dashboard-panel-title">Score Breakdown</div>
        <div class="dashboard-panel-subtitle">Lightweight recruiter-readable signal view.</div>
        """,
        unsafe_allow_html=True,
    )

    for metric in build_score_metrics(candidate):
        _render_progress_row(metric["label"], metric["value"], metric["help"])


def build_score_metrics(candidate: Dict[str, Any]) -> List[Dict[str, Any]]:
    return [
        {
            "label": "Skill Alignment",
            "value": _coerce_unit(candidate.get("semantic_score", candidate.get("retrieval_quality", 0.0))),
            "help": "Semantic match to required skills",
        },
        {
            "label": "Experience Relevance",
            "value": _coerce_unit(candidate.get("experience_relevance", candidate.get("evidence_quality", 0.0))),
            "help": "Evidence-backed work history signal",
        },
        {
            "label": "Education Fit",
            "value": _coerce_unit(candidate.get("education_fit", 0.0)),
            "help": "Education signal when available",
        },
        {
            "label": "Project Relevance",
            "value": _coerce_unit(candidate.get("project_relevance", candidate.get("retrieval_quality", 0.0))),
            "help": "Project and portfolio alignment",
        },
        {
            "label": "Confidence",
            "value": _coerce_unit(candidate.get("confidence", candidate.get("confidence_score", 0.0))),
            "help": "Trust signal for recruiter review",
        },
    ]


def _render_progress_row(label: str, value: float, help_text: str) -> None:
    percentage = int(round(value * 100))
    st.markdown(
        f"""
        <div class="score-row">
            <div class="score-label-row">
                <span>{escape(label)}</span>
                <span>{percentage}%</span>
            </div>
            <div class="progress-track">
                <div class="progress-fill" style="width:{percentage}%;"></div>
            </div>
            <div class="metric-help">{escape(help_text)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _coerce_unit(value: Any) -> float:
    number = float(value or 0.0)

    if number > 1.0:
        number = number / 10.0

    return min(max(number, 0.0), 1.0)
