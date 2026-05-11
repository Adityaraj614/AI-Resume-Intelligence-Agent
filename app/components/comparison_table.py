from typing import Any, Dict, List

import streamlit as st


def render_comparison_table(candidate_a: Dict[str, Any], candidate_b: Dict[str, Any]) -> None:
    rows = build_comparison_rows(candidate_a, candidate_b)

    st.dataframe(
        rows,
        width="stretch",
        hide_index=True,
        column_order=["Signal", "Candidate A", "Candidate B", "Advantage"],
    )


def build_comparison_rows(candidate_a: Dict[str, Any], candidate_b: Dict[str, Any]) -> List[Dict[str, str]]:
    numeric_signals = [
        ("Match Score", "final_score"),
        ("Skill Alignment", "semantic_score"),
        ("Experience Relevance", "experience_relevance", "evidence_quality"),
        ("Education Fit", "education_fit"),
        ("Project Relevance", "project_relevance", "retrieval_quality"),
        ("Confidence", "confidence", "confidence_score"),
    ]
    rows = []

    for signal in numeric_signals:
        label = signal[0]
        a_value = _first_number(candidate_a, signal[1:])
        b_value = _first_number(candidate_b, signal[1:])
        rows.append({
            "Signal": label,
            "Candidate A": f"{a_value:.2f}",
            "Candidate B": f"{b_value:.2f}",
            "Advantage": _advantage_label(a_value, b_value),
        })

    rows.extend([
        {
            "Signal": "Recommendation",
            "Candidate A": str(candidate_a.get("recommendation", "")),
            "Candidate B": str(candidate_b.get("recommendation", "")),
            "Advantage": "Review",
        },
        {
            "Signal": "Risk Flags",
            "Candidate A": str(_risk_count(candidate_a)),
            "Candidate B": str(_risk_count(candidate_b)),
            "Advantage": _lower_is_better_label(_risk_count(candidate_a), _risk_count(candidate_b)),
        },
    ])

    return rows


def _first_number(candidate: Dict[str, Any], keys: tuple) -> float:
    for key in keys:
        if key in candidate:
            return float(candidate.get(key, 0.0) or 0.0)

    return 0.0


def _advantage_label(a_value: float, b_value: float) -> str:
    if a_value == b_value:
        return "Tie"

    return "Candidate A" if a_value > b_value else "Candidate B"


def _lower_is_better_label(a_value: int, b_value: int) -> str:
    if a_value == b_value:
        return "Tie"

    return "Candidate A" if a_value < b_value else "Candidate B"


def _risk_count(candidate: Dict[str, Any]) -> int:
    flags = candidate.get("risk_flags", candidate.get("warning_flags", []))

    if not isinstance(flags, list):
        return 0

    return len(flags)
