from typing import Any, Dict, List

from core.recruiter.shortlist_utils import (
    bounded_float,
    get_confidence_score,
    get_ranking_position,
    normalize_score_to_10,
)


REQUIRED_QUERY_RESULT_KEYS = (
    "query_summary",
    "candidate_count",
    "filtered_candidates",
)


def normalize_filter_query(query: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize recruiter filter query options without changing intent.
    """

    if not isinstance(query, dict):
        raise TypeError("query must be a dictionary.")

    return {
        "required_skills": query.get("required_skills"),
        "strict_skills": bool(query.get("strict_skills", True)),
        "min_confidence": query.get("min_confidence"),
        "max_hallucination_risk": query.get("max_hallucination_risk"),
        "min_evidence_quality": query.get("min_evidence_quality"),
        "allowed_recommendations": query.get("allowed_recommendations"),
        "allowed_buckets": query.get("allowed_buckets"),
        "excluded_buckets": query.get("excluded_buckets"),
        "min_years": query.get("min_years"),
        "max_years": query.get("max_years"),
        "education_keywords": query.get("education_keywords"),
        "top_k": query.get("top_k"),
    }


def normalize_filtered_candidate(candidate: Dict[str, Any]) -> Dict[str, Any]:
    """
    Preserve candidate fields while normalizing common recruiter-facing values.
    """

    if not isinstance(candidate, dict):
        raise TypeError("candidate must be a dictionary.")

    normalized = dict(candidate)
    candidate_id = str(candidate.get("candidate_id", "unknown_candidate")).strip()
    candidate_id = candidate_id or "unknown_candidate"

    normalized["candidate_id"] = candidate_id
    normalized["candidate_name"] = str(
        candidate.get("candidate_name", candidate_id)
    ).strip() or candidate_id
    normalized["ranking_position"] = get_ranking_position(candidate)
    normalized["final_score"] = normalize_score_to_10(candidate.get("final_score", 0.0))
    normalized["confidence_score"] = get_confidence_score(candidate)
    normalized["hallucination_risk"] = bounded_float(
        candidate.get("hallucination_risk", 0.0),
        0.0,
        1.0,
    )
    normalized["evidence_quality"] = bounded_float(
        candidate.get("evidence_quality", candidate.get("evidence_coverage", 0.0)),
        0.0,
        1.0,
    )

    return normalized


def build_filter_result(query_summary: str,
                        filtered_candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
    normalized_candidates = [
        normalize_filtered_candidate(candidate)
        for candidate in filtered_candidates
    ]

    return {
        "query_summary": query_summary,
        "candidate_count": len(normalized_candidates),
        "filtered_candidates": normalized_candidates,
    }


def validate_filter_result(filter_result: Dict[str, Any]) -> bool:
    if not isinstance(filter_result, dict):
        return False

    for key in REQUIRED_QUERY_RESULT_KEYS:
        if key not in filter_result:
            return False

    if not isinstance(filter_result["query_summary"], str):
        return False

    if filter_result["candidate_count"] != len(filter_result["filtered_candidates"]):
        return False

    previous_position = 0

    for candidate in filter_result["filtered_candidates"]:
        if not isinstance(candidate, dict):
            return False

        if not candidate.get("candidate_id"):
            return False

        if candidate["ranking_position"] < previous_position:
            return False

        if not 0 <= candidate["final_score"] <= 10:
            return False

        if not 0 <= candidate["confidence_score"] <= 1:
            return False

        if not 0 <= candidate["hallucination_risk"] <= 1:
            return False

        if not 0 <= candidate["evidence_quality"] <= 1:
            return False

        previous_position = candidate["ranking_position"]

    return True

