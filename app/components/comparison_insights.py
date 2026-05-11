from typing import Any, Dict, List

import streamlit as st


def render_comparison_insights(candidate_a: Dict[str, Any], candidate_b: Dict[str, Any]) -> None:
    insights = build_comparison_insights(candidate_a, candidate_b)

    for insight in insights:
        st.markdown(f'<div class="insight-card">{insight}</div>', unsafe_allow_html=True)


def build_comparison_insights(candidate_a: Dict[str, Any], candidate_b: Dict[str, Any]) -> List[str]:
    insights = []
    score_delta = _number(candidate_a, "final_score") - _number(candidate_b, "final_score")
    semantic_delta = _number(candidate_a, "semantic_score") - _number(candidate_b, "semantic_score")
    confidence_delta = _confidence(candidate_a) - _confidence(candidate_b)
    evidence_delta = _number(candidate_a, "evidence_quality") - _number(candidate_b, "evidence_quality")

    if score_delta > 0:
        insights.append(
            f"Candidate A ranks higher by {abs(score_delta):.2f} match-score points based on the existing ranking output."
        )
    elif score_delta < 0:
        insights.append(
            f"Candidate B ranks higher by {abs(score_delta):.2f} match-score points based on the existing ranking output."
        )
    else:
        insights.append("Both candidates have the same match score in the current ranking output.")

    insights.append(_delta_sentence("semantic alignment", semantic_delta))
    insights.append(_delta_sentence("evidence quality", evidence_delta))
    insights.append(_delta_sentence("confidence", confidence_delta))

    risk_a = _risk_count(candidate_a)
    risk_b = _risk_count(candidate_b)

    if risk_a != risk_b:
        lower_risk = "Candidate A" if risk_a < risk_b else "Candidate B"
        insights.append(f"{lower_risk} has fewer visible risk flags for recruiter review.")
    else:
        insights.append("Both candidates show the same visible risk-flag count.")

    return insights


def _delta_sentence(label: str, delta: float) -> str:
    if delta > 0:
        return f"Candidate A shows stronger {label} in the available candidate signals."

    if delta < 0:
        return f"Candidate B shows stronger {label} in the available candidate signals."

    return f"Both candidates show similar {label} in the available candidate signals."


def _number(candidate: Dict[str, Any], key: str) -> float:
    return float(candidate.get(key, 0.0) or 0.0)


def _confidence(candidate: Dict[str, Any]) -> float:
    return float(candidate.get("confidence", candidate.get("confidence_score", 0.0)) or 0.0)


def _risk_count(candidate: Dict[str, Any]) -> int:
    flags = candidate.get("risk_flags", candidate.get("warning_flags", []))

    if not isinstance(flags, list):
        return 0

    return len(flags)
