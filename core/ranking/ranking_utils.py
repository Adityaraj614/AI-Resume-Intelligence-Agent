from typing import Any, Dict, List


RECOMMENDATION_PRIORITY = {
    "strong match": 1.0,
    "moderate match": 0.70,
    "weak match": 0.35,
    "poor match": 0.0,
}


def _bounded_float(value: float,
                   minimum: float,
                   maximum: float) -> float:
    return float(min(max(float(value), minimum), maximum))


def apply_confidence_penalty(final_score: float,
                             confidence: float,
                             penalty_weight: float = 1.0) -> float:
    """
    Reduce priority for low-confidence candidates.
    """

    confidence = _bounded_float(confidence, 0.0, 1.0)
    penalty = (1.0 - confidence) * penalty_weight

    return _bounded_float(final_score - penalty, 0.0, 10.0)


def apply_hallucination_penalty(priority_score: float,
                                hallucination_risk: float,
                                penalty_weight: float = 3.0) -> float:
    """
    Penalize candidates with unsupported or unsafe analysis.
    """

    hallucination_risk = _bounded_float(hallucination_risk, 0.0, 1.0)
    penalty = hallucination_risk * penalty_weight

    return _bounded_float(priority_score - penalty, 0.0, 10.0)


def calculate_recommendation_quality(candidate_record: Dict[str, Any]) -> float:
    """
    Convert recruiter recommendation labels into a bounded ranking signal.
    """

    recommendation = str(
        candidate_record.get("recommendation", "")
    ).strip().lower()

    return RECOMMENDATION_PRIORITY.get(recommendation, 0.35)


def calculate_evidence_quality(candidate_record: Dict[str, Any]) -> float:
    """
    Estimate evidence quality from retrieval coverage, confidence, and safety.
    """

    confidence = _bounded_float(candidate_record.get("confidence", 0.0), 0.0, 1.0)
    hallucination_risk = _bounded_float(
        candidate_record.get("hallucination_risk", 0.0),
        0.0,
        1.0,
    )
    semantic_score = _bounded_float(
        candidate_record.get("semantic_score", 0.0),
        0.0,
        1.0,
    )
    evidence_coverage = _bounded_float(
        candidate_record.get(
            "evidence_coverage",
            candidate_record.get("jd_match_coverage", semantic_score),
        ),
        0.0,
        1.0,
    )
    retrieval_quality = _bounded_float(
        candidate_record.get("retrieval_quality", semantic_score),
        0.0,
        1.0,
    )

    return _bounded_float(
        (semantic_score * 0.30)
        + (retrieval_quality * 0.25)
        + (evidence_coverage * 0.20)
        + (confidence * 0.05)
        + ((1.0 - hallucination_risk) * 0.20),
        0.0,
        1.0,
    )


def calculate_ranking_priority(candidate_record: Dict[str, Any]) -> float:
    """
    Deterministically combine score, confidence, evidence, and safety signals.
    """

    final_score = _bounded_float(candidate_record.get("final_score", 0.0), 0.0, 10.0)
    confidence = _bounded_float(candidate_record.get("confidence", 0.0), 0.0, 1.0)
    hallucination_risk = _bounded_float(
        candidate_record.get("hallucination_risk", 0.0),
        0.0,
        1.0,
    )
    evidence_quality = calculate_evidence_quality(candidate_record)
    recommendation_quality = calculate_recommendation_quality(candidate_record)
    base_priority = (
        (final_score * 0.70)
        + ((confidence * 10) * 0.15)
        + ((evidence_quality * 10) * 0.10)
        + ((recommendation_quality * 10) * 0.05)
    )

    return apply_hallucination_penalty(
        priority_score=base_priority,
        hallucination_risk=hallucination_risk,
    )


def safety_priority_bucket(candidate_record: Dict[str, Any]) -> int:
    """
    Group safer evidence-grounded candidates ahead of risky AI outputs.
    """

    warning_flags = candidate_record.get("warning_flags", [])

    if not isinstance(warning_flags, list):
        warning_flags = []

    hallucination_risk = _bounded_float(
        candidate_record.get("hallucination_risk", 0.0),
        0.0,
        1.0,
    )
    evidence_quality = _bounded_float(
        candidate_record.get(
            "evidence_quality",
            calculate_evidence_quality(candidate_record),
        ),
        0.0,
        1.0,
    )

    if (
        hallucination_risk >= 0.30
        or "safety_validation_failed" in warning_flags
        or "unsupported_claims_detected" in warning_flags
    ):
        return 2

    if evidence_quality < 0.45 or "weak_evidence_trace" in warning_flags:
        return 1

    return 0


def sort_candidates_by_priority(candidate_records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Sort candidates deterministically by safety, priority, and stable tie-breakers.
    """

    if not isinstance(candidate_records, list):
        raise TypeError("candidate_records must be a list.")

    return sorted(
        candidate_records,
        key=lambda item: (
            safety_priority_bucket(item),
            -float(item.get("ranking_priority", 0.0)),
            -float(item.get("final_score", 0.0)),
            -float(item.get("confidence", 0.0)),
            float(item.get("hallucination_risk", 0.0)),
            str(item.get("candidate_id", "")),
        ),
    )


def normalize_final_rankings(ranking_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Assign sequential ranks after sorting.
    """

    normalized_rankings = []

    for rank, item in enumerate(ranking_items, start=1):
        normalized_rankings.append({
            **item,
            "rank": rank,
        })

    return normalized_rankings
