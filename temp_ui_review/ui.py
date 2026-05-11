import streamlit as st

from app.state import initialize_session_state


# ---------------------------------------------------------------------------
# Page registry — maps route key → (render_fn_importer, page_title)
# We import lazily to avoid circular imports and keep startup fast.
# ---------------------------------------------------------------------------

_PAGE_REGISTRY = {
    "Dashboard": ("app.pages.dashboard", "render_dashboard"),
    "Upload Workspace": ("app.pages.upload_workspace", "render_upload_workspace"),
    "Candidate Rankings": ("app.pages.rankings", "render_rankings_page"),
    "Candidate Intelligence": ("app.pages.candidate_viewer", "render_candidate_viewer"),
    "Analytics": ("app.pages.analytics", "render_analytics_dashboard"),
    "Override & Audit": ("app.pages.overrides", "render_override_workspace"),
    "Reports & Export": ("app.pages.workflow_export", "render_workflow_export_page"),
    "Comparison": ("app.pages.comparison", "render_comparison_workspace"),
}


def _get_page() -> str:
    return st.session_state.get("_active_page", "Dashboard")


def _set_page(page: str) -> None:
    st.session_state["_active_page"] = page


def render_nav_sidebar() -> None:
    """Render the sidebar with real Streamlit buttons for navigation."""
    from app.styles.theme import apply_theme
    apply_theme()

    nav_items = [
        ("🏠", "Dashboard"),
        ("📤", "Upload Workspace"),
        ("🏆", "Candidate Rankings"),
        ("🔍", "Candidate Intelligence"),
        ("📊", "Analytics"),
        ("✏️", "Override & Audit"),
        ("📁", "Reports & Export"),
        ("⚖️", "Comparison"),
    ]

    active = _get_page()

    with st.sidebar:
        st.markdown(
            """
            <div class="sidebar-brand">
                <div class="brand-mark">AI</div>
                <div>
                    <div class="brand-title">Recruiter OS</div>
                    <div class="brand-subtitle">AI screening workspace</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("**Navigation**")
        for icon, label in nav_items:
            is_active = label == active
            # Use a styled button; active state highlighted via button_type
            btn_label = f"{icon}  {label}"
            if is_active:
                st.markdown(
                    f'<div class="nav-pill active"><div class="nav-icon">{icon}</div>{label}</div>',
                    unsafe_allow_html=True,
                )
            else:
                if st.button(btn_label, key=f"nav_{label}", use_container_width=True):
                    _set_page(label)
                    st.rerun()

        st.markdown(
            """
            <div class="sidebar-footer">
                <div class="sidebar-footer-title">Enterprise-ready demo</div>
                <div class="sidebar-footer-copy">Upload → Analyze → Review → Export</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_ui():
    st.set_page_config(
        page_title="Recruiter Intelligence Platform",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    initialize_session_state()
    render_nav_sidebar()

    page = _get_page()

    # Lazy import + call the right render function
    import importlib
    if page in _PAGE_REGISTRY:
        module_path, fn_name = _PAGE_REGISTRY[page]
        try:
            mod = importlib.import_module(module_path)
            render_fn = getattr(mod, fn_name)
            render_fn()
        except Exception as exc:
            st.error(f"Page '{page}' failed to load: {exc}")
    else:
        st.error(f"Unknown page: {page}")

    return None, "", False


def display_resume_data(resumes_data):
    """
    Display preprocessing and chunk validation data
    """

    st.markdown("---")
    st.header("Resume Processing Debug View")

    for resume in resumes_data:

        st.subheader(f"Candidate: {resume['candidate_name']}")

        # =========================================
        # Structured Candidate Metadata
        # =========================================

        st.write("## Candidate Metadata")

        st.json(resume.get("metadata", {}))

        st.markdown("---")

        # =========================================
        # Hybrid NLP Validation Diagnostics
        # =========================================

        st.write("## NLP Section Validation")

        st.json(resume.get("nlp_validation", {}))

        st.markdown("---")

        # =========================================
        # Cleaned Resume Preview
        # =========================================

        st.write("## Cleaned Resume Preview")

        st.write(resume["resume_text"][:1500])

        st.markdown("---")

        # =========================================
        # Global Chunk Information
        # =========================================

        st.write("## Global Chunk Information")

        st.write(f"Total Global Chunks: {len(resume['chunks'])}")

        for i, chunk in enumerate(resume["chunks"]):

            st.write(f"### Global Chunk {i + 1}")

            st.write(f"Chunk Length: {len(chunk)}")

            st.write(chunk[:500])

            st.markdown("---")

        # =========================================
        # Extracted Resume Sections
        # =========================================

        st.write("## Extracted Resume Sections")

        for section_name, content in resume["sections"].items():

            st.write(f"### {section_name.upper()}")

            st.write(content[:1000])

            st.write(f"Content Length: {len(content)}")

            st.markdown("---")

        # =========================================
        # Section-wise Chunk Validation
        # =========================================

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
