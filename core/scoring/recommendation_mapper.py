from typing import Dict, Optional


DEFAULT_RECOMMENDATION_THRESHOLDS = {
    "strong": 8.0,
    "moderate": 6.0,
    "weak": 4.0,
}


def normalize_score_range(score: float,
                          source_min: float = 0.0,
                          source_max: float = 1.0,
                          target_min: float = 0.0,
                          target_max: float = 10.0) -> float:
    """
    Convert scores between bounded numeric ranges.
    """

    score = float(score)

    if source_max <= source_min:
        raise ValueError("source_max must be greater than source_min.")

    clipped_score = min(max(score, source_min), source_max)
    source_span = source_max - source_min
    target_span = target_max - target_min
    normalized = ((clipped_score - source_min) / source_span) * target_span

    return float(target_min + normalized)


def map_score_to_recommendation(
    score: float,
    thresholds: Optional[Dict[str, float]] = None
) -> str:
    """
    Map a 0-10 final score into a recruiter-friendly recommendation label.
    """

    thresholds = thresholds or DEFAULT_RECOMMENDATION_THRESHOLDS
    score = float(score)

    if score >= thresholds["strong"]:
        return "Strong Match"

    if score >= thresholds["moderate"]:
        return "Moderate Match"

    if score >= thresholds["weak"]:
        return "Weak Match"

    return "Poor Match"
