from html import escape
from typing import Any, Dict, List

import streamlit as st


def render_original_ai_output(candidate: Dict[str, Any]) -> None:
    score = _format_score(_score(candidate))
    recommendation = _text(candidate.get("recommendation", "Needs Review"))
    confidence = _format_confidence(candidate)
    reasoning = _reasoning(candidate)

    columns = st.columns(3, gap="small")

    with columns[0]:
        _render_signal_card("Original Score", score, "AI ranking output")

    with columns[1]:
        _render_signal_card("Recommendation", recommendation, "Initial AI guidance")

    with columns[2]:
        _render_signal_card("Confidence", confidence, "Model confidence signal")

    st.markdown(
        f"""
        <div class="evidence-card" style="margin-top:0.85rem;">
            <div class="evidence-meta">Reasoning Summary</div>
            <div class="evidence-text">{escape(reasoning)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_original_vs_override(
    original_candidate: Dict[str, Any],
    final_result: Dict[str, Any],
) -> None:
    rows = build_original_vs_override_rows(original_candidate, final_result)

    st.dataframe(
        rows,
        width="stretch",
        hide_index=True,
        column_order=["Field", "Original AI", "Final Result", "Status"],
    )


def build_original_vs_override_rows(
    original_candidate: Dict[str, Any],
    final_result: Dict[str, Any],
) -> List[Dict[str, str]]:
    fields = [
        ("Score", _format_score(_score(original_candidate)), _format_score(_score(final_result))),
        (
            "Recommendation",
            _text(original_candidate.get("recommendation", "Needs Review")),
            _text(final_result.get("recommendation", "Needs Review")),
        ),
        (
            "Shortlist",
            _text(original_candidate.get("shortlist_status", _shortlist_label(original_candidate))),
            _text(final_result.get("shortlist_status", _shortlist_label(final_result))),
        ),
        (
            "Reviewer Notes",
            _text(original_candidate.get("review_notes", "")) or "None",
            _text(final_result.get("review_notes", "")) or "None",
        ),
    ]

    return [
        {
            "Field": label,
            "Original AI": original,
            "Final Result": final,
            "Status": "Changed" if original != final else "Unchanged",
        }
        for label, original, final in fields
    ]


def _render_signal_card(label: str, value: str, help_text: str) -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{escape(label)}</div>
            <div class="metric-value" style="font-size:1.2rem;">{escape(value)}</div>
            <div class="metric-help">{escape(help_text)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _score(candidate: Dict[str, Any]) -> Any:
    if "final_score" in candidate:
        return candidate.get("final_score")

    return candidate.get("score", 0.0)


def _reasoning(candidate: Dict[str, Any]) -> str:
    for key in ("ranking_reason", "decision_summary", "reasoning_summary", "summary"):
        value = candidate.get(key)

        if value:
            return str(value)

    return "No AI reasoning summary is available for this candidate."


def _shortlist_label(candidate: Dict[str, Any]) -> str:
    if candidate.get("is_shortlisted") is True:
        return "Shortlisted"

    if candidate.get("is_shortlisted") is False:
        return "Not Shortlisted"

    return "No Decision"


def _format_score(value: Any) -> str:
    return f"{float(value or 0.0):.2f}"


def _format_confidence(candidate: Dict[str, Any]) -> str:
    value = candidate.get("confidence", candidate.get("confidence_score", 0.0))
    return f"{float(value or 0.0):.2f}"


def _text(value: Any) -> str:
    return " ".join(str(value or "").strip().split())
