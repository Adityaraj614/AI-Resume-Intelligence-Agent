from typing import Any, Dict, Iterable, List, Optional

from core.recruiter.filter_rules import normalize_keywords
from core.recruiter.shortlist_utils import sort_ranked_candidates


def preserve_candidate_order(candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Preserve upstream ranking order with deterministic tie-breakers.
    """

    return sort_ranked_candidates(candidates)


def apply_top_k(candidates: List[Dict[str, Any]],
                top_k: Optional[int] = None) -> List[Dict[str, Any]]:
    if top_k is None:
        return candidates

    if top_k < 0:
        raise ValueError("top_k cannot be negative.")

    return candidates[:top_k]


def format_keyword_list(values: Optional[Iterable[Any]]) -> str:
    keywords = normalize_keywords(values)

    if not keywords:
        return ""

    return ", ".join(keywords)


def build_query_summary(query: Dict[str, Any],
                        candidate_count: int) -> str:
    """
    Build a deterministic recruiter-readable query summary.
    """

    parts = []

    skills = format_keyword_list(query.get("required_skills"))
    if skills:
        match_type = "strict" if query.get("strict_skills", True) else "partial"
        parts.append(f"{match_type} skills: {skills}")

    if query.get("min_confidence") is not None:
        parts.append(f"confidence >= {float(query['min_confidence']):.2f}")

    if query.get("max_hallucination_risk") is not None:
        parts.append(
            f"hallucination risk <= {query['max_hallucination_risk']}"
        )

    if query.get("min_evidence_quality") is not None:
        parts.append(f"evidence quality >= {float(query['min_evidence_quality']):.2f}")

    buckets = format_keyword_list(query.get("allowed_buckets"))
    if buckets:
        parts.append(f"allowed buckets: {buckets}")

    excluded_buckets = format_keyword_list(query.get("excluded_buckets"))
    if excluded_buckets:
        parts.append(f"excluded buckets: {excluded_buckets}")

    recommendations = format_keyword_list(query.get("allowed_recommendations"))
    if recommendations:
        parts.append(f"recommendations: {recommendations}")

    if query.get("min_years") is not None:
        parts.append(f"experience >= {float(query['min_years']):g} years")

    if query.get("max_years") is not None:
        parts.append(f"experience <= {float(query['max_years']):g} years")

    education = format_keyword_list(query.get("education_keywords"))
    if education:
        parts.append(f"education contains: {education}")

    if query.get("top_k") is not None:
        parts.append(f"top {int(query['top_k'])}")

    if not parts:
        return f"Showing all recruiter-safe candidates. Found {candidate_count} candidates."

    return f"Showing candidates with {'; '.join(parts)}. Found {candidate_count} candidates."

