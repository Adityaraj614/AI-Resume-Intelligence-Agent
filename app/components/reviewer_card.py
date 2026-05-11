from html import escape
from typing import Any, Dict

import streamlit as st


def render_reviewer_card(reviewer_name: str, latest_entry: Dict[str, Any] = None) -> None:
    latest_entry = latest_entry or {}
    reviewer = latest_entry.get("reviewer", {}) if isinstance(latest_entry, dict) else {}
    display_name = reviewer.get("reviewer_name") or reviewer_name or "No reviewer recorded"
    timestamp = latest_entry.get("timestamp", "No override submitted")

    st.markdown(
        f"""
        <div class="info-card">
            <div class="comparison-label">Reviewer</div>
            <div style="color:#111827;font-size:1.05rem;font-weight:750;line-height:1.25;">
                {escape(str(display_name))}
            </div>
            <div class="candidate-meta" style="margin-top:0.35rem;">
                Latest review: {escape(str(timestamp))}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
