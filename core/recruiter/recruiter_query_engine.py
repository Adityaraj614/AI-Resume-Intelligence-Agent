from typing import Any, Dict, List, Optional

from core.recruiter.candidate_filter import filter_candidates
from core.recruiter.filter_schema import (
    build_filter_result,
    normalize_filter_query,
    validate_filter_result,
)
from core.recruiter.query_utils import (
    apply_top_k,
    build_query_summary,
)


def query_candidates(candidates: List[Dict[str, Any]],
                     top_k: Optional[int] = None,
                     **query_options: Any) -> Dict[str, Any]:
    """
    Compose recruiter-safe filters and return a structured query response.
    """

    query = normalize_filter_query({
        **query_options,
        "top_k": top_k,
    })
    filtered_candidates = filter_candidates(
        candidates,
        required_skills=query["required_skills"],
        strict_skills=query["strict_skills"],
        min_confidence=query["min_confidence"],
        max_hallucination_risk=query["max_hallucination_risk"],
        min_evidence_quality=query["min_evidence_quality"],
        allowed_recommendations=query["allowed_recommendations"],
        allowed_buckets=query["allowed_buckets"],
        excluded_buckets=query["excluded_buckets"],
        min_years=query["min_years"],
        max_years=query["max_years"],
        education_keywords=query["education_keywords"],
    )
    filtered_candidates = apply_top_k(filtered_candidates, query["top_k"])
    query_summary = build_query_summary(query, len(filtered_candidates))
    result = build_filter_result(query_summary, filtered_candidates)

    if not validate_filter_result(result):
        raise ValueError("Recruiter query result failed schema validation.")

    return result


def get_top_candidates(candidates: List[Dict[str, Any]],
                       top_k: int = 10) -> Dict[str, Any]:
    """
    Return top candidates while preserving upstream ranking order.
    """

    return query_candidates(candidates, top_k=top_k)

