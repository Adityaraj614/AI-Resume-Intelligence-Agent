from typing import Any, Dict, List, Optional

from core.recruiter.comparison_utils import (
    get_evidence_quality,
    get_hallucination_risk,
    get_semantic_score,
    normalize_missing_skills,
    normalize_weaknesses,
)
from core.recruiter.risk_analyzer import generate_risk_flags
from core.recruiter.shortlist_utils import (
    get_confidence_score,
    normalize_score_to_10,
)


PRIORITY_INTERVIEW = "PRIORITY_INTERVIEW"
STANDARD_INTERVIEW = "STANDARD_INTERVIEW"
HOLD = "HOLD"
REJECT = "REJECT"

HIGH_READINESS = "HIGH"
MEDIUM_READINESS = "MEDIUM"
LOW_READINESS = "LOW"


DEFAULT_DECISION_THRESHOLDS = {
    PRIORITY_INTERVIEW: {
        "min_final_score": 8.5,
        "min_confidence": 0.80,
        "max_hallucination_risk": 0.10,
        "min_evidence_quality": 0.75,
    },
    STANDARD_INTERVIEW: {
        "min_final_score": 7.0,
        "min_confidence": 0.65,
        "max_hallucination_risk": 0.20,
        "min_evidence_quality": 0.60,
    },
    HOLD: {
        "min_final_score": 5.5,
        "min_confidence": 0.45,
        "max_hallucination_risk": 0.30,
        "min_evidence_quality": 0.45,
    },
}


def normalize_decision_thresholds(
    thresholds: Optional[Dict[str, Dict[str, float]]] = None
) -> Dict[str, Dict[str, float]]:
    merged = {
        label: values.copy()
        for label, values in DEFAULT_DECISION_THRESHOLDS.items()
    }

    if not thresholds:
        return merged

    for label, values in thresholds.items():
        if label in merged and isinstance(values, dict):
            merged[label].update(values)

    return merged


def _candidate_signals(candidate: Dict[str, Any]) -> Dict[str, float]:
    return {
        "final_score": normalize_score_to_10(candidate.get("final_score", 0.0)),
        "confidence": get_confidence_score(candidate),
        "hallucination_risk": get_hallucination_risk(candidate),
        "evidence_quality": get_evidence_quality(candidate),
        "semantic_score": get_semantic_score(candidate),
    }


def _meets_thresholds(signals: Dict[str, float],
                      thresholds: Dict[str, float]) -> bool:
    return (
        signals["final_score"] >= thresholds["min_final_score"]
        and signals["confidence"] >= thresholds["min_confidence"]
        and signals["hallucination_risk"] <= thresholds["max_hallucination_risk"]
        and signals["evidence_quality"] >= thresholds["min_evidence_quality"]
    )


def recommend_interview_priority(
    candidate: Dict[str, Any],
    thresholds: Optional[Dict[str, Dict[str, float]]] = None,
) -> str:
    """
    Assign deterministic interview priority from score, evidence, confidence, and safety.
    """

    active_thresholds = normalize_decision_thresholds(thresholds)
    signals = _candidate_signals(candidate)
    risk_flags = generate_risk_flags(candidate)

    if "HIGH_HALLUCINATION_RISK" in risk_flags or "UNSUPPORTED_CLAIMS" in risk_flags:
        return REJECT

    if _meets_thresholds(signals, active_thresholds[PRIORITY_INTERVIEW]):
        return PRIORITY_INTERVIEW

    if _meets_thresholds(signals, active_thresholds[STANDARD_INTERVIEW]):
        return STANDARD_INTERVIEW

    if _meets_thresholds(signals, active_thresholds[HOLD]):
        return HOLD

    return REJECT


def evaluate_hiring_readiness(candidate: Dict[str, Any]) -> Dict[str, str]:
    signals = _candidate_signals(candidate)
    missing_skill_count = len(normalize_missing_skills(candidate))
    risk_flags = generate_risk_flags(candidate)

    if (
        signals["final_score"] >= 8.0
        and signals["confidence"] >= 0.75
        and signals["evidence_quality"] >= 0.70
        and signals["hallucination_risk"] <= 0.15
        and missing_skill_count <= 1
        and "HIGH_HALLUCINATION_RISK" not in risk_flags
        and "UNSUPPORTED_CLAIMS" not in risk_flags
    ):
        return {
            "hiring_readiness": HIGH_READINESS,
            "readiness_reason": "Strong evidence-backed alignment with low hallucination risk.",
        }

    if (
        signals["final_score"] >= 6.0
        and signals["confidence"] >= 0.50
        and signals["evidence_quality"] >= 0.45
        and signals["hallucination_risk"] <= 0.30
    ):
        return {
            "hiring_readiness": MEDIUM_READINESS,
            "readiness_reason": "Moderate evidence-backed alignment with recruiter review recommended.",
        }

    return {
        "hiring_readiness": LOW_READINESS,
        "readiness_reason": "Insufficient evidence, confidence, or safety for hiring-ready status.",
    }


def suggest_interview_focus_areas(candidate: Dict[str, Any],
                                  max_items: int = 5) -> List[str]:
    """
    Generate interview focus areas only from missing skills and weaknesses.
    """

    focus_areas = []

    for missing_skill in normalize_missing_skills(candidate):
        focus_areas.append(f"Validate {missing_skill} experience.")

    for weakness in normalize_weaknesses(candidate):
        focus_areas.append(f"Probe {weakness}.")

    if get_evidence_quality(candidate) < 0.45:
        focus_areas.append("Validate claims with concrete project evidence.")

    if get_confidence_score(candidate) < 0.50:
        focus_areas.append("Clarify low-confidence profile areas.")

    deduped_focus = []

    for focus_area in focus_areas:
        if focus_area not in deduped_focus:
            deduped_focus.append(focus_area)

    return deduped_focus[:max_items]

