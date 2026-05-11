from typing import Any, Dict, List, Optional

from core.recruiter.shortlist_rules import (
    WEAK_MATCH,
    assign_shortlist_bucket,
    should_exclude_candidate,
)
from core.recruiter.shortlist_schema import (
    normalize_shortlist_item,
    validate_shortlist_output,
)
from core.recruiter.shortlist_utils import (
    bounded_float,
    get_confidence_score,
    get_ranking_position,
    sort_ranked_candidates,
    truncate_shortlist,
)


def build_shortlist_reason(candidate: Dict[str, Any],
                           bucket: str) -> str:
    """
    Build deterministic recruiter-readable shortlist reasoning.
    """

    semantic_score = bounded_float(candidate.get("semantic_score", 0.0), 0.0, 1.0)
    confidence = get_confidence_score(candidate)
    hallucination_risk = bounded_float(
        candidate.get("hallucination_risk", 0.0),
        0.0,
        1.0,
    )
    evidence_quality = bounded_float(
        candidate.get("evidence_quality", candidate.get("evidence_coverage", 0.0)),
        0.0,
        1.0,
    )

    if semantic_score >= 0.80:
        retrieval_text = "strong semantic alignment with the job description"
    elif semantic_score >= 0.60:
        retrieval_text = "moderate semantic alignment with the job description"
    else:
        retrieval_text = "limited semantic alignment with the job description"

    if evidence_quality >= 0.75:
        evidence_text = "high evidence quality"
    elif evidence_quality >= 0.45:
        evidence_text = "usable evidence quality"
    else:
        evidence_text = "weak evidence quality"

    if confidence >= 0.80:
        confidence_text = "high confidence"
    elif confidence >= 0.45:
        confidence_text = "moderate confidence"
    else:
        confidence_text = "low confidence"

    if hallucination_risk <= 0.10:
        safety_text = "low hallucination risk"
    elif hallucination_risk <= 0.30:
        safety_text = "manageable hallucination risk"
    else:
        safety_text = "elevated hallucination risk requiring recruiter review"

    return (
        f"{bucket}: {retrieval_text}, {evidence_text}, "
        f"{confidence_text}, and {safety_text}."
    )


def _build_shortlist_item(candidate: Dict[str, Any],
                          bucket: str) -> Dict[str, Any]:
    return normalize_shortlist_item({
        **candidate,
        "ranking_position": get_ranking_position(candidate),
        "confidence_score": get_confidence_score(candidate),
        "evidence_quality": bounded_float(
            candidate.get("evidence_quality", candidate.get("evidence_coverage", 0.0)),
            0.0,
            1.0,
        ),
        "bucket": bucket,
        "shortlist_reason": build_shortlist_reason(candidate, bucket),
    })


def generate_shortlist(
    ranked_candidates: List[Dict[str, Any]],
    top_k: int = 10,
    thresholds: Optional[Dict[str, Dict[str, float]]] = None,
    include_weak: bool = False,
    exclude_unsafe: bool = True,
) -> List[Dict[str, Any]]:
    """
    Convert ranked candidates into a recruiter-facing deterministic shortlist.
    """

    if not isinstance(ranked_candidates, list):
        raise TypeError("ranked_candidates must be a list.")

    if top_k < 0:
        raise ValueError("top_k cannot be negative.")

    shortlist_items = []

    for candidate in sort_ranked_candidates(ranked_candidates):
        if not isinstance(candidate, dict):
            raise TypeError("Each ranked candidate must be a dictionary.")

        if exclude_unsafe and should_exclude_candidate(candidate, thresholds):
            continue

        bucket = assign_shortlist_bucket(candidate, thresholds)

        if bucket == WEAK_MATCH and not include_weak:
            continue

        shortlist_items.append(_build_shortlist_item(candidate, bucket))

    shortlist_items = truncate_shortlist(shortlist_items, top_k)

    if not validate_shortlist_output(shortlist_items):
        raise ValueError("Shortlist output failed schema validation.")

    return shortlist_items


def group_shortlist_by_bucket(
    shortlist_items: List[Dict[str, Any]]
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Group already generated shortlist items into recruiter bucket sections.
    """

    grouped = {
        "STRONG_MATCH": [],
        "GOOD_MATCH": [],
        "POTENTIAL_MATCH": [],
        "WEAK_MATCH": [],
    }

    for item in shortlist_items:
        bucket = item.get("bucket", WEAK_MATCH)
        grouped.setdefault(bucket, []).append(item)

    return grouped

