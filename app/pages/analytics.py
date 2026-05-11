import streamlit as st

from app.components.analytics_cards import render_analytics_cards
from app.components.analytics_summary import render_analytics_summary
from app.components.charts import (
    bucket_distribution_from_analytics,
    confidence_distribution_from_analytics,
    evidence_distribution_from_analytics,
    render_bar_distribution,
    score_distribution_from_analytics,
)
from app.components.dashboard_analytics import render_dashboard_analytics
from app.components.skill_distribution import render_skill_distribution_from_analytics
from app.state import get_analytics, get_workflow_result, initialize_session_state
from app.styles.theme import render_panel_end, render_panel_heading, render_panel_start


def render_analytics_dashboard() -> None:
    initialize_session_state()
    analytics_report = get_analytics()
    workflow_result = get_workflow_result()

    st.markdown(
        """
        <div class="page-heading">
            <div class="eyebrow">Analytics workspace</div>
            <h1>Recruiter Analytics</h1>
            <p>Explore hiring funnel health, score distribution, skill insights, confidence, evidence quality, and workflow trends.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not workflow_result:
        render_empty_analytics_state()
        return

    render_panel_start()
    render_panel_heading(
        "Hiring Analytics",
        "Dedicated analytics panels for score distribution, JD fit, funnel progress, and skills.",
    )
    render_dashboard_analytics(workflow_result)
    render_panel_end()

    render_panel_start()
    render_panel_heading(
        "Recruiter Metrics",
        "Backend analytics from the current candidate pool.",
    )
    render_analytics_cards(analytics_report)
    render_panel_end()

    left, right = st.columns(2, gap="large")

    with left:
        render_bar_distribution(
            "Score Distribution",
            score_distribution_from_analytics(analytics_report),
        )

    with right:
        render_bar_distribution(
            "Confidence Distribution",
            confidence_distribution_from_analytics(analytics_report),
        )

    left, right = st.columns([0.58, 0.42], gap="large")

    with left:
        render_skill_distribution_from_analytics(analytics_report)

    with right:
        render_bar_distribution(
            "Evidence Distribution",
            evidence_distribution_from_analytics(analytics_report),
        )

    render_bar_distribution(
        "Bucket Distribution",
        bucket_distribution_from_analytics(analytics_report),
    )

    render_analytics_summary(analytics_report)


def render_empty_analytics_state() -> None:
    render_panel_start()
    render_panel_heading(
        "Analytics Not Ready",
        "Run analysis from Upload Workspace before opening the analytics dashboard.",
    )
    st.info("Analytics uses existing workflow outputs only. No mock analytics are generated.")

    if st.button("Go to Upload Workspace", type="primary"):
        st.session_state["_active_page"] = "Upload Workspace"
        st.rerun()

    render_panel_end()


if __name__ == "__main__":
    render_analytics_dashboard()
