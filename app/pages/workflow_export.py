from typing import Any, Dict, List

import streamlit as st

from app.components.export_buttons import render_export_buttons
from app.components.export_preview import render_export_preview
from app.components.recruiter_decisions import render_recruiter_decisions
from app.components.session_overview import build_session_metrics, render_session_overview
from app.components.workflow_summary import render_workflow_completion_summary
from app.state import (
    get_override_history,
    get_ranked_candidates,
    get_workflow_result,
    initialize_session_state,
)
from app.styles.theme import render_panel_end, render_panel_heading, render_panel_start


def render_workflow_export_page() -> None:
    initialize_session_state()

    workflow_result = resolve_workflow_result()
    ranked_candidates = resolve_ranked_candidates(workflow_result)
    override_history = resolve_override_history()
    final_candidates = resolve_final_candidates(ranked_candidates)
    session_summary = build_export_session_summary(workflow_result, final_candidates, override_history)

    st.markdown(
        """
        <div class="page-heading">
            <div class="eyebrow">Reports workspace</div>
            <h1>Reports & Export</h1>
            <p>Close the recruiter review session with final recommendations, export-ready outputs, and a concise workflow handoff.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not final_candidates:
        render_empty_export_state()
        return

    render_panel_start()
    render_panel_heading(
        "Workflow Session Overview",
        "High-level workflow context for the current hiring review session.",
    )
    render_session_overview(workflow_result, final_candidates, override_history)
    render_panel_end()

    render_panel_start()
    render_panel_heading(
        "Recruiter Decision Summary",
        "Deterministic summaries from workflow outputs, final candidates, and override history.",
    )
    render_recruiter_decisions(workflow_result, final_candidates, override_history)
    render_panel_end()

    render_panel_start()
    render_panel_heading(
        "Export Preview",
        "Compact preview of final recruiter-facing candidate rows.",
    )
    render_export_preview(final_candidates, override_history)
    render_panel_end()

    render_panel_start()
    render_panel_heading(
        "Export Actions",
        "Download final workflow outputs for hiring review handoff.",
    )
    render_export_buttons(workflow_result, final_candidates, override_history, session_summary)
    render_panel_end()

    render_panel_start()
    render_panel_heading(
        "Workflow Completion Summary",
        "Finalize the review session after confirming exports are ready.",
    )
    render_workflow_completion_summary(workflow_result, final_candidates, override_history)
    render_panel_end()


def resolve_workflow_result() -> Dict[str, Any]:
    return get_workflow_result()


def resolve_ranked_candidates(workflow_result: Dict[str, Any]) -> List[Dict[str, Any]]:
    return _ordered_candidates(get_ranked_candidates(final=False))


def resolve_override_history() -> List[Dict[str, Any]]:
    return get_override_history()


def resolve_final_candidates(ranked_candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return _ordered_candidates(get_ranked_candidates(final=True))


def build_export_session_summary(
    workflow_result: Dict[str, Any],
    final_candidates: List[Dict[str, Any]],
    override_history: List[Dict[str, Any]],
) -> Dict[str, Any]:
    metadata = workflow_result.get("workflow_metadata", {}) if isinstance(workflow_result, dict) else {}
    metrics = build_session_metrics(metadata, final_candidates, override_history)

    return {
        "workflow_id": metadata.get("workflow_id", "current_session"),
        "execution_timestamp": metadata.get("execution_timestamp", "not_provided"),
        "metrics": metrics,
        "top_candidate": _candidate_name(final_candidates[0]) if final_candidates else "",
        "export_row_count": len(final_candidates),
        "override_count": len(override_history),
        "completion_status": "completed" if st.session_state.get("workflow_export_completed") else "ready",
    }


def render_empty_export_state() -> None:
    render_panel_start()
    render_panel_heading(
        "Workflow Export Not Ready",
        "Run the recruiter workflow before exporting final hiring review outputs.",
    )
    st.info(
        "This page consumes existing ranked candidates, overrides, analytics, and workflow metadata. "
        "It does not fabricate recommendations or rerun pipeline steps."
    )
    if st.button("Go to Upload Workspace", type="primary"):
        st.session_state["_active_page"] = "Upload Workspace"
        st.rerun()
    render_panel_end()


def _ordered_candidates(candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return sorted(
        candidates,
        key=lambda candidate: (
            int(candidate.get("rank", candidate.get("ranking_position", 9999)) or 9999),
            str(candidate.get("candidate_name", candidate.get("name", ""))).lower(),
            str(candidate.get("candidate_id", "")),
        ),
    )


def _candidate_name(candidate: Dict[str, Any]) -> str:
    return str(candidate.get("candidate_name", candidate.get("name", candidate.get("candidate_id", "Unknown"))))


if __name__ == "__main__":
    render_workflow_export_page()
