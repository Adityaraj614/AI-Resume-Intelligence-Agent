from typing import Any, Dict, List


VALID_INTERVIEW_PRIORITIES = {
    "PRIORITY_INTERVIEW",
    "STANDARD_INTERVIEW",
    "HOLD",
    "REJECT",
}

VALID_READINESS_LEVELS = {
    "HIGH",
    "MEDIUM",
    "LOW",
}

REQUIRED_DECISION_KEYS = (
    "candidate_id",
    "candidate_name",
    "ranking_position",
    "interview_priority",
    "hiring_readiness",
    "readiness_reason",
    "risk_flags",
    "interview_focus_areas",
    "decision_summary",
    "action_recommendation",
)

REQUIRED_REPORT_KEYS = (
    "candidate_count",
    "prioritized_interviews",
    "hiring_ready_candidates",
    "risk_summary",
    "candidate_decisions",
    "report_summary",
)


def normalize_decision_output(decision: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(decision, dict):
        raise TypeError("decision must be a dictionary.")

    candidate_id = str(decision.get("candidate_id", "unknown_candidate")).strip()
    candidate_id = candidate_id or "unknown_candidate"

    return {
        "candidate_id": candidate_id,
        "candidate_name": str(decision.get("candidate_name", candidate_id)).strip() or candidate_id,
        "ranking_position": int(decision.get("ranking_position", 0) or 0),
        "interview_priority": str(decision.get("interview_priority", "REJECT")).strip(),
        "hiring_readiness": str(decision.get("hiring_readiness", "LOW")).strip(),
        "readiness_reason": str(decision.get("readiness_reason", "")).strip(),
        "risk_flags": list(decision.get("risk_flags", [])),
        "interview_focus_areas": list(decision.get("interview_focus_areas", [])),
        "decision_summary": str(decision.get("decision_summary", "")).strip(),
        "action_recommendation": str(decision.get("action_recommendation", "")).strip(),
    }


def validate_decision_output(decision: Dict[str, Any]) -> bool:
    if not isinstance(decision, dict):
        return False

    for key in REQUIRED_DECISION_KEYS:
        if key not in decision:
            return False

    if not decision["candidate_id"]:
        return False

    if decision["interview_priority"] not in VALID_INTERVIEW_PRIORITIES:
        return False

    if decision["hiring_readiness"] not in VALID_READINESS_LEVELS:
        return False

    if not isinstance(decision["risk_flags"], list):
        return False

    if not isinstance(decision["interview_focus_areas"], list):
        return False

    if not decision["decision_summary"]:
        return False

    if not decision["action_recommendation"]:
        return False

    return True


def validate_decision_report(report: Dict[str, Any]) -> bool:
    if not isinstance(report, dict):
        return False

    for key in REQUIRED_REPORT_KEYS:
        if key not in report:
            return False

    if report["candidate_count"] != len(report["candidate_decisions"]):
        return False

    if not isinstance(report["prioritized_interviews"], list):
        return False

    if not isinstance(report["hiring_ready_candidates"], list):
        return False

    if not isinstance(report["risk_summary"], dict):
        return False

    if not isinstance(report["report_summary"], str):
        return False

    return all(
        validate_decision_output(decision)
        for decision in report["candidate_decisions"]
    )

