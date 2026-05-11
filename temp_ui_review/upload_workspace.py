"""
Upload Workspace — dedicated intake page.

This page handles ONLY:
  - JD text / file upload
  - Resume PDF upload
  - LinkedIn JSON upload
  - Analyze Candidates trigger

No rankings, no analytics, no clutter.
"""

import logging
from typing import Any, Dict

import streamlit as st

from app.components.upload_widget import render_upload_section, validate_dashboard_inputs
from app.state import get_workflow_result, set_workflow_result
from app.styles.theme import apply_theme, render_panel_end, render_panel_heading, render_panel_start
from core.workflow.dashboard_workflow import DashboardWorkflowError, run_dashboard_workflow

logger = logging.getLogger(__name__)


def render_upload_workspace() -> None:
    apply_theme()

    st.markdown(
        """
        <div style="margin-bottom:1.5rem;">
            <div class="eyebrow">AI intake workspace</div>
            <h1 style="margin:0.25rem 0 0.5rem;color:#111827;font-size:2rem;font-weight:760;">
                Upload Workspace
            </h1>
            <p style="color:#6B7280;font-size:0.98rem;max-width:640px;margin:0;">
                Upload a Job Description and candidate sources, then run the AI recruiter workflow.
                Results will appear in <strong>Candidate Rankings</strong> and <strong>Analytics</strong>.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Workflow progress indicator ─────────────────────────────────────────
    st.markdown(
        """
        <div style="display:flex;align-items:center;gap:0.6rem;margin-bottom:1.5rem;
                    background:rgba(255,255,255,0.7);border:1px solid rgba(0,0,0,0.06);
                    border-radius:16px;padding:0.75rem 1.2rem;width:fit-content;">
            <span style="background:#4F46E5;color:#fff;border-radius:50%;width:26px;height:26px;
                          display:grid;place-items:center;font-size:0.75rem;font-weight:800;">1</span>
            <span style="font-size:0.85rem;font-weight:700;color:#4F46E5;">Upload</span>
            <span style="color:#D1D5DB;">→</span>
            <span style="background:#E5E7EB;color:#9CA3AF;border-radius:50%;width:26px;height:26px;
                          display:grid;place-items:center;font-size:0.75rem;font-weight:800;">2</span>
            <span style="font-size:0.85rem;font-weight:700;color:#9CA3AF;">Analyze</span>
            <span style="color:#D1D5DB;">→</span>
            <span style="background:#E5E7EB;color:#9CA3AF;border-radius:50%;width:26px;height:26px;
                          display:grid;place-items:center;font-size:0.75rem;font-weight:800;">3</span>
            <span style="font-size:0.85rem;font-weight:700;color:#9CA3AF;">Review</span>
            <span style="color:#D1D5DB;">→</span>
            <span style="background:#E5E7EB;color:#9CA3AF;border-radius:50%;width:26px;height:26px;
                          display:grid;place-items:center;font-size:0.75rem;font-weight:800;">4</span>
            <span style="font-size:0.85rem;font-weight:700;color:#9CA3AF;">Export</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_panel_start()
    render_panel_heading(
        "Job Description & Candidate Sources",
        "Upload the role context and candidate files before running analysis.",
    )
    inputs = render_upload_section()
    render_panel_end()

    # ── Analyze button ──────────────────────────────────────────────────────
    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
    col_info, col_btn = st.columns([0.68, 0.32])
    with col_info:
        st.markdown(
            "<p style='color:#6B7280;font-size:0.9rem;margin:0;padding-top:0.6rem;'>"
            "After analysis, navigate to <strong>Candidate Rankings</strong> to review results."
            "</p>",
            unsafe_allow_html=True,
        )
    with col_btn:
        analyze_clicked = st.button(
            "⚡  Analyze Candidates",
            type="primary",
            use_container_width=True,
        )

    if analyze_clicked:
        _handle_analyze(inputs)

    # ── Status feedback if workflow already ran ─────────────────────────────
    workflow_result = get_workflow_result()
    if workflow_result:
        outputs = workflow_result.get("workflow_outputs", {})
        ranked = outputs.get("ranked_candidates", [])
        count = len(ranked) if isinstance(ranked, list) else 0
        st.success(
            f"✅  Last analysis processed **{count} candidate(s)**. "
            "Go to **Candidate Rankings** to review."
        )


def _handle_analyze(inputs: Dict[str, Any]) -> None:
    warnings = validate_dashboard_inputs(inputs)
    if warnings:
        for w in warnings:
            st.warning(w)
        return

    with st.spinner("Running recruiter intelligence workflow…"):
        try:
            result = run_dashboard_workflow(inputs)
        except DashboardWorkflowError as exc:
            st.error(str(exc))
            return
        except Exception:
            logger.exception("upload_workspace_analysis_failed")
            st.error("Analysis failed unexpectedly. Check files and backend configuration.")
            return

    st.session_state["dashboard_inputs"] = inputs
    set_workflow_result(result)
    st.session_state["workflow_error"] = ""
    st.success("Analysis complete! Navigate to Candidate Rankings to review results.")


if __name__ == "__main__":
    render_upload_workspace()
