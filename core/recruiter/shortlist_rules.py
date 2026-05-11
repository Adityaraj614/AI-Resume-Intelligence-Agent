from typing import Any, Dict, Optional

from core.recruiter.shortlist_utils import (
    bounded_float,
    get_confidence_score,
    get_warning_flags,
    normalize_score_to_10,
)


STRONG_MATCH = "STRONG_MATCH"
GOOD_MATCH = "GOOD_MATCH"
POTENTIAL_MATCH = "POTENTIAL_MATCH"
WEAK_MATCH = "WEAK_MATCH"


DEFAULT_SHORTLIST_THRESHOLDS = {
    STRONG_MATCH: {
        "min_final_score": 8.5,
        "min_confidence": 0.80,
        "max_hallucination_risk": 0.10,
        "min_evidence_quality": 0.75,
    },
    GOOD_MATCH: {
        "min_final_score": 7.0,
        "min_confidence": 0.65,
        "max_hallucination_risk": 0.20,
        "min_evidence_quality": 0.60,
    },
    POTENTIAL_MATCH: {
        "min_final_score": 5.5,
        "min_confidence": 0.45,
        "max_hallucination_risk": 0.30,
        "min_evidence_quality": 0.45,
    },
    "exclusion": {
        "max_hallucination_risk": 0.60,
        "min_evidence_quality": 0.25,
    },
}


def normalize_shortlist_thresholds(
    thresholds: Optional[Dict[str, Dict[str, float]]] = None
) -> Dict[str, Dict[str, float]]:
    """
    Merge caller thresholds with deterministic defaults.
    """

    merged = {
        bucket: values.copy()
        for bucket, values in DEFAULT_SHORTLIST_THRESHOLDS.items()
    }

    if not thresholds:
        return merged

    for bucket, values in thresholds.items():
        if bucket not in merged or not isinstance(values, dict):
            continue

        merged[bucket].update(values)

    return merged


def _candidate_signals(candidate: Dict[str, Any]) -> Dict[str, float]:
    return {
        "final_score": normalize_score_to_10(candidate.get("final_score", 0.0)),
        "confidence": get_confidence_score(candidate),
        "hallucination_risk": bounded_float(
            candidate.get("hallucination_risk", 0.0),
            0.0,
            1.0,
        ),
        "evidence_quality": bounded_float(
            candidate.get(
                "evidence_quality",
                candidate.get("evidence_coverage", 0.0),
            ),
            0.0,
            1.0,
        ),
        "semantic_score": bounded_float(
            candidate.get("semantic_score", 0.0),
            0.0,
            1.0,
        ),
    }


def should_exclude_candidate(
    candidate: Dict[str, Any],
    thresholds: Optional[Dict[str, Dict[str, float]]] = None
) -> bool:
    """
    Exclude candidates with severe safety or evidence problems.
    """

    active_thresholds = normalize_shortlist_thresholds(thresholds)
    exclusion = active_thresholds["exclusion"]
    signals = _candidate_signals(candidate)
    warning_flags = get_warning_flags(candidate)

    if "unsupported_claims_detected" in warning_flags:
        return True

    if signals["hallucination_risk"] >= exclusion["max_hallucination_risk"]:
        return True

    if signals["evidence_quality"] < exclusion["min_evidence_quality"]:
        return True

    return False


def _meets_bucket(signals: Dict[str, float],
                  bucket_thresholds: Dict[str, float]) -> bool:
    return (
        signals["final_score"] >= bucket_thresholds["min_final_score"]
        and signals["confidence"] >= bucket_thresholds["min_confidence"]
        and signals["hallucination_risk"] <= bucket_thresholds["max_hallucination_risk"]
        and signals["evidence_quality"] >= bucket_thresholds["min_evidence_quality"]
    )


def assign_shortlist_bucket(
    candidate: Dict[str, Any],
    thresholds: Optional[Dict[str, Dict[str, float]]] = None
) -> str:
    """
    Assign a recruiter shortlist bucket using transparent deterministic rules.
    """

    active_thresholds = normalize_shortlist_thresholds(thresholds)
    signals = _candidate_signals(candidate)

    if should_exclude_candidate(candidate, active_thresholds):
        return WEAK_MATCH

    for bucket in (STRONG_MATCH, GOOD_MATCH, POTENTIAL_MATCH):
        if _meets_bucket(signals, active_thresholds[bucket]):
            return bucket

    return WEAK_MATCH

