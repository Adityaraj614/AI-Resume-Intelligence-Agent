from typing import Any, Dict

import streamlit as st


RECOMMENDATION_OPTIONS = [
    "Strong Match",
    "Interview",
    "Consider",
    "Hold for Review",
    "Not Recommended",
    "Needs Review",
]

SHORTLIST_OPTIONS = [
    "No Decision",
    "Shortlisted",
    "Include",
    "Hold",
    "Exclude",
]


def render_override_controls(candidate: Dict[str, Any], current_result: Dict[str, Any]) -> Dict[str, Any]:
    current_score = _score(current_result)
    current_recommendation = _text(current_result.get("recommendation", "Needs Review"))
    current_shortlist = _text(
        current_result.get("shortlist_status", _shortlist_label(current_result))
    )
    current_notes = _text(current_result.get("review_notes", ""))

    with st.form("override_controls_form", clear_on_submit=False):
        left, right = st.columns([0.5, 0.5], gap="large")

        with left:
            reviewer_name = st.text_input(
                "Reviewer",
                value=st.session_state.get("override_reviewer_name", ""),
                placeholder="Recruiter name",
            )
            score_override = st.number_input(
                "Score Override",
                min_value=0.0,
                max_value=100.0,
                value=float(current_score),
                step=0.5,
            )
            recommendation_override = st.selectbox(
                "Recommendation Override",
                _options_with_current(RECOMMENDATION_OPTIONS, current_recommendation),
                index=0,
            )

        with right:
            shortlist_override = st.selectbox(
                "Shortlist Override",
                _options_with_current(SHORTLIST_OPTIONS, current_shortlist),
                index=0,
            )
            override_reason = st.text_area(
                "Override Reason",
                value="",
                height=92,
                placeholder="Briefly explain the recruiter review reason.",
            )
            recruiter_notes = st.text_area(
                "Recruiter Notes",
                value=current_notes,
                height=92,
                placeholder="Optional profile review notes.",
            )

        submitted = st.form_submit_button("Apply Recruiter Override", type="primary")

    if submitted:
        st.session_state["override_reviewer_name"] = reviewer_name

    return {
        "submitted": submitted,
        "candidate_id": candidate.get("candidate_id", ""),
        "reviewer_name": reviewer_name,
        "score_override": score_override,
        "recommendation_override": recommendation_override,
        "shortlist_override": shortlist_override,
        "recruiter_notes": recruiter_notes,
        "override_reason": override_reason,
    }


def _options_with_current(options: list, current_value: str) -> list:
    cleaned = [_text(option) for option in options if _text(option)]
    current = _text(current_value)

    if current and current not in cleaned:
        return [current, *cleaned]

    if current in cleaned:
        return [current, *[option for option in cleaned if option != current]]

    return cleaned


def _score(candidate: Dict[str, Any]) -> float:
    if "final_score" in candidate:
        return float(candidate.get("final_score", 0.0) or 0.0)

    return float(candidate.get("score", 0.0) or 0.0)


def _shortlist_label(candidate: Dict[str, Any]) -> str:
    if candidate.get("is_shortlisted") is True:
        return "Shortlisted"

    if candidate.get("is_shortlisted") is False:
        return "No Decision"

    return "No Decision"


def _text(value: Any) -> str:
    return " ".join(str(value or "").strip().split())
