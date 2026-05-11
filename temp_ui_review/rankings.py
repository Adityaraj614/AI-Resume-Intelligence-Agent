"""
Candidate Rankings — dedicated recruiter review page.

This page handles ONLY:
  - Ranked candidate list
  - AI summaries and match scores
  - Shortlist actions
  - Navigation to Candidate Intelligence view
  - Navigation to Override & Audit
"""

from typing import Any, Dict, List

import streamlit as st

from app.components.ranking_table import render_ranking_table
from app.components.summary_cards import render_summary_cards
from app.state import get_workflow_result, initialize_session_state, set_selected_candidate
from app.styles.theme import apply_theme, render_panel_end, render_panel_heading, render_panel_start


def render_rankings_page() -> None:
    apply_theme()
    initialize_session_state()

    workflow_result = get_workflow_result()

    st.markdown(
        """
        <div style="margin-bottom:1.5rem;">
            <div class="eyebrow">Recruiter review workspace</div>
            <h1 style="margin:0.25rem 0 0.5rem;color:#111827;font-size:2rem;font-weight:760;">
                Candidate Rankings
            </h1>
            <p style="color:#6B7280;font-size:0.98rem;max-width:700px;margin:0;">
                AI-ranked candidates sorted by total weighted score. Review AI summaries,
                inspect evidence, compare candidates, or apply overrides.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not workflow_result:
        _render_empty_state()
        return

    # ── KPI summary bar ─────────────────────────────────────────────────────
    render_summary_cards(workflow_result)

    st.markdown("<div style='height:0.25rem'></div>", unsafe_allow_html=True)

    # ── Quick action row ────────────────────────────────────────────────────
    col1, col2, col3, col_space = st.columns([1, 1, 1, 3])
    with col1:
        if st.button("📊  Analytics", use_container_width=True):
            st.session_state["_active_page"] = "Analytics"
            st.rerun()
    with col2:
        if st.button("✏️  Overrides", use_container_width=True):
            st.session_state["_active_page"] = "Override & Audit"
            st.rerun()
    with col3:
        if st.button("⚖️  Compare", use_container_width=True):
            st.session_state["_active_page"] = "Comparison"
            st.rerun()

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    # ── Rankings table ──────────────────────────────────────────────────────
    render_panel_start()
    render_panel_heading(
        "Ranked Candidates",
        "Candidates sorted by weighted AI score. Click a candidate to open the Intelligence view.",
    )
    render_ranking_table(workflow_result)
    render_panel_end()

    # ── Per-candidate view buttons ──────────────────────────────────────────
    _render_candidate_quick_view(workflow_result)


def _render_candidate_quick_view(workflow_result: Dict[str, Any]) -> None:
    """Render 'View' buttons for top candidates that navigate to Intelligence page."""
    outputs = workflow_result.get("workflow_outputs", {}) if isinstance(workflow_result, dict) else {}
    ranked = outputs.get("ranked_candidates", [])
    if not isinstance(ranked, list) or not ranked:
        return

    render_panel_start()
    render_panel_heading(
        "Open Candidate Intelligence",
        "Select a candidate below to open the detailed AI evidence and scoring view.",
    )

    top_candidates = ranked[:10]
    cols = st.columns(min(len(top_candidates), 5))

    for i, candidate in enumerate(top_candidates):
        name = str(candidate.get("candidate_name", candidate.get("name", f"Candidate {i+1}")))
        score = candidate.get("final_score", 0) or 0
        pct = int(min(float(score) * 100, 100)) if float(score) <= 1 else int(min(float(score), 100))
        col_idx = i % 5
        with cols[col_idx]:
            if st.button(
                f"🔍  {name[:18]}… ({pct}%)" if len(name) > 18 else f"🔍  {name} ({pct}%)",
                key=f"view_candidate_{i}",
                use_container_width=True,
            ):
                set_selected_candidate(candidate)
                st.session_state["_active_page"] = "Candidate Intelligence"
                st.rerun()

    render_panel_end()


def _render_empty_state() -> None:
    render_panel_start()
    render_panel_heading(
        "No Candidates Ranked Yet",
        "Run the workflow from Upload Workspace to see ranked candidates here.",
    )
    st.info("Go to Upload Workspace, upload a JD and resumes, then click Analyze Candidates.")
    if st.button("📤  Go to Upload Workspace", type="primary"):
        st.session_state["_active_page"] = "Upload Workspace"
        st.rerun()
    render_panel_end()


if __name__ == "__main__":
    render_rankings_page()
