from typing import Any, Dict, List


REQUIRED_RANKING_KEYS = (
    "rank",
    "candidate_id",
    "final_score",
    "confidence",
    "recommendation",
    "hallucination_risk",
    "ranking_reason",
)


def _bounded_float(value: Any,
                   minimum: float,
                   maximum: float) -> float:
    number = float(value)

    return float(min(max(number, minimum), maximum))


def normalize_ranking_schema(ranking_item: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize one ranking item into stable recruiter-facing field types.
    """

    if not isinstance(ranking_item, dict):
        raise TypeError("ranking_item must be a dictionary.")

    normalized_item = {
        "rank": int(ranking_item.get("rank", 0)),
        "candidate_id": str(
            ranking_item.get("candidate_id", "unknown_candidate")
        ).strip() or "unknown_candidate",
        "final_score": _bounded_float(ranking_item.get("final_score", 0.0), 0.0, 10.0),
        "confidence": _bounded_float(ranking_item.get("confidence", 0.0), 0.0, 1.0),
        "recommendation": str(ranking_item.get("recommendation", "")).strip(),
        "hallucination_risk": _bounded_float(
            ranking_item.get("hallucination_risk", 0.0),
            0.0,
            1.0,
        ),
        "ranking_reason": str(ranking_item.get("ranking_reason", "")).strip(),
    }

    optional_keys = (
        "ranking_priority",
        "evidence_quality",
        "evidence_coverage",
        "retrieval_quality",
        "recommendation_quality",
        "warning_flags",
    )

    for optional_key in optional_keys:
        if optional_key in ranking_item:
            normalized_item[optional_key] = ranking_item[optional_key]

    return normalized_item


def validate_ranking_output(ranking_output: List[Dict[str, Any]]) -> bool:
    """
    Validate final ordered ranking output.
    """

    if not isinstance(ranking_output, list):
        return False

    expected_rank = 1

    for item in ranking_output:
        if not isinstance(item, dict):
            return False

        for key in REQUIRED_RANKING_KEYS:
            if key not in item:
                return False

        if item["rank"] != expected_rank:
            return False

        if not isinstance(item["candidate_id"], str) or not item["candidate_id"].strip():
            return False

        if not 0 <= item["final_score"] <= 10:
            return False

        if not 0 <= item["confidence"] <= 1:
            return False

        if not isinstance(item["recommendation"], str) or not item["recommendation"].strip():
            return False

        if not 0 <= item["hallucination_risk"] <= 1:
            return False

        if not isinstance(item["ranking_reason"], str) or not item["ranking_reason"].strip():
            return False

        if "warning_flags" in item and not isinstance(item["warning_flags"], list):
            return False

        expected_rank += 1

    return True
