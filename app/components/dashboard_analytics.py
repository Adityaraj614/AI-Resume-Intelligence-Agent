from html import escape
from typing import Any, Dict, List

import streamlit as st


def render_dashboard_analytics(workflow_result: Dict[str, Any] = None) -> None:
    outputs = workflow_result.get("workflow_outputs", {}) if isinstance(workflow_result, dict) else {}
    ranked_candidates = outputs.get("ranked_candidates", [])
    analytics_report = outputs.get("analytics_report", {}) if isinstance(outputs, dict) else {}

    if not isinstance(ranked_candidates, list):
        ranked_candidates = []

    average_score = _average_score(ranked_candidates, analytics_report)
    shortlist_count = _shortlist_count(outputs, ranked_candidates)
    total_count = len(ranked_candidates)
    top_skills = _top_skills(analytics_report, ranked_candidates)

    st.markdown(
        f"""
        <div class="analytics-grid">
            <div class="analytics-card">
                <div class="analytics-title">Score Distribution</div>
                <div class="analytics-subtitle">Average match health across the candidate pool.</div>
                <div class="donut" style="--value:{int(round(average_score))}">
                    <div class="donut-label">{int(round(average_score))}%</div>
                </div>
            </div>
            <div class="analytics-card">
                <div class="analytics-title">JD Match Radar</div>
                <div class="analytics-subtitle">Balanced view of skills, evidence, confidence, and role fit.</div>
                <div class="radar"></div>
            </div>
            <div class="analytics-card">
                <div class="analytics-title">Hiring Funnel</div>
                <div class="analytics-subtitle">Current intake to shortlist conversion.</div>
                {_funnel_html(total_count, shortlist_count)}
            </div>
            <div class="analytics-card">
                <div class="analytics-title">Top Skills</div>
                <div class="analytics-subtitle">Most frequent signals found in the candidate pool.</div>
                {_skills_html(top_skills)}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_ai_insights(workflow_result: Dict[str, Any] = None, limit: int = 4) -> None:
    insights = _insight_cards(workflow_result or {})[:limit]

    if not insights:
        st.info("Run analysis to generate recruiter insights for this workspace.")
        return

    columns = st.columns(len(insights), gap="small")

    for column, (icon, title, copy) in zip(columns, insights):
        with column:
            with st.container(border=True):
                st.caption(icon)
                st.markdown(f"**{title}**")
                st.write(copy)


def get_dashboard_overview(workflow_result: Dict[str, Any] = None) -> Dict[str, Any]:
    outputs = workflow_result.get("workflow_outputs", {}) if isinstance(workflow_result, dict) else {}
    ranked_candidates = outputs.get("ranked_candidates", [])
    analytics_report = outputs.get("analytics_report", {}) if isinstance(outputs, dict) else {}

    if not isinstance(ranked_candidates, list):
        ranked_candidates = []

    return {
        "candidates_processed": len(ranked_candidates),
        "average_score": _average_score(ranked_candidates, analytics_report),
        "shortlisted": _shortlist_count(outputs, ranked_candidates),
    }


def _average_score(ranked_candidates: List[Dict[str, Any]], analytics_report: Dict[str, Any]) -> float:
    pool_summary = analytics_report.get("candidate_pool_summary", {}) if isinstance(analytics_report, dict) else {}
    average = float(pool_summary.get("average_score", 0.0) or 0.0)

    if average:
        return _score_to_percent(average)

    scores = [
        _score_to_percent(float(candidate.get("final_score", 0.0) or 0.0))
        for candidate in ranked_candidates
        if isinstance(candidate, dict)
    ]

    return sum(scores) / len(scores) if scores else 0.0


def _shortlist_count(outputs: Dict[str, Any], ranked_candidates: List[Dict[str, Any]]) -> int:
    shortlist = outputs.get("shortlist", []) if isinstance(outputs, dict) else []

    if isinstance(shortlist, list) and shortlist:
        return len(shortlist)

    return sum(
        1
        for candidate in ranked_candidates
        if _score_to_percent(float(candidate.get("final_score", 0.0) or 0.0)) >= 80
    )


def _top_skills(
    analytics_report: Dict[str, Any],
    ranked_candidates: List[Dict[str, Any]],
    limit: int = 4,
) -> List[Dict[str, Any]]:
    skill_analytics = analytics_report.get("skill_analytics", {}) if isinstance(analytics_report, dict) else {}
    skills = skill_analytics.get("top_skills", [])

    if isinstance(skills, list) and skills:
        return skills[:limit]

    counts: Dict[str, int] = {}

    for candidate in ranked_candidates:
        candidate_skills = candidate.get("extracted_skills", candidate.get("skills", []))

        if not isinstance(candidate_skills, list):
            candidate_skills = [candidate_skills]

        for skill in candidate_skills:
            normalized = str(skill).strip()

            if normalized:
                counts[normalized] = counts.get(normalized, 0) + 1

    return [
        {"skill": skill, "count": count}
        for skill, count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:limit]
    ]


def _skills_html(skills: List[Dict[str, Any]]) -> str:
    if not skills:
        skills = [
            {"skill": "Python", "count": 0},
            {"skill": "Machine Learning", "count": 0},
            {"skill": "Communication", "count": 0},
        ]

    max_count = max(int(skill.get("count", 0) or 0) for skill in skills) or 1
    rows = []

    for skill in skills:
        label = escape(str(skill.get("skill", "Skill")))
        count = int(skill.get("count", 0) or 0)
        width = int((count / max_count) * 100) if max_count else 0
        rows.append(
            f"""
            <div class="skill-progress-row">
                <div class="skill-progress-label"><span>{label}</span><span>{count}</span></div>
                <div class="progress-track"><div class="progress-fill" style="width:{width}%;"></div></div>
            </div>
            """
        )

    return "".join(rows)


def _funnel_html(total_count: int, shortlist_count: int) -> str:
    reviewed = max(total_count, shortlist_count)
    considered = max(shortlist_count, int(round(reviewed * 0.65))) if reviewed else 0
    shortlist = shortlist_count

    return f"""
        <div class="funnel-step" style="width:100%;">Uploaded {reviewed}</div>
        <div class="funnel-step" style="width:78%;">Reviewed {considered}</div>
        <div class="funnel-step" style="width:56%;">Shortlisted {shortlist}</div>
    """


def _insight_cards(workflow_result: Dict[str, Any]) -> List[tuple]:
    outputs = workflow_result.get("workflow_outputs", {}) if isinstance(workflow_result, dict) else {}
    ranked_candidates = outputs.get("ranked_candidates", [])
    decision_support = outputs.get("decision_support", {}) if isinstance(outputs, dict) else {}
    top_candidate = ranked_candidates[0] if isinstance(ranked_candidates, list) and ranked_candidates else {}
    top_name = str(top_candidate.get("candidate_name", "top candidates") or "top candidates")
    recommendation = str(top_candidate.get("recommendation", "Review strongest matches first.") or "Review strongest matches first.")
    risk_summary = decision_support.get("risk_summary", {}) if isinstance(decision_support, dict) else {}
    risk_count = sum(int(value) for value in risk_summary.values()) if isinstance(risk_summary, dict) else 0

    return [
        ("ST", "Strengths", f"{top_name} currently leads the pool based on evidence-backed ranking signals."),
        ("SG", "Hiring Suggestions", recommendation),
        ("GP", "Skill Gaps", "Use JD match and evidence panels to validate missing requirements before shortlisting."),
        ("RC", "Recommendations", f"Prioritize high-confidence matches and review {risk_count} flagged decision signals."),
    ]


def _score_to_percent(score: float) -> float:
    if score <= 1:
        return max(0.0, min(score * 100, 100.0))

    return max(0.0, min(score, 100.0))
