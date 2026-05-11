from typing import Any, Dict, List

from core.analytics.ranking_analytics import build_full_ranking_analytics


def generate_recruiter_insights_from_analytics(analytics: Dict[str, Any]) -> List[str]:
    """
    Generate deterministic recruiter-safe insights from aggregate analytics.
    """

    insights = []
    summary = analytics.get("candidate_pool_summary", {})
    confidence = analytics.get("confidence_analytics", {})
    hallucination = analytics.get("hallucination_analytics", {})
    evidence = analytics.get("evidence_analytics", {})
    skills = analytics.get("skill_analytics", {})
    missing_skills = analytics.get("missing_skill_analytics", {})
    buckets = analytics.get("bucket_analytics", {})

    total_candidates = int(summary.get("total_candidates", 0))

    if total_candidates == 0:
        return ["No candidates available for analytics."]

    strong_match_count = buckets.get("strong_match_count", 0)
    insights.append(
        f"{strong_match_count} of {total_candidates} candidates are in the STRONG_MATCH bucket."
    )

    if confidence.get("average_confidence", 0.0) >= 0.80:
        insights.append("Candidate pool has high average confidence.")
    elif confidence.get("low_confidence_count", 0) > 0:
        insights.append(
            f"{confidence['low_confidence_count']} candidates have low confidence scores."
        )

    if hallucination.get("high_risk_count", 0) > 0:
        insights.append(
            f"{hallucination['high_risk_count']} candidates show elevated hallucination risk."
        )
    else:
        insights.append("No high hallucination-risk candidates were detected.")

    if evidence.get("weak_evidence_count", 0) > 0:
        insights.append(
            f"{evidence['weak_evidence_count']} candidates have weak evidence quality."
        )
    elif evidence.get("strong_evidence_count", 0) > 0:
        insights.append(
            f"{evidence['strong_evidence_count']} candidates have strong evidence quality."
        )

    top_skills = skills.get("top_skills", [])

    if top_skills:
        top_skill = top_skills[0]
        insights.append(
            f"{top_skill['skill']} is the most common retrieved skill across candidates."
        )

    top_missing_skills = missing_skills.get("top_missing_skills", [])

    if top_missing_skills:
        missing_skill = top_missing_skills[0]
        insights.append(
            f"{missing_skill['skill']} is the most common missing skill across candidates."
        )

    return insights


def generate_recruiter_insights(candidates: List[Dict[str, Any]]) -> List[str]:
    analytics = build_full_ranking_analytics(candidates)

    return generate_recruiter_insights_from_analytics(analytics)


def build_analytics_report(candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
    analytics = build_full_ranking_analytics(candidates)

    return {
        **analytics,
        "recruiter_insights": generate_recruiter_insights_from_analytics(analytics),
    }

