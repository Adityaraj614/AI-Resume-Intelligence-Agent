from html import escape
from typing import Any, Dict, List

import streamlit as st


TABLE_COLUMNS = (
    "Candidate",
    "Match Score",
    "Confidence",
    "Recommendation",
    "Source",
    "Actions",
)


def render_ranking_table(workflow_result: Dict[str, Any] = None) -> None:
    rows = build_ranking_rows(workflow_result or {})

    if not rows:
        st.info("No ranked candidates yet. Complete candidate intake and run Analyze Candidates.")
        st.markdown(
            """
            <div class="candidate-list">
                <div class="candidate-row">
                    <div class="candidate-avatar">AI</div>
                    <div>
                        <div class="candidate-name">Candidate workspace awaiting analysis</div>
                        <div class="candidate-role">Upload resumes and a JD to activate rankings.</div>
                    </div>
                    <div class="candidate-score"><div class="score-ring" style="--score:0"><span>0%</span></div></div>
                    <div class="candidate-status"><span class="status-badge status-review">Under Review</span></div>
                    <div class="candidate-source candidate-meta">Source pending</div>
                    <div class="action-group">
                        <span class="action-button">View</span>
                        <span class="action-button">Compare</span>
                        <span class="action-button">Override</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    for row in rows:
        _render_candidate_row(row)


def build_ranking_rows(workflow_result: Dict[str, Any]) -> List[Dict[str, Any]]:
    outputs = workflow_result.get("workflow_outputs", {}) if isinstance(workflow_result, dict) else {}
    ranked_candidates = outputs.get("ranked_candidates", [])

    if not isinstance(ranked_candidates, list):
        return []

    rows = []

    for candidate in ranked_candidates:
        if not isinstance(candidate, dict):
            continue

        score = _numeric_score(candidate.get("final_score", 0.0))
        confidence = _numeric_score(candidate.get("confidence", candidate.get("confidence_score", 0.0)))
        recommendation = str(candidate.get("recommendation", "Under Review") or "Under Review")
        candidate_name = str(candidate.get("candidate_name", candidate.get("candidate_id", "Unknown")) or "Unknown")
        role = str(candidate.get("target_role", candidate.get("role", "Candidate profile")) or "Candidate profile")

        rows.append({
            "Candidate": candidate_name,
            "Role": role,
            "Match Score": _format_score(score),
            "Match Percent": _score_to_percent(score),
            "Confidence": _format_confidence(confidence),
            "Recommendation": recommendation,
            "Status": _status_from_recommendation(recommendation, score),
            "Source": str(candidate.get("source", "resume") or "resume").title(),
            "Actions": "View | Compare | Override",
            "_rank": int(candidate.get("rank", candidate.get("ranking_position", len(rows) + 1)) or len(rows) + 1),
        })

    return sorted(rows, key=lambda item: item["_rank"])


def _render_candidate_row(row: Dict[str, Any]) -> None:
    candidate = escape(str(row["Candidate"]))
    role = escape(str(row.get("Role", "Candidate profile")))
    source = escape(str(row.get("Source", "Resume")))
    status = str(row.get("Status", "Under Review"))
    status_class = _status_class(status)
    score = int(round(float(row.get("Match Percent", 0.0) or 0.0)))
    initials = escape(_initials(candidate))

    st.markdown(
        f"""
        <div class="candidate-row">
            <div class="candidate-avatar">{initials}</div>
            <div>
                <div class="candidate-name">{candidate}</div>
                <div class="candidate-role">{role}</div>
            </div>
            <div class="candidate-score">
                <div class="score-ring" style="--score:{score}"><span>{score}%</span></div>
            </div>
            <div class="candidate-status">
                <span class="status-badge {status_class}">{escape(status)}</span>
            </div>
            <div class="candidate-source candidate-meta">{source}</div>
            <div class="action-group">
                <span class="action-button">View</span>
                <span class="action-button">Compare</span>
                <span class="action-button">Override</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _format_score(value: Any) -> str:
    return f"{float(value or 0.0):.2f}"


def _format_confidence(value: Any) -> str:
    return f"{float(value or 0.0):.2f}"


def _numeric_score(value: Any) -> float:
    try:
        return float(value or 0.0)
    except (TypeError, ValueError):
        return 0.0


def _score_to_percent(score: float) -> float:
    if score <= 1.0:
        return max(0.0, min(score * 100.0, 100.0))
    if score <= 10.0:
        return max(0.0, min(score * 10.0, 100.0))
    return max(0.0, min(score, 100.0))


def _status_from_recommendation(recommendation: str, score: float) -> str:
    normalized = recommendation.lower()
    percent = _score_to_percent(score)

    if "shortlist" in normalized or "strong" in normalized or "interview" in normalized or percent >= 80:
        return "Shortlisted"

    if "reject" in normalized or "low" in normalized or "weak" in normalized or percent < 45:
        return "Low Match"

    if "review" in normalized or percent < 65:
        return "Under Review"

    return "Consider"


def _status_class(status: str) -> str:
    if status == "Shortlisted":
        return "status-shortlisted"

    if status == "Low Match":
        return "status-low"

    if status == "Consider":
        return "status-consider"

    return "status-review"


def _initials(name: str) -> str:
    parts = [part for part in name.replace("_", " ").split() if part]

    if not parts:
        return "AI"

    return "".join(part[0].upper() for part in parts[:2])
