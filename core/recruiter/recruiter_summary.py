from typing import Any, Dict, List

from core.recruiter.comparison_utils import (
    get_evidence_quality,
    get_hallucination_risk,
    get_semantic_score,
    normalize_missing_skills,
    normalize_strengths,
)
from core.recruiter.interview_recommender import (
    evaluate_hiring_readiness,
    recommend_interview_priority,
)
from core.recruiter.risk_analyzer import generate_risk_flags
from core.recruiter.shortlist_utils import get_confidence_score


def build_candidate_decision_summary(candidate: Dict[str, Any]) -> str:
    """
    Build deterministic recruiter-readable summary from provided candidate fields.
    """

    candidate_name = str(
        candidate.get("candidate_name", candidate.get("candidate_id", "Candidate"))
    ).strip() or "Candidate"
    semantic_score = get_semantic_score(candidate)
    evidence_quality = get_evidence_quality(candidate)
    confidence = get_confidence_score(candidate)
    hallucination_risk = get_hallucination_risk(candidate)
    missing_skills = normalize_missing_skills(candidate)
    strengths = normalize_strengths(candidate)

    if semantic_score >= 0.80:
        alignment = "strong semantic alignment"
    elif semantic_score >= 0.55:
        alignment = "moderate semantic alignment"
    else:
        alignment = "weak semantic alignment"

    if evidence_quality >= 0.75:
        evidence = "strong evidence quality"
    elif evidence_quality >= 0.45:
        evidence = "usable evidence quality"
    else:
        evidence = "weak evidence quality"

    if confidence >= 0.80:
        confidence_text = "high confidence"
    elif confidence >= 0.50:
        confidence_text = "moderate confidence"
    else:
        confidence_text = "low confidence"

    if hallucination_risk <= 0.10:
        safety = "low hallucination risk"
    elif hallucination_risk <= 0.30:
        safety = "manageable hallucination risk"
    else:
        safety = "elevated hallucination risk"

    summary = (
        f"{candidate_name} shows {alignment}, {evidence}, "
        f"{confidence_text}, and {safety}"
    )

    if strengths:
        summary += f"; strongest provided signal: {strengths[0]}"

    if missing_skills:
        summary += f"; review missing skill: {missing_skills[0]}"

    return summary + "."


def build_action_recommendation(candidate: Dict[str, Any]) -> str:
    priority = recommend_interview_priority(candidate)
    readiness = evaluate_hiring_readiness(candidate)["hiring_readiness"]
    risk_flags = generate_risk_flags(candidate)

    if priority == "PRIORITY_INTERVIEW" and readiness == "HIGH":
        return "Schedule priority interview."

    if priority == "STANDARD_INTERVIEW":
        return "Schedule standard interview with targeted validation."

    if priority == "HOLD":
        return "Hold for recruiter review before interview scheduling."

    if "HIGH_HALLUCINATION_RISK" in risk_flags or "UNSUPPORTED_CLAIMS" in risk_flags:
        return "Do not advance until unsupported or unsafe claims are resolved."

    return "Do not advance based on current evidence."


def summarize_decision_report(decisions: List[Dict[str, Any]]) -> str:
    total = len(decisions)

    if total == 0:
        return "No candidates available for recruiter decision support."

    priority_count = len([
        decision
        for decision in decisions
        if decision["interview_priority"] == "PRIORITY_INTERVIEW"
    ])
    high_readiness_count = len([
        decision
        for decision in decisions
        if decision["hiring_readiness"] == "HIGH"
    ])

    return (
        f"{priority_count} of {total} candidates are priority interview candidates; "
        f"{high_readiness_count} candidates are hiring-ready."
    )

