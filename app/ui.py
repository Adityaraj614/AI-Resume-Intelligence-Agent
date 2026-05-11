import importlib
from typing import Callable, Dict, Tuple

import streamlit as st

from app.state import has_workflow, initialize_session_state
from app.styles.theme import apply_theme, render_top_navbar


PAGE_REGISTRY: Dict[str, Tuple[str, str]] = {
    "Dashboard": ("app.pages.dashboard", "render_dashboard"),
    "Upload Workspace": ("app.pages.upload_workspace", "render_upload_workspace"),
    "Candidate Rankings": ("app.pages.rankings", "render_rankings_page"),
    "Candidate Intelligence": ("app.pages.candidate_viewer", "render_candidate_viewer"),
    "Analytics": ("app.pages.analytics", "render_analytics_dashboard"),
    "Reports": ("app.pages.workflow_export", "render_workflow_export_page"),
    "Comparison": ("app.pages.comparison", "render_comparison_workspace"),
    "Override & Audit": ("app.pages.overrides", "render_override_workspace"),
    "Settings": ("app.pages.settings", "render_settings_page"),
}


NAV_ITEMS = (
    ("Dashboard", False),
    ("Upload Workspace", False),
    ("Candidate Rankings", True),
    ("Candidate Intelligence", True),
    ("Analytics", True),
    ("Reports", True),
    ("Comparison", True),
    ("Override & Audit", True),
    ("Settings", False),
)


def render_ui():
    st.set_page_config(
        page_title="Recruiter Intelligence Platform",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    initialize_session_state()
    st.session_state.setdefault("_active_page", "Dashboard")

    apply_theme()
    render_nav_sidebar()
    render_top_navbar()
    _render_active_page()
    return None, "", False


def render_nav_sidebar() -> None:
    active_page = get_active_page()
    workflow_ready = has_workflow()

    with st.sidebar:
        st.markdown(
            """
            <div class="sidebar-brand">
                <div class="brand-mark">AI</div>
                <div>
                    <div class="brand-title">Recruiter OS</div>
                    <div class="brand-subtitle">Upload -> Analyze -> Review -> Export</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        for label, requires_workflow in NAV_ITEMS:
            disabled = requires_workflow and not workflow_ready
            is_active = label == active_page

            if is_active:
                st.markdown(
                    f"""
                    <div class="nav-pill active">
                        <div>{label}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                continue

            if st.button(
                label,
                key=f"nav_{label}",
                width="stretch",
                disabled=disabled,
            ):
                set_active_page(label)
                st.rerun()

        st.markdown(
            """
            <div class="sidebar-footer">
                <div class="sidebar-footer-title">Workflow Status</div>
                <div class="sidebar-footer-copy">Run analysis to unlock rankings, intelligence, analytics, comparison, overrides, and reports.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def get_active_page() -> str:
    page = st.session_state.get("_active_page", "Dashboard")
    return page if page in PAGE_REGISTRY else "Dashboard"


def set_active_page(page: str) -> None:
    if page in PAGE_REGISTRY:
        st.session_state["_active_page"] = page


def navigate_to(page: str) -> None:
    set_active_page(page)
    st.rerun()


def _render_active_page() -> None:
    page = get_active_page()
    render_fn = _load_page(page)
    render_fn()


def _load_page(page: str) -> Callable[[], None]:
    module_path, function_name = PAGE_REGISTRY[page]
    module = importlib.import_module(module_path)
    return getattr(module, function_name)


def display_resume_data(resumes_data):
    """
    Display preprocessing and chunk validation data.
    """

    st.markdown("---")
    st.header("Resume Processing Debug View")

    for resume in resumes_data:
        st.subheader(f"Candidate: {resume['candidate_name']}")
        st.write("## Candidate Metadata")
        st.json(resume.get("metadata", {}))
        st.markdown("---")
        st.write("## NLP Section Validation")
        st.json(resume.get("nlp_validation", {}))
        st.markdown("---")
        st.write("## Cleaned Resume Preview")
        st.write(resume["resume_text"][:1500])
        st.markdown("---")
        st.write("## Global Chunk Information")
        st.write(f"Total Global Chunks: {len(resume['chunks'])}")

        for i, chunk in enumerate(resume["chunks"]):
            st.write(f"### Global Chunk {i + 1}")
            st.write(f"Chunk Length: {len(chunk)}")
            st.write(chunk[:500])
            st.markdown("---")

        st.write("## Extracted Resume Sections")

        for section_name, content in resume["sections"].items():
            st.write(f"### {section_name.upper()}")
            st.write(content[:1000])
            st.write(f"Content Length: {len(content)}")
            st.markdown("---")

        st.write("## Section-wise Chunks")

        for section_name, chunks in resume["section_chunks"].items():
            st.write(f"### {section_name.upper()} Chunks")
            st.write(f"Total Chunks: {len(chunks)}")

            for i, chunk in enumerate(chunks):
                st.write(f"Chunk {i + 1}")
                st.write(f"Chunk Length: {len(chunk)}")
                st.write(chunk[:500])
                st.markdown("---")

        st.markdown("====================================")
