from typing import Any, Dict, List

import streamlit as st

from app.components.ranking_table import render_ranking_table
from app.components.summary_cards import render_summary_cards
from app.state import get_workflow_result, initialize_session_state, set_selected_candidate
from app.styles.theme import render_panel_end, render_panel_heading, render_panel_start


def render_rankings_page() -> None:
    initialize_session_state()
    workflow_result = get_workflow_result()

    st.markdown(
        """
        <div class="page-heading">
            <div class="eyebrow">Recruiter review workspace</div>
            <h1>Candidate Rankings</h1>
            <p>Review AI-ranked candidates, inspect match indicators, open candidate intelligence, compare profiles, or apply recruiter overrides.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not workflow_result:
        _render_empty_state()
        return

    render_summary_cards(workflow_result)
    _render_action_bar()

    render_panel_start()
    render_panel_heading(
        "Ranked Candidate Review",
        "Candidates are sorted by the existing deterministic ranking workflow. UI actions do not rerun ranking.",
    )
    render_ranking_table(workflow_result)
    render_panel_end()

    _render_candidate_intelligence_picker(workflow_result)


def _render_action_bar() -> None:
    render_panel_start()
    render_panel_heading(
        "Review Actions",
        "Continue through comparison, overrides, analytics, or final reports.",
    )

    col_compare, col_override, col_analytics, col_reports = st.columns(4, gap="small")

    with col_compare:
        if st.button("Compare Candidates", width="stretch"):
            _navigate("Comparison")

    with col_override:
        if st.button("Override Workflow", width="stretch"):
            _navigate("Override & Audit")

    with col_analytics:
        if st.button("Open Analytics", width="stretch"):
            _navigate("Analytics")

    with col_reports:
        if st.button("Export Reports", width="stretch"):
            _navigate("Reports")

    render_panel_end()


def _render_candidate_intelligence_picker(workflow_result: Dict[str, Any]) -> None:
    candidates = _ranked_candidates(workflow_result)

    if not candidates:
        return

    render_panel_start()
    render_panel_heading(
        "Open Candidate Intelligence",
        "Select a candidate to deep-dive into semantic fit, evidence, strengths, and skill gaps.",
    )

    columns = st.columns(min(len(candidates[:10]), 5), gap="small")

    for index, candidate in enumerate(candidates[:10]):
        name = str(candidate.get("candidate_name", candidate.get("name", f"Candidate {index + 1}")))
        score = _score_to_percent(float(candidate.get("final_score", 0.0) or 0.0))

        with columns[index % len(columns)]:
            if st.button(f"{name[:18]} ({score:.0f}%)", key=f"rankings_candidate_{index}", width="stretch"):
                set_selected_candidate(candidate)
                _navigate("Candidate Intelligence")

    render_panel_end()


def _render_empty_state() -> None:
    render_panel_start()
    render_panel_heading(
        "Rankings Not Ready",
        "Run analysis from Upload Workspace before reviewing ranked candidates.",
    )
    st.info("Upload a JD and candidate files, then analyze them to unlock this workspace.")

    if st.button("Go to Upload Workspace", type="primary"):
        _navigate("Upload Workspace")

    render_panel_end()


def _ranked_candidates(workflow_result: Dict[str, Any]) -> List[Dict[str, Any]]:
    outputs = workflow_result.get("workflow_outputs", {}) if isinstance(workflow_result, dict) else {}
    candidates = outputs.get("ranked_candidates", [])

    if not isinstance(candidates, list):
        return []

    return [candidate for candidate in candidates if isinstance(candidate, dict)]


def _score_to_percent(score: float) -> float:
    if score <= 1:
        return max(0.0, min(score * 100, 100.0))

    return max(0.0, min(score, 100.0))


def _navigate(page: str) -> None:
    st.session_state["_active_page"] = page
    st.rerun()
