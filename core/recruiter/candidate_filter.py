from typing import Any, Dict, Iterable, List, Optional

from core.recruiter.filter_rules import (
    bucket_matches,
    confidence_matches,
    education_matches,
    evidence_quality_matches,
    experience_matches,
    hallucination_risk_matches,
    recommendation_matches,
    skill_matches,
)
from core.recruiter.query_utils import preserve_candidate_order


def _ensure_candidates(candidates: List[Dict[str, Any]]) -> None:
    if not isinstance(candidates, list):
        raise TypeError("candidates must be a list.")

    for candidate in candidates:
        if not isinstance(candidate, dict):
            raise TypeError("Each candidate must be a dictionary.")


def filter_by_skills(candidates: List[Dict[str, Any]],
                     required_skills: Optional[Iterable[Any]],
                     strict: bool = True) -> List[Dict[str, Any]]:
    _ensure_candidates(candidates)

    return [
        candidate
        for candidate in preserve_candidate_order(candidates)
        if skill_matches(candidate, required_skills, strict=strict)
    ]


def filter_by_confidence(candidates: List[Dict[str, Any]],
                         min_confidence: Optional[float] = None,
                         max_hallucination_risk: Optional[Any] = None,
                         min_evidence_quality: Optional[float] = None) -> List[Dict[str, Any]]:
    _ensure_candidates(candidates)

    return [
        candidate
        for candidate in preserve_candidate_order(candidates)
        if confidence_matches(candidate, min_confidence)
        and hallucination_risk_matches(candidate, max_hallucination_risk)
        and evidence_quality_matches(candidate, min_evidence_quality)
    ]


def filter_by_recommendation(candidates: List[Dict[str, Any]],
                             allowed_recommendations: Optional[Iterable[Any]] = None) -> List[Dict[str, Any]]:
    _ensure_candidates(candidates)

    return [
        candidate
        for candidate in preserve_candidate_order(candidates)
        if recommendation_matches(candidate, allowed_recommendations)
    ]


def filter_by_bucket(candidates: List[Dict[str, Any]],
                     allowed_buckets: Optional[Iterable[Any]] = None,
                     excluded_buckets: Optional[Iterable[Any]] = None) -> List[Dict[str, Any]]:
    _ensure_candidates(candidates)

    return [
        candidate
        for candidate in preserve_candidate_order(candidates)
        if bucket_matches(candidate, allowed_buckets, excluded_buckets)
    ]


def filter_by_experience(candidates: List[Dict[str, Any]],
                         min_years: Optional[float] = None,
                         max_years: Optional[float] = None) -> List[Dict[str, Any]]:
    _ensure_candidates(candidates)

    return [
        candidate
        for candidate in preserve_candidate_order(candidates)
        if experience_matches(candidate, min_years, max_years)
    ]


def filter_by_education(candidates: List[Dict[str, Any]],
                        education_keywords: Optional[Iterable[Any]] = None) -> List[Dict[str, Any]]:
    _ensure_candidates(candidates)

    return [
        candidate
        for candidate in preserve_candidate_order(candidates)
        if education_matches(candidate, education_keywords)
    ]


def filter_candidates(candidates: List[Dict[str, Any]],
                      required_skills: Optional[Iterable[Any]] = None,
                      strict_skills: bool = True,
                      min_confidence: Optional[float] = None,
                      max_hallucination_risk: Optional[Any] = None,
                      min_evidence_quality: Optional[float] = None,
                      allowed_recommendations: Optional[Iterable[Any]] = None,
                      allowed_buckets: Optional[Iterable[Any]] = None,
                      excluded_buckets: Optional[Iterable[Any]] = None,
                      min_years: Optional[float] = None,
                      max_years: Optional[float] = None,
                      education_keywords: Optional[Iterable[Any]] = None) -> List[Dict[str, Any]]:
    """
    Apply deterministic recruiter filters in a fixed composable order.
    """

    _ensure_candidates(candidates)
    filtered = preserve_candidate_order(candidates)
    filtered = filter_by_skills(filtered, required_skills, strict=strict_skills)
    filtered = filter_by_confidence(
        filtered,
        min_confidence=min_confidence,
        max_hallucination_risk=max_hallucination_risk,
        min_evidence_quality=min_evidence_quality,
    )
    filtered = filter_by_recommendation(filtered, allowed_recommendations)
    filtered = filter_by_bucket(filtered, allowed_buckets, excluded_buckets)
    filtered = filter_by_experience(filtered, min_years, max_years)
    filtered = filter_by_education(filtered, education_keywords)

    return filtered

