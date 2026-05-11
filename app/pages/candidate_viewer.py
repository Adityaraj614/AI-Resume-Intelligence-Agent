from html import escape
from typing import Any, Dict

import streamlit as st

from app.components.candidate_card import render_candidate_card
from app.components.candidate_sections import render_candidate_sections
from app.components.evidence_panel import render_evidence_panel
from app.components.intelligence_panel import render_intelligence_panel
from app.components.score_breakdown import render_score_breakdown
from app.state import get_selected_candidate, initialize_session_state
from app.styles.theme import render_panel_end, render_panel_heading, render_panel_start


def render_candidate_viewer(candidate: Dict[str, Any] = None) -> None:
    initialize_session_state()
    selected_candidate = candidate or resolve_selected_candidate()

    st.markdown(
        """
        <div class="page-heading">
            <div class="eyebrow">Candidate intelligence</div>
            <h1>Candidate Intelligence</h1>
            <p>Deep-dive into semantic fit, evidence matching, strengths, skill gaps, recruiter notes, and AI reasoning.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not selected_candidate:
        render_empty_candidate_state()
        return

    render_panel_start()
    render_panel_heading(
        "Candidate Overview",
        "Core recruiter-facing candidate signals and source attribution.",
    )
    render_candidate_card(selected_candidate)
    render_panel_end()

    _render_recruiter_copilot_summary(selected_candidate)

    left, right = st.columns([0.66, 0.34], gap="large")

    with left:
        render_intelligence_panel(selected_candidate)

    with right:
        render_score_breakdown(selected_candidate)

    render_evidence_panel(selected_candidate)
    render_candidate_sections(selected_candidate)


def _render_recruiter_copilot_summary(candidate: Dict[str, Any]) -> None:
    name = str(candidate.get("candidate_name", candidate.get("name", "This candidate")))
    recommendation = str(candidate.get("recommendation", "Needs recruiter review"))
    reasoning = str(
        candidate.get(
            "ranking_reason",
            candidate.get("decision_summary", "Review the evidence below to confirm semantic fit and hiring readiness."),
        )
        or "Review the evidence below to confirm semantic fit and hiring readiness."
    )
    strengths = _list_text(candidate.get("strengths", candidate.get("extracted_skills", [])), limit=3)
    gaps = _list_text(candidate.get("missing_skills", candidate.get("skill_gaps", [])), limit=3)

    strengths_text = ", ".join(strengths) if strengths else "Evidence-backed strengths will appear after analysis."
    gaps_text = ", ".join(gaps) if gaps else "No explicit skill gaps were attached to this candidate."

    st.markdown(
        f"""
        <div class="candidate-copilot">
            <div class="candidate-copilot-title">Recruiter Copilot Summary</div>
            <div class="candidate-copilot-copy">
                <strong>{escape(name)}</strong> is currently marked as <strong>{escape(recommendation)}</strong>.
                {escape(reasoning)}
                <br><br>
                <strong>Strengths:</strong> {escape(strengths_text)}
                <br>
                <strong>Skill gaps:</strong> {escape(gaps_text)}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _list_text(value: Any, limit: int) -> list:
    if value is None:
        return []

    values = value if isinstance(value, list) else [value]
    return [str(item).strip() for item in values if str(item).strip()][:limit]


def resolve_selected_candidate() -> Dict[str, Any]:
    """
    Integration hook for dashboard/workflow-selected candidates.

    This viewer consumes existing candidate dictionaries and does not run
    retrieval, scoring, ranking, or LLM logic itself.
    """

    return get_selected_candidate()


def render_empty_candidate_state() -> None:
    render_panel_start()
    render_panel_heading(
        "No Candidate Selected",
        "Run the recruiter workflow or set a selected candidate to open this explainability view.",
    )
    st.info(
        "Run analysis to unlock the recruiter copilot view for each candidate, including AI reasoning, semantic fit, strengths, skill gaps, and grounded evidence."
    )
    if st.button("Open Candidate Rankings", type="primary"):
        st.session_state["_active_page"] = "Candidate Rankings"
        st.rerun()
    render_panel_end()


if __name__ == "__main__":
    render_candidate_viewer()
