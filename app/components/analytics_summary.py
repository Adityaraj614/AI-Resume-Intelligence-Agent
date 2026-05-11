from html import escape
from typing import Any, Dict, List

import streamlit as st

from core.analytics.insight_generator import generate_recruiter_insights_from_analytics


def render_analytics_summary(analytics_report: Dict[str, Any]) -> None:
    insights = build_recruiter_insights(analytics_report)
    st.markdown(
        """
        <div class="dashboard-panel-title">Recruiter Summary Insights</div>
        <div class="dashboard-panel-subtitle">Deterministic summaries from current workflow outputs.</div>
        """,
        unsafe_allow_html=True,
    )

    if not insights:
        st.info("No analytics insights available yet.")
    else:
        for insight in insights:
            st.markdown(f'<div class="insight-card">{escape(insight)}</div>', unsafe_allow_html=True)


def build_recruiter_insights(analytics_report: Dict[str, Any]) -> List[str]:
    if not analytics_report:
        return []

    existing = analytics_report.get("recruiter_insights", [])

    if isinstance(existing, list) and existing:
        return [str(insight) for insight in existing if str(insight).strip()]

    return generate_recruiter_insights_from_analytics(analytics_report)
