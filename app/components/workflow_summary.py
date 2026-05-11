from html import escape
from typing import Any, Dict, List

import streamlit as st


def render_workflow_completion_summary(
    workflow_result: Dict[str, Any],
    final_candidates: List[Dict[str, Any]],
    override_history: List[Dict[str, Any]],
) -> None:
    completed = bool(st.session_state.get("workflow_export_completed"))
    status = "Completed" if completed else "Ready to Finalize"
    summary = build_completion_summary(workflow_result, final_candidates, override_history, completed)

    st.markdown(
        f"""
        <div class="info-card">
            <div class="comparison-label">Workflow Status</div>
            <div style="color:#111827;font-size:1.3rem;font-weight:760;line-height:1.2;">
                {escape(status)}
            </div>
            <div style="color:#6B7280;font-size:0.92rem;line-height:1.5;margin-top:0.65rem;">
                {escape(summary)}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    _, button_col = st.columns([0.66, 0.34])

    with button_col:
        if st.button("Finalize Hiring Review Session", type="primary", width="stretch"):
            st.session_state["workflow_export_completed"] = True
            st.rerun()


def build_completion_summary(
    workflow_result: Dict[str, Any],
    final_candidates: List[Dict[str, Any]],
    override_history: List[Dict[str, Any]],
    completed: bool = False,
) -> str:
    metadata = workflow_result.get("workflow_metadata", {}) if isinstance(workflow_result, dict) else {}
    workflow_id = metadata.get("workflow_id", "current workflow")

    if completed:
        return (
            f"Recruiter review session {workflow_id} is finalized. "
            f"{len(final_candidates)} ranked candidates and {len(override_history)} override events are export-ready."
        )

    return (
        f"Recruiter review session {workflow_id} is ready for closure. "
        f"{len(final_candidates)} ranked candidates and {len(override_history)} override events can be exported."
    )
