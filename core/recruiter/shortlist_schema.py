from typing import Any, Dict, List

from core.recruiter.shortlist_rules import (
    GOOD_MATCH,
    POTENTIAL_MATCH,
    STRONG_MATCH,
    WEAK_MATCH,
)
from core.recruiter.shortlist_utils import (
    bounded_float,
    get_confidence_score,
    get_ranking_position,
    normalize_score_to_10,
)


VALID_SHORTLIST_BUCKETS = {
    STRONG_MATCH,
    GOOD_MATCH,
    POTENTIAL_MATCH,
    WEAK_MATCH,
}

REQUIRED_SHORTLIST_KEYS = (
    "candidate_id",
    "candidate_name",
    "ranking_position",
    "final_score",
    "confidence_score",
    "hallucination_risk",
    "evidence_quality",
    "recommendation",
    "bucket",
    "shortlist_reason",
)


def normalize_shortlist_item(shortlist_item: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize one shortlist item into stable recruiter-facing field types.
    """

    if not isinstance(shortlist_item, dict):
        raise TypeError("shortlist_item must be a dictionary.")

    candidate_id = str(
        shortlist_item.get("candidate_id", "unknown_candidate")
    ).strip() or "unknown_candidate"

    return {
        "candidate_id": candidate_id,
        "candidate_name": str(
            shortlist_item.get("candidate_name", candidate_id)
        ).strip() or candidate_id,
        "ranking_position": get_ranking_position(shortlist_item),
        "final_score": normalize_score_to_10(shortlist_item.get("final_score", 0.0)),
        "confidence_score": get_confidence_score(shortlist_item),
        "hallucination_risk": bounded_float(
            shortlist_item.get("hallucination_risk", 0.0),
            0.0,
            1.0,
        ),
        "evidence_quality": bounded_float(
            shortlist_item.get("evidence_quality", 0.0),
            0.0,
            1.0,
        ),
        "recommendation": str(shortlist_item.get("recommendation", "")).strip(),
        "bucket": str(shortlist_item.get("bucket", WEAK_MATCH)).strip(),
        "shortlist_reason": str(
            shortlist_item.get("shortlist_reason", "")
        ).strip(),
    }


def validate_shortlist_output(shortlist_output: List[Dict[str, Any]]) -> bool:
    """
    Validate recruiter shortlist output for stable downstream UI usage.
    """

    if not isinstance(shortlist_output, list):
        return False

    previous_position = 0

    for item in shortlist_output:
        if not isinstance(item, dict):
            return False

        for key in REQUIRED_SHORTLIST_KEYS:
            if key not in item:
                return False

        if not isinstance(item["candidate_id"], str) or not item["candidate_id"].strip():
            return False

        if item["ranking_position"] < previous_position:
            return False

        if not 0 <= item["final_score"] <= 10:
            return False

        if not 0 <= item["confidence_score"] <= 1:
            return False

        if not 0 <= item["hallucination_risk"] <= 1:
            return False

        if not 0 <= item["evidence_quality"] <= 1:
            return False

        if item["bucket"] not in VALID_SHORTLIST_BUCKETS:
            return False

        if not isinstance(item["shortlist_reason"], str) or not item["shortlist_reason"]:
            return False

        previous_position = item["ranking_position"]

    return True

