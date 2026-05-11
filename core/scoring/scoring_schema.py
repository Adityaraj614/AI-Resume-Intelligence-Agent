from typing import Any, Dict


REQUIRED_SCORING_KEYS = (
    "candidate_id",
    "semantic_score",
    "llm_match_score",
    "final_score",
    "confidence",
    "recommendation",
    "score_breakdown",
)


def _bounded_float(value: Any,
                   minimum: float,
                   maximum: float) -> float:
    number = float(value)

    return float(min(max(number, minimum), maximum))


def normalize_scoring_schema(scoring_output: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize scoring output into stable ranking-safe field types.
    """

    if not isinstance(scoring_output, dict):
        raise TypeError("scoring_output must be a dictionary.")

    score_breakdown = scoring_output.get("score_breakdown", {})

    if not isinstance(score_breakdown, dict):
        score_breakdown = {}

    return {
        "candidate_id": str(
            scoring_output.get("candidate_id", "unknown_candidate")
        ).strip() or "unknown_candidate",
        "semantic_score": _bounded_float(
            scoring_output.get("semantic_score", 0.0),
            0.0,
            1.0,
        ),
        "llm_match_score": _bounded_float(
            scoring_output.get("llm_match_score", 0.0),
            0.0,
            10.0,
        ),
        "final_score": _bounded_float(
            scoring_output.get("final_score", 0.0),
            0.0,
            10.0,
        ),
        "confidence": _bounded_float(
            scoring_output.get("confidence", 0.0),
            0.0,
            1.0,
        ),
        "recommendation": str(
            scoring_output.get("recommendation", "")
        ).strip(),
        "score_breakdown": score_breakdown,
    }


def validate_scoring_output(scoring_output: Dict[str, Any]) -> bool:
    """
    Validate structured scoring output for downstream ranking.
    """

    if not isinstance(scoring_output, dict):
        return False

    for key in REQUIRED_SCORING_KEYS:
        if key not in scoring_output:
            return False

    if not isinstance(scoring_output["candidate_id"], str) or not scoring_output["candidate_id"].strip():
        return False

    if not 0 <= scoring_output["semantic_score"] <= 1:
        return False

    if not 0 <= scoring_output["llm_match_score"] <= 10:
        return False

    if not 0 <= scoring_output["final_score"] <= 10:
        return False

    if not 0 <= scoring_output["confidence"] <= 1:
        return False

    if not isinstance(scoring_output["recommendation"], str) or not scoring_output["recommendation"].strip():
        return False

    if not isinstance(scoring_output["score_breakdown"], dict):
        return False

    return True
