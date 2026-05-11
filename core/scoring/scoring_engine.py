from typing import Any, Dict

from core.analysis.analysis_schema import validate_analysis_output
from core.scoring.confidence_calculator import calculate_confidence
from core.scoring.recommendation_mapper import (
    map_score_to_recommendation,
    normalize_score_range,
)
from core.scoring.scoring_schema import (
    normalize_scoring_schema,
    validate_scoring_output,
)


DEFAULT_RETRIEVAL_WEIGHT = 0.7
DEFAULT_LLM_WEIGHT = 0.3


def _score_from_analysis_recommendation(recommendation: str) -> float:
    normalized_recommendation = recommendation.strip().lower()

    if "strong" in normalized_recommendation:
        return 9.0

    if "moderate" in normalized_recommendation:
        return 7.0

    if "weak" in normalized_recommendation:
        return 5.0

    if "poor" in normalized_recommendation:
        return 2.0

    return 6.0


def _analysis_completeness_score(candidate_analysis: Dict[str, Any]) -> float:
    strengths = candidate_analysis.get("strengths", [])
    missing_skills = candidate_analysis.get("missing_skills", [])
    evidence_used = candidate_analysis.get("evidence_used", [])

    strength_signal = min(len(strengths) / 3, 1.0)
    evidence_signal = min(len(evidence_used) / 3, 1.0)
    summary_signal = 1.0 if candidate_analysis.get("summary") else 0.0
    gap_signal = 1.0 if isinstance(missing_skills, list) else 0.0

    return (
        (strength_signal * 0.30)
        + (evidence_signal * 0.35)
        + (summary_signal * 0.20)
        + (gap_signal * 0.15)
    )


def calculate_llm_match_score(candidate_analysis: Dict[str, Any]) -> float:
    """
    Deterministically score LLM analysis quality and recommendation signal.
    """

    if not validate_analysis_output(candidate_analysis):
        raise ValueError("candidate_analysis failed schema validation.")

    recommendation_score = _score_from_analysis_recommendation(
        candidate_analysis["recommendation"]
    )
    completeness_score = _analysis_completeness_score(candidate_analysis) * 10

    return float((recommendation_score * 0.6) + (completeness_score * 0.4))


def score_candidate(
    candidate_metadata: Dict[str, Any],
    candidate_analysis: Dict[str, Any],
    retrieval_weight: float = DEFAULT_RETRIEVAL_WEIGHT,
    llm_weight: float = DEFAULT_LLM_WEIGHT,
) -> Dict[str, Any]:
    """
    Build a structured, explainable hybrid candidate score.
    """

    if not isinstance(candidate_metadata, dict):
        raise TypeError("candidate_metadata must be a dictionary.")

    if not validate_analysis_output(candidate_analysis):
        raise ValueError("candidate_analysis failed schema validation.")

    if retrieval_weight < 0 or llm_weight < 0:
        raise ValueError("Scoring weights cannot be negative.")

    total_weight = retrieval_weight + llm_weight

    if total_weight <= 0:
        raise ValueError("At least one scoring weight must be greater than zero.")

    normalized_retrieval_weight = retrieval_weight / total_weight
    normalized_llm_weight = llm_weight / total_weight
    
    # Base FAISS cosine similarity (typically bounded 0.1 to 0.7 for natural text)
    semantic_score = float(candidate_metadata.get("aggregate_score", 0.0) or 0.0)
    semantic_score = min(max(semantic_score, 0.0), 1.0)
    
    # CALIBRATION: Apply square root curve to soften raw cosine scaling.
    # Elevates 0.36 -> 0.60, softening the harsh penalty for imperfect keyword overlap.
    import math
    calibrated_semantic_score = math.sqrt(semantic_score)
    
    semantic_score_10 = normalize_score_range(calibrated_semantic_score)
    llm_match_score = calculate_llm_match_score(candidate_analysis)
    final_score = (
        (semantic_score_10 * normalized_retrieval_weight)
        + (llm_match_score * normalized_llm_weight)
    )
    confidence = calculate_confidence(
        candidate_metadata=candidate_metadata,
        analysis=candidate_analysis,
    )

    scoring_output = normalize_scoring_schema({
        "candidate_id": candidate_analysis["candidate_id"],
        "semantic_score": semantic_score,
        "llm_match_score": llm_match_score,
        "final_score": final_score,
        "confidence": confidence,
        "recommendation": map_score_to_recommendation(final_score),
        "score_breakdown": {
            "retrieval_weight": normalized_retrieval_weight,
            "llm_weight": normalized_llm_weight,
            "semantic_score_10_point": semantic_score_10,
            "retrieval_source": "candidate_metadata.aggregate_score",
            "llm_source": "structured_candidate_analysis",
        },
    })

    if not validate_scoring_output(scoring_output):
        raise ValueError("Scoring output failed schema validation.")

    return scoring_output
