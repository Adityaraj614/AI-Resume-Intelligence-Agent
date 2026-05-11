from typing import Any, Dict, List

from core.recruiter.shortlist_utils import (
    get_confidence_score,
    normalize_score_to_10,
)
from core.recruiter.comparison_utils import (
    get_evidence_quality,
    get_hallucination_risk,
    get_semantic_score,
)


def validate_score_normalization(candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Validate score and signal ranges without changing upstream ranking logic.
    """

    if not isinstance(candidates, list):
        raise TypeError("candidates must be a list.")

    anomalies = []

    for candidate in candidates:
        candidate_id = str(candidate.get("candidate_id", "unknown_candidate"))
        raw_score = float(candidate.get("final_score", 0.0) or 0.0)
        normalized_score = normalize_score_to_10(raw_score)
        confidence = get_confidence_score(candidate)
        hallucination_risk = get_hallucination_risk(candidate)
        evidence_quality = get_evidence_quality(candidate)
        semantic_score = get_semantic_score(candidate)

        if raw_score < 0 or raw_score > 100:
            anomalies.append({
                "candidate_id": candidate_id,
                "field": "final_score",
                "value": raw_score,
                "issue": "score_outside_supported_range",
            })

        if not 0 <= normalized_score <= 10:
            anomalies.append({
                "candidate_id": candidate_id,
                "field": "final_score",
                "value": normalized_score,
                "issue": "normalized_score_outside_0_10",
            })

        for field, value in (
            ("confidence_score", confidence),
            ("hallucination_risk", hallucination_risk),
            ("evidence_quality", evidence_quality),
            ("semantic_score", semantic_score),
        ):
            if not 0 <= value <= 1:
                anomalies.append({
                    "candidate_id": candidate_id,
                    "field": field,
                    "value": value,
                    "issue": "signal_outside_0_1",
                })

    return {
        "is_valid": not anomalies,
        "anomaly_count": len(anomalies),
        "anomalies": anomalies,
    }


def validate_ranking_positions(candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Validate duplicate and missing ranking positions.
    """

    if not isinstance(candidates, list):
        raise TypeError("candidates must be a list.")

    positions = []
    anomalies = []

    for candidate in candidates:
        candidate_id = str(candidate.get("candidate_id", "unknown_candidate"))
        position = int(candidate.get("ranking_position", candidate.get("rank", 0)) or 0)
        positions.append(position)

        if position <= 0:
            anomalies.append({
                "candidate_id": candidate_id,
                "field": "ranking_position",
                "value": position,
                "issue": "missing_or_invalid_ranking_position",
            })

    duplicate_positions = sorted({
        position
        for position in positions
        if position > 0 and positions.count(position) > 1
    })

    for position in duplicate_positions:
        anomalies.append({
            "candidate_id": "multiple_candidates",
            "field": "ranking_position",
            "value": position,
            "issue": "duplicate_ranking_position",
        })

    return {
        "is_valid": not anomalies,
        "anomaly_count": len(anomalies),
        "anomalies": anomalies,
    }

