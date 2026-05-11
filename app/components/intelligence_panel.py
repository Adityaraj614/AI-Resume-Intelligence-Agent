from html import escape
from typing import Any, Dict, List

import streamlit as st


def render_intelligence_panel(candidate: Dict[str, Any]) -> None:
    recommendation = candidate.get("recommendation", "Needs Review")
    summary = _candidate_summary(candidate)
    reasoning = candidate.get("ranking_reason", candidate.get("decision_summary", ""))
    confidence_text = _confidence_assessment(candidate)
    risk_flags = _risk_flags(candidate)

    st.markdown(
        f"""
            <div class="info-card">
            <div class="dashboard-panel-title">AI Intelligence Summary</div>
            <div class="dashboard-panel-subtitle">Explainable recommendation based on existing retrieval, scoring, and safety signals.</div>
            <div style="color:#111827;font-weight:700;margin-bottom:0.45rem;">{escape(str(recommendation))}</div>
            <div style="color:#111827;font-size:0.94rem;line-height:1.5;margin-bottom:0.85rem;">{escape(str(summary))}</div>
            <div style="color:#6B7280;font-size:0.9rem;line-height:1.5;margin-bottom:0.85rem;">{escape(str(reasoning or "No ranking reason available yet."))}</div>
            <div style="color:#111827;font-size:0.9rem;font-weight:650;margin-bottom:0.45rem;">{escape(str(confidence_text))}</div>
            {_render_risk_badges(risk_flags)}
        </div>
        """,
        unsafe_allow_html=True,
    )


def _candidate_summary(candidate: Dict[str, Any]) -> str:
    if candidate.get("decision_summary"):
        return str(candidate["decision_summary"])

    name = candidate.get("candidate_name", candidate.get("candidate_id", "This candidate"))
    recommendation = candidate.get("recommendation", "requires recruiter review")

    return (
        f"{name} is currently marked as {recommendation}. Review the evidence below "
        "to confirm semantic alignment and recruiter fit."
    )


def _confidence_assessment(candidate: Dict[str, Any]) -> str:
    confidence = float(candidate.get("confidence", candidate.get("confidence_score", 0.0)) or 0.0)

    if confidence >= 0.8:
        label = "High confidence"
    elif confidence >= 0.5:
        label = "Moderate confidence"
    else:
        label = "Low confidence"

    return f"Confidence assessment: {label} ({confidence:.2f})"


def _risk_flags(candidate: Dict[str, Any]) -> List[str]:
    flags = candidate.get("risk_flags", candidate.get("warning_flags", []))

    if not isinstance(flags, list):
        return []

    return [str(flag).replace("_", " ").title() for flag in flags if str(flag).strip()]


def _render_risk_badges(risk_flags: List[str]) -> str:
    if not risk_flags:
        return '<span class="status-badge">No active risk flags</span>'

    return "".join(f'<span class="risk-badge">{escape(flag)}</span>' for flag in risk_flags)
