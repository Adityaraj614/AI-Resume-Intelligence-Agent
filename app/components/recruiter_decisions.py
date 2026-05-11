from html import escape
from typing import Any, Dict, List

import streamlit as st


def render_recruiter_decisions(
    workflow_result: Dict[str, Any],
    final_candidates: List[Dict[str, Any]],
    override_history: List[Dict[str, Any]],
) -> None:
    summaries = build_decision_summary_lines(workflow_result, final_candidates, override_history)

    if not summaries:
        st.info("No recruiter decision summary is available yet.")
        return

    for summary in summaries:
        st.markdown(
            f"""
            <div class="insight-card">
                {escape(summary)}
            </div>
            """,
            unsafe_allow_html=True,
        )


def build_decision_summary_lines(
    workflow_result: Dict[str, Any],
    final_candidates: List[Dict[str, Any]],
    override_history: List[Dict[str, Any]],
) -> List[str]:
    if not final_candidates:
        return []

    outputs = workflow_result.get("workflow_outputs", {}) if isinstance(workflow_result, dict) else {}
    workflow_summary = _clean_text(workflow_result.get("workflow_summary", ""))
    top_candidate = final_candidates[0]
    lines = []

    if workflow_summary:
        lines.append(workflow_summary)

    lines.append(
        f"Top candidate: {_candidate_name(top_candidate)} with final score {_score(top_candidate):.2f} and recommendation {_clean_text(top_candidate.get('recommendation', 'Needs Review'))}."
    )

    shortlist = outputs.get("shortlist", [])
    shortlist_count = len(shortlist) if isinstance(shortlist, list) else _shortlisted_count(final_candidates)

    if shortlist_count:
        lines.append(f"{shortlist_count} candidates are available in the shortlist for hiring review.")
    else:
        lines.append("No candidates are currently marked as shortlisted.")

    if override_history:
        affected_candidates = sorted({
            _clean_text(entry.get("candidate_id"))
            for entry in override_history
            if isinstance(entry, dict) and entry.get("candidate_id")
        })
        lines.append(
            f"{len(override_history)} recruiter override events were recorded across {len(affected_candidates)} candidates."
        )

    decision_support = outputs.get("decision_support", {})
    prioritized = decision_support.get("prioritized_interviews", []) if isinstance(decision_support, dict) else []

    if prioritized:
        lines.append(f"{len(prioritized)} priority interview recommendations are included in decision support outputs.")

    return lines


def _candidate_name(candidate: Dict[str, Any]) -> str:
    return _clean_text(candidate.get("candidate_name", candidate.get("name", candidate.get("candidate_id", "Unknown Candidate"))))


def _score(candidate: Dict[str, Any]) -> float:
    return float(candidate.get("final_score", candidate.get("score", 0.0)) or 0.0)


def _shortlisted_count(candidates: List[Dict[str, Any]]) -> int:
    return len([
        candidate
        for candidate in candidates
        if candidate.get("is_shortlisted") is True
        or str(candidate.get("shortlist_status", "")).strip().lower() in (
            "shortlisted",
            "include",
            "included",
            "yes",
        )
    ])


def _clean_text(value: Any) -> str:
    return " ".join(str(value or "").strip().split())
