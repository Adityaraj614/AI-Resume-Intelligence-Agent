from html import escape
from typing import Any, Dict, List

import streamlit as st


def render_candidate_snapshot(candidate: Dict[str, Any], label: str) -> None:
    strengths = _top_strengths(candidate)
    strengths_html = "".join(f'<span class="status-badge">{escape(strength)}</span>' for strength in strengths)

    st.markdown(
        f"""
        <div class="snapshot-card">
            <div class="comparison-label">{escape(str(label))}</div>
            <div class="snapshot-name">{escape(str(candidate.get("candidate_name", candidate.get("candidate_id", "Unknown"))))}</div>
            <div class="snapshot-subtitle">Source: {escape(str(candidate.get("source", "resume")))} · ID: {escape(str(candidate.get("candidate_id", "unknown")))}</div>
            <div style="margin-bottom:0.5rem;">
                <span class="status-badge">{escape(str(candidate.get("recommendation", "Needs Review")))}</span>
            </div>
            <div style="color:#111827;font-size:0.92rem;line-height:1.5;">
                Score <strong>{_score(candidate):.2f}</strong> · Confidence <strong>{_confidence(candidate):.2f}</strong>
            </div>
            <div style="margin-top:0.75rem;">{strengths_html or '<span class="status-badge">No strengths listed</span>'}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _top_strengths(candidate: Dict[str, Any]) -> List[str]:
    strengths = candidate.get("strengths", [])

    if not strengths:
        strengths = candidate.get("skills", candidate.get("extracted_skills", []))

    if not isinstance(strengths, list):
        strengths = [strengths]

    return [str(item).strip() for item in strengths if str(item).strip()][:3]


def _score(candidate: Dict[str, Any]) -> float:
    return float(candidate.get("final_score", 0.0) or 0.0)


def _confidence(candidate: Dict[str, Any]) -> float:
    return float(candidate.get("confidence", candidate.get("confidence_score", 0.0)) or 0.0)
