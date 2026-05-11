"""
Dashboard — executive overview page ONLY.

This page contains:
  - Hero section with KPIs
  - 4 summary cards
  - Recent candidates (top 5)
  - 2-3 AI insights
  - Quick navigation to other pages

It does NOT contain: uploads, full rankings table,
full analytics charts, or override controls.
"""

import logging
from typing import Any, Dict

import streamlit as st

from app.components.dashboard_analytics import get_dashboard_overview, render_ai_insights
from app.components.summary_cards import render_summary_cards
from app.state import get_workflow_result, initialize_session_state
from app.styles.theme import apply_theme, render_panel_end, render_panel_heading, render_panel_start

logger = logging.getLogger(__name__)


def render_dashboard() -> None:
    apply_theme()
    initialize_session_state()

    workflow_result = get_workflow_result()
    overview = get_dashboard_overview(workflow_result)

    _render_hero(overview)
    render_summary_cards(workflow_result)

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    _render_quick_actions(workflow_result)

    if workflow_result:
        _render_recent_candidates(workflow_result)

    render_panel_start()
    render_panel_heading(
        "AI Insights",
        "Evidence-grounded recommendations for recruiter decision-making.",
    )
    render_ai_insights(workflow_result)
    render_panel_end()


def _render_hero(overview: Dict[str, Any]) -> None:
    candidates = overview.get("candidates_processed", 0)
    avg_score = overview.get("average_score", 0.0)
    shortlisted = overview.get("shortlisted", 0)

    st.markdown(
        f"""
        <section class="hero-section">
            <div class="hero-grid">
                <div>
                    <div class="eyebrow">AI recruiter intelligence platform</div>
                    <h1 class="hero-title">Recruiter Intelligence</h1>
                    <p class="hero-subtitle">
                        Accelerate hiring decisions with AI-powered candidate evaluation,
                        transparent scoring, and recruiter-in-the-loop controls.
                    </p>
                </div>
                <div class="live-overview">
                    <div class="live-title">Live Overview</div>
                    <div class="live-row">
                        <div class="live-label">Candidates processed</div>
                        <div class="live-value">{candidates}</div>
                    </div>
                    <div class="live-row">
                        <div class="live-label">Average match score</div>
                        <div class="live-value">{avg_score:.0f}%</div>
                    </div>
                    <div class="live-row">
                        <div class="live-label">Shortlisted</div>
                        <div class="live-value">{shortlisted}</div>
                    </div>
                </div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def _render_quick_actions(workflow_result: Dict[str, Any]) -> None:
    render_panel_start()
    render_panel_heading("Quick Actions", "Jump directly into any recruiter workflow.")

    has_results = bool(workflow_result)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("📤  Upload & Analyze", use_container_width=True, type="primary"):
            st.session_state["_active_page"] = "Upload Workspace"
            st.rerun()
    with col2:
        if st.button("🏆  View Rankings", use_container_width=True, disabled=not has_results):
            st.session_state["_active_page"] = "Candidate Rankings"
            st.rerun()
    with col3:
        if st.button("📊  Analytics", use_container_width=True, disabled=not has_results):
            st.session_state["_active_page"] = "Analytics"
            st.rerun()
    with col4:
        if st.button("📁  Export Report", use_container_width=True, disabled=not has_results):
            st.session_state["_active_page"] = "Reports & Export"
            st.rerun()

    if not has_results:
        st.caption("Run an analysis from Upload Workspace to unlock Rankings, Analytics, and Export.")

    render_panel_end()


def _render_recent_candidates(workflow_result: Dict[str, Any]) -> None:
    outputs = workflow_result.get("workflow_outputs", {}) if isinstance(workflow_result, dict) else {}
    ranked = outputs.get("ranked_candidates", [])
    if not isinstance(ranked, list) or not ranked:
        return

    top5 = ranked[:5]

    render_panel_start()
    render_panel_heading(
        "Recent Candidates",
        "Top 5 from latest analysis. Go to Rankings for the full list.",
    )

    for i, candidate in enumerate(top5):
        name = str(candidate.get("candidate_name", candidate.get("name", f"Candidate {i+1}")))
        score = float(candidate.get("final_score", 0) or 0)
        pct = int(min(score * 100, 100)) if score <= 1 else int(min(score, 100))
        rec = str(candidate.get("recommendation", "Under Review") or "Under Review")
        badge_color = "#22C55E" if pct >= 80 else "#F59E0B" if pct >= 60 else "#EF4444"

        col_name, col_score, col_rec, col_action = st.columns([3, 1, 2, 1])
        with col_name:
            st.markdown(
                f"<div style='padding:0.4rem 0;font-weight:700;color:#111827;'>{name}</div>",
                unsafe_allow_html=True,
            )
        with col_score:
            st.markdown(
                f"<div style='padding:0.4rem 0;font-weight:800;color:{badge_color};'>{pct}%</div>",
                unsafe_allow_html=True,
            )
        with col_rec:
            st.markdown(
                f"<div style='padding:0.4rem 0;color:#6B7280;font-size:0.88rem;'>{rec[:40]}</div>",
                unsafe_allow_html=True,
            )
        with col_action:
            if st.button("View", key=f"dash_view_{i}", use_container_width=True):
                from app.state import set_selected_candidate
                set_selected_candidate(candidate)
                st.session_state["_active_page"] = "Candidate Intelligence"
                st.rerun()

        if i < len(top5) - 1:
            st.divider()

    if st.button("See All Rankings →"):
        st.session_state["_active_page"] = "Candidate Rankings"
        st.rerun()

    render_panel_end()
