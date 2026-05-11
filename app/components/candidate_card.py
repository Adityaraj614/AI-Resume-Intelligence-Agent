from html import escape
from typing import Any, Dict

import streamlit as st

from app.styles.theme import render_metric_card


def render_candidate_card(candidate: Dict[str, Any]) -> None:
    name = candidate.get("candidate_name", candidate.get("name", "Unknown Candidate"))
    candidate_id = candidate.get("candidate_id", "unknown_candidate")
    source = candidate.get("source", "resume")
    recommendation = candidate.get("recommendation", "Needs Review")

    st.markdown(
        f"""
        <div class="info-card">
            <div class="candidate-title">{escape(str(name))}</div>
            <div class="candidate-meta">Candidate ID: {escape(str(candidate_id))} · Source: {escape(str(source))}</div>
            <div style="margin-top:0.75rem;">
                <span class="status-badge">{escape(str(recommendation))}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    columns = st.columns(3, gap="small")

    with columns[0]:
        render_metric_card("Match Score", _format_score(candidate.get("final_score")), "Hybrid recruiter score")

    with columns[1]:
        render_metric_card("Confidence", _format_confidence(candidate), "Analysis confidence")

    with columns[2]:
        render_metric_card("Source", str(source).title(), "Candidate profile origin")


def _format_score(value: Any) -> str:
    return f"{float(value or 0.0):.2f}"


def _format_confidence(candidate: Dict[str, Any]) -> str:
    value = candidate.get("confidence", candidate.get("confidence_score", 0.0))
    return f"{float(value or 0.0):.2f}"
