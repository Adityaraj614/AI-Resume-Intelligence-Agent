import logging
from typing import Any, Dict

import streamlit as st

from app.components.upload_widget import render_upload_section, validate_dashboard_inputs
from app.pages.dashboard import run_dashboard_analysis
from app.state import get_workflow_result, initialize_session_state, set_workflow_result
from app.styles.theme import render_panel_end, render_panel_heading, render_panel_start
from core.workflow.dashboard_workflow import DashboardWorkflowError


logger = logging.getLogger(__name__)


def render_upload_workspace() -> None:
    initialize_session_state()

    st.markdown(
        """
        <div class="page-heading">
            <div class="eyebrow">AI intake workspace</div>
            <h1>Upload Workspace</h1>
            <p>Upload a job description, resume PDFs, and structured LinkedIn JSON profiles, then run the recruiter intelligence workflow.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    _render_workflow_progress()

    render_panel_start()
    render_panel_heading(
        "Job Description & Candidate Sources",
        "The backend workflow remains the single source of truth for parsing, retrieval, scoring, ranking, analytics, and exports.",
    )
    inputs = render_upload_section()
    _render_upload_readiness(inputs)
    render_panel_end()

    left, right = st.columns([0.68, 0.32], gap="large")

    with left:
        st.markdown(
            """
            <div class="guidance-note">
                After analysis, continue to Candidate Rankings to review fit, compare candidates, inspect evidence, and export reports.
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        analyze_button = st.button("Analyze Candidates", type="primary", width="stretch")

    if analyze_button:
        _handle_analyze(inputs)

    _render_previous_run_status()


def _render_workflow_progress() -> None:
    workflow_result = get_workflow_result()
    analyzed_class = "complete" if workflow_result else ""

    st.markdown(
        f"""
        <div class="workflow-steps">
            <div class="workflow-step active"><span>1</span>Upload</div>
            <div class="workflow-step active"><span>2</span>Analyze</div>
            <div class="workflow-step {analyzed_class}"><span>3</span>Review</div>
            <div class="workflow-step {analyzed_class}"><span>4</span>Export</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _handle_analyze(inputs: Dict[str, Any]) -> None:
    warnings = validate_dashboard_inputs(inputs)

    if warnings:
        for warning in warnings:
            st.warning(warning)
        return

    progress = st.progress(0, text="Preparing recruiter workflow...")

    with st.spinner("Running recruiter intelligence workflow..."):
        try:
            progress.progress(15, text="Parsing job description and candidate files...")
            progress.progress(35, text="Generating embeddings and retrieval context...")
            progress.progress(55, text="Evaluating candidate fit against the role...")
            progress.progress(75, text="Building recruiter rankings and analytics...")
            workflow_result = run_dashboard_analysis(inputs)
            progress.progress(100, text="Recruiter workflow complete.")
        except DashboardWorkflowError as exc:
            logger.warning("upload_workspace_analysis_failed", exc_info=True)
            st.session_state["workflow_error"] = str(exc)
            st.error(str(exc))
            return
        except Exception:
            logger.exception("upload_workspace_unexpected_failure")
            st.session_state["workflow_error"] = (
                "Candidate analysis failed unexpectedly. Check uploaded files and backend configuration."
            )
            st.error(st.session_state["workflow_error"])
            return

    st.session_state["dashboard_inputs"] = inputs
    set_workflow_result(workflow_result)
    st.session_state["workflow_error"] = ""
    st.success("Analysis complete. Candidate Rankings, Analytics, Reports, Comparison, and Overrides are ready.")

    if st.button("Continue to Candidate Rankings", width="stretch"):
        st.session_state["_active_page"] = "Candidate Rankings"
        st.rerun()


def _render_upload_readiness(inputs: Dict[str, Any]) -> None:
    job_description = str(inputs.get("job_description", "")).strip()
    jd_file = inputs.get("jd_file")
    resume_count = len(inputs.get("resume_files", []) or [])
    linkedin_count = len(inputs.get("linkedin_files", []) or [])
    has_role_context = bool(job_description or jd_file)
    has_candidates = bool(resume_count or linkedin_count)
    ready = has_role_context and has_candidates

    if ready:
        title = "Ready to analyze"
        copy = (
            f"Role context is loaded with {resume_count} resume file(s) and "
            f"{linkedin_count} LinkedIn profile(s). Run analysis to unlock rankings and reports."
        )
    else:
        title = "Add role context and candidate files"
        copy = (
            "Accepted inputs: JD text or TXT/MD/PDF files, resume PDFs, and structured LinkedIn JSON. "
            "The workflow will parse, retrieve, score, rank, and prepare recruiter outputs after analysis."
        )

    st.markdown(
        f"""
        <div class="readiness-card">
            <div class="readiness-title">{title}</div>
            <div class="readiness-copy">{copy}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_previous_run_status() -> None:
    workflow_result = get_workflow_result()

    if not workflow_result:
        return

    outputs = workflow_result.get("workflow_outputs", {}) if isinstance(workflow_result, dict) else {}
    ranked_candidates = outputs.get("ranked_candidates", [])
    candidate_count = len(ranked_candidates) if isinstance(ranked_candidates, list) else 0

    render_panel_start()
    render_panel_heading(
        "Latest Workflow Run",
        "Your current session has analysis outputs ready for recruiter review.",
    )
    st.success(f"{candidate_count} candidate(s) processed. Continue to Candidate Rankings or Reports.")

    col_rankings, col_reports = st.columns(2, gap="small")

    with col_rankings:
        if st.button("Open Rankings", width="stretch"):
            st.session_state["_active_page"] = "Candidate Rankings"
            st.rerun()

    with col_reports:
        if st.button("Open Reports", width="stretch"):
            st.session_state["_active_page"] = "Reports"
            st.rerun()

    render_panel_end()
