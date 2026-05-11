from html import escape
from typing import Any, Dict, List

import streamlit as st

from app.components.evidence_panel import extract_evidence_items


def render_comparison_evidence(candidate_a: Dict[str, Any], candidate_b: Dict[str, Any]) -> None:
    left, right = st.columns(2, gap="large")

    with left:
        _render_candidate_evidence("Candidate A Evidence", candidate_a)

    with right:
        _render_candidate_evidence("Candidate B Evidence", candidate_b)


def _render_candidate_evidence(title: str, candidate: Dict[str, Any]) -> None:
    st.markdown(f'<div class="comparison-label">{escape(title)}</div>', unsafe_allow_html=True)
    evidence_items = extract_evidence_items(candidate)[:4]

    if not evidence_items:
        st.info("No retrieval evidence attached yet.")
        return

    for item in evidence_items:
        _render_item(item)


def _render_item(item: Dict[str, Any]) -> None:
    score = f" · score {item['score']}" if item.get("score") else ""
    st.markdown(
        f"""
        <div class="evidence-card">
            <div class="evidence-meta">{escape(str(item.get("section", "Evidence")))} · {escape(str(item.get("source", "retrieval")))}{escape(score)}</div>
            <div class="evidence-text">{escape(str(item.get("text", "")))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
