from typing import Any, Dict, List, Optional

from core.recruiter.comparison_utils import build_candidate_summary
from core.recruiter.decision_schema import (
    normalize_decision_output,
    validate_decision_output,
    validate_decision_report,
)
from core.recruiter.interview_recommender import (
    evaluate_hiring_readiness,
    recommend_interview_priority,
    suggest_interview_focus_areas,
)
from core.recruiter.recruiter_summary import (
    build_action_recommendation,
    build_candidate_decision_summary,
    summarize_decision_report,
)
from core.recruiter.risk_analyzer import generate_risk_flags
from core.recruiter.shortlist_utils import sort_ranked_candidates


def build_candidate_decision_support(
    candidate: Dict[str, Any],
    thresholds: Optional[Dict[str, Dict[str, float]]] = None,
) -> Dict[str, Any]:
    """
    Build deterministic recruiter decision support for one candidate.
    """

    summary = build_candidate_summary(candidate)
    readiness = evaluate_hiring_readiness(candidate)
    decision = normalize_decision_output({
        "candidate_id": summary["candidate_id"],
        "candidate_name": summary["candidate_name"],
        "ranking_position": summary["ranking_position"],
        "interview_priority": recommend_interview_priority(candidate, thresholds),
        "hiring_readiness": readiness["hiring_readiness"],
        "readiness_reason": readiness["readiness_reason"],
        "risk_flags": generate_risk_flags(candidate),
        "interview_focus_areas": suggest_interview_focus_areas(candidate),
        "decision_summary": build_candidate_decision_summary(candidate),
        "action_recommendation": build_action_recommendation(candidate),
    })

    if not validate_decision_output(decision):
        raise ValueError("Decision support output failed schema validation.")

    return decision


def summarize_risks(candidate_decisions: List[Dict[str, Any]]) -> Dict[str, int]:
    risk_counts: Dict[str, int] = {}

    for decision in candidate_decisions:
        for risk_flag in decision["risk_flags"]:
            risk_counts[risk_flag] = risk_counts.get(risk_flag, 0) + 1

    return {
        key: risk_counts[key]
        for key in sorted(risk_counts)
    }


def generate_recruiter_decision_report(
    candidates: List[Dict[str, Any]],
    thresholds: Optional[Dict[str, Dict[str, float]]] = None,
) -> Dict[str, Any]:
    """
    Generate deterministic batch recruiter decision-support report.
    """

    if not isinstance(candidates, list):
        raise TypeError("candidates must be a list.")

    ordered_candidates = sort_ranked_candidates(candidates)
    candidate_decisions = [
        build_candidate_decision_support(candidate, thresholds)
        for candidate in ordered_candidates
    ]
    prioritized_interviews = [
        decision
        for decision in candidate_decisions
        if decision["interview_priority"] == "PRIORITY_INTERVIEW"
    ]
    hiring_ready_candidates = [
        decision
        for decision in candidate_decisions
        if decision["hiring_readiness"] == "HIGH"
    ]
    report = {
        "candidate_count": len(candidate_decisions),
        "prioritized_interviews": prioritized_interviews,
        "hiring_ready_candidates": hiring_ready_candidates,
        "risk_summary": summarize_risks(candidate_decisions),
        "candidate_decisions": candidate_decisions,
        "report_summary": summarize_decision_report(candidate_decisions),
    }

    if not validate_decision_report(report):
        raise ValueError("Decision report failed schema validation.")

    return report

