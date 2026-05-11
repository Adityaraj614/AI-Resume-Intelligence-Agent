import streamlit as st

from app.state import has_workflow, initialize_session_state
from app.styles.theme import render_panel_end, render_panel_heading, render_panel_start


def render_settings_page() -> None:
    initialize_session_state()

    st.markdown(
        """
        <div class="page-heading">
            <div class="eyebrow">Workspace settings</div>
            <h1>Settings</h1>
            <p>Review UI workflow status and environment guidance without changing backend configuration.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_panel_start()
    render_panel_heading(
        "Recruiter Workflow",
        "This page is UI-only and does not modify orchestration, ranking, retrieval, scoring, or analytics systems.",
    )
    status = "Ready for review" if has_workflow() else "Awaiting analysis"
    st.info(f"Current workflow status: {status}")

    if st.button("Go to Upload Workspace", type="primary"):
        st.session_state["_active_page"] = "Upload Workspace"
        st.rerun()

    render_panel_end()
