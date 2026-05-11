import logging
from html import escape
from typing import Any, Dict

import streamlit as st

from app.components.dashboard_analytics import get_dashboard_overview, render_ai_insights
from app.components.summary_cards import render_summary_cards
from app.state import get_workflow_result, initialize_session_state, set_selected_candidate, set_workflow_result
from app.styles.theme import render_hero, render_panel_end, render_panel_heading, render_panel_start
from core.workflow.dashboard_workflow import DashboardWorkflowError, run_dashboard_workflow


logger = logging.getLogger(__name__)


def render_dashboard() -> None:
    initialize_session_state()
    workflow_result = get_workflow_result()
    overview = get_dashboard_overview(workflow_result)

    render_hero(
        candidates_processed=overview["candidates_processed"],
        average_score=overview["average_score"],
        shortlisted=overview["shortlisted"],
    )

    render_summary_cards(workflow_result)
    _render_recent_candidates(workflow_result)

    render_panel_start()
    render_panel_heading(
        "AI Insights",
        "Concise recruiter guidance from the latest workflow output.",
    )
    render_ai_insights(workflow_result, limit=3)
    render_panel_end()

    _render_quick_navigation(workflow_result)


def run_dashboard_analysis(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute the existing backend intake, ranking, and recruiter workflow
    using the lightweight CrewAI orchestration wrapper.
    """
    from core.agents.crew import LightweightOrchestrator
    
    orchestrator = LightweightOrchestrator()
    return orchestrator.run_sequential_flow(inputs)


def _render_recent_candidates(workflow_result: Dict[str, Any]) -> None:
    outputs = workflow_result.get("workflow_outputs", {}) if isinstance(workflow_result, dict) else {}
    candidates = outputs.get("ranked_candidates", [])

    render_panel_start()
    render_panel_heading(
        "Recent Candidates",
        "Top 5 from the latest analysis. Open Rankings for the full recruiter review workspace.",
    )

    if not isinstance(candidates, list) or not candidates:
        st.markdown(
            """
            <div class="empty-state">
                <div class="empty-state-icon">AI</div>
                <div class="empty-state-title">Activate your recruiter workspace</div>
                <div class="empty-state-copy">
                    Upload resumes and a job description to activate AI candidate analysis.
                    Once the workflow runs, this dashboard will show recent candidates,
                    recruiter insights, rankings, analytics, and report handoff options.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Go to Upload Workspace", type="primary"):
            _navigate("Upload Workspace")
        render_panel_end()
        return

    for index, candidate in enumerate(candidates[:5]):
        _render_recent_candidate_row(index, candidate)

    if st.button("Open Candidate Rankings", width="stretch"):
        _navigate("Candidate Rankings")

    render_panel_end()


def _render_recent_candidate_row(index: int, candidate: Dict[str, Any]) -> None:
    name = str(candidate.get("candidate_name", candidate.get("name", f"Candidate {index + 1}")))
    recommendation = str(candidate.get("recommendation", "Under Review") or "Under Review")
    score = _score_to_percent(float(candidate.get("final_score", 0.0) or 0.0))
    status_class = "status-shortlisted" if score >= 80 else "status-consider" if score >= 60 else "status-low"

    left, score_col, status_col, action_col = st.columns([3.2, 0.9, 1.5, 1.0], gap="small")

    with left:
        st.markdown(
            f"""
            <div class="recent-candidate-main">
                <div class="candidate-avatar">{escape(_initials(name))}</div>
                <div>
                    <div class="candidate-name">{escape(name)}</div>
                    <div class="candidate-role">{escape(str(candidate.get("source", "resume")).title())} source</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with score_col:
        st.markdown(
            f'<div class="recent-score">{score:.0f}%</div>',
            unsafe_allow_html=True,
        )

    with status_col:
        st.markdown(
            f'<span class="status-badge {status_class}">{escape(recommendation[:24])}</span>',
            unsafe_allow_html=True,
        )

    with action_col:
        if st.button("View", key=f"dashboard_view_candidate_{index}", width="stretch"):
            set_selected_candidate(candidate)
            _navigate("Candidate Intelligence")


def _render_quick_navigation(workflow_result: Dict[str, Any]) -> None:
    workflow_ready = bool(workflow_result)

    render_panel_start()
    render_panel_heading(
        "Quick Navigation",
        "Move through the recruiter workflow without crowding the dashboard.",
    )

    col_upload, col_rankings, col_analytics, col_reports = st.columns(4, gap="small")

    with col_upload:
        if st.button("Upload Workspace", type="primary", width="stretch"):
            _navigate("Upload Workspace")

    with col_rankings:
        if st.button("Rankings", width="stretch", disabled=not workflow_ready):
            _navigate("Candidate Rankings")

    with col_analytics:
        if st.button("Analytics", width="stretch", disabled=not workflow_ready):
            _navigate("Analytics")

    with col_reports:
        if st.button("Reports", width="stretch", disabled=not workflow_ready):
            _navigate("Reports")

    if not workflow_ready:
        st.caption("Run an analysis to unlock Rankings, Analytics, Reports, Comparison, and Overrides.")

    render_panel_end()


def _navigate(page: str) -> None:
    st.session_state["_active_page"] = page
    st.rerun()


def _score_to_percent(score: float) -> float:
    if score <= 1.0:
        return max(0.0, min(score * 100.0, 100.0))
    if score <= 10.0:
        return max(0.0, min(score * 10.0, 100.0))
    return max(0.0, min(score, 100.0))


def _initials(name: str) -> str:
    parts = [part for part in name.replace("_", " ").split() if part]
    return "".join(part[0].upper() for part in parts[:2]) or "AI"


def _handle_analyze_click(inputs: Dict[str, Any]) -> None:
    try:
        workflow_result = run_dashboard_analysis(inputs)
    except DashboardWorkflowError as exc:
        logger.warning("dashboard_analysis_failed", exc_info=True)
        st.error(str(exc))
        return

    st.session_state["dashboard_inputs"] = inputs
    set_workflow_result(workflow_result)
