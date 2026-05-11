from typing import Any, Dict, Iterable, List, Optional

from core.recruiter.shortlist_utils import (
    bounded_float,
    get_confidence_score,
)


HALLUCINATION_RISK_LEVELS = {
    "LOW": 0.10,
    "MEDIUM": 0.30,
    "HIGH": 0.60,
}


def normalize_text(value: Any) -> str:
    return str(value or "").strip().lower()


def normalize_keywords(values: Optional[Iterable[Any]]) -> List[str]:
    if not values:
        return []

    return [
        normalize_text(value)
        for value in values
        if normalize_text(value)
    ]


def normalize_candidate_skills(candidate: Dict[str, Any]) -> List[str]:
    skills = candidate.get("extracted_skills", candidate.get("skills", []))

    if isinstance(skills, str):
        skills = [skills]

    if not isinstance(skills, list):
        return []

    return normalize_keywords(skills)


def skill_matches(candidate: Dict[str, Any],
                  required_skills: Optional[Iterable[Any]],
                  strict: bool = True) -> bool:
    """
    Match required skills against extracted candidate skills.
    """

    required = normalize_keywords(required_skills)

    if not required:
        return True

    candidate_skills = normalize_candidate_skills(candidate)

    if not candidate_skills:
        return False

    if strict:
        return all(skill in candidate_skills for skill in required)

    return all(
        any(
            required_skill in candidate_skill
            or candidate_skill in required_skill
            for candidate_skill in candidate_skills
        )
        for required_skill in required
    )


def confidence_matches(candidate: Dict[str, Any],
                       min_confidence: Optional[float] = None) -> bool:
    if min_confidence is None:
        return True

    return get_confidence_score(candidate) >= bounded_float(min_confidence, 0.0, 1.0)


def hallucination_risk_matches(candidate: Dict[str, Any],
                               max_hallucination_risk: Optional[Any] = None) -> bool:
    if max_hallucination_risk is None:
        return True

    if isinstance(max_hallucination_risk, str):
        threshold = HALLUCINATION_RISK_LEVELS.get(
            max_hallucination_risk.strip().upper()
        )

        if threshold is None:
            raise ValueError("Unknown hallucination risk level.")
    else:
        threshold = bounded_float(max_hallucination_risk, 0.0, 1.0)

    risk = bounded_float(candidate.get("hallucination_risk", 0.0), 0.0, 1.0)

    return risk <= threshold


def evidence_quality_matches(candidate: Dict[str, Any],
                             min_evidence_quality: Optional[float] = None) -> bool:
    if min_evidence_quality is None:
        return True

    evidence_quality = bounded_float(
        candidate.get("evidence_quality", candidate.get("evidence_coverage", 0.0)),
        0.0,
        1.0,
    )

    return evidence_quality >= bounded_float(min_evidence_quality, 0.0, 1.0)


def recommendation_matches(candidate: Dict[str, Any],
                           allowed_recommendations: Optional[Iterable[Any]] = None) -> bool:
    allowed = normalize_keywords(allowed_recommendations)

    if not allowed:
        return True

    return normalize_text(candidate.get("recommendation", "")) in allowed


def bucket_matches(candidate: Dict[str, Any],
                   allowed_buckets: Optional[Iterable[Any]] = None,
                   excluded_buckets: Optional[Iterable[Any]] = None) -> bool:
    bucket = normalize_text(candidate.get("bucket", ""))
    allowed = normalize_keywords(allowed_buckets)
    excluded = normalize_keywords(excluded_buckets)

    if allowed and bucket not in allowed:
        return False

    if excluded and bucket in excluded:
        return False

    return True


def experience_matches(candidate: Dict[str, Any],
                       min_years: Optional[float] = None,
                       max_years: Optional[float] = None) -> bool:
    years = candidate.get("years_experience")

    if years is None:
        return min_years is None and max_years is None

    years = float(years)

    if min_years is not None and years < float(min_years):
        return False

    if max_years is not None and years > float(max_years):
        return False

    return True


def education_matches(candidate: Dict[str, Any],
                      education_keywords: Optional[Iterable[Any]] = None) -> bool:
    keywords = normalize_keywords(education_keywords)

    if not keywords:
        return True

    education = candidate.get("education", "")

    if isinstance(education, list):
        education_text = " ".join(str(item) for item in education)
    elif isinstance(education, dict):
        education_text = " ".join(str(value) for value in education.values())
    else:
        education_text = str(education)

    normalized_education = normalize_text(education_text)

    return all(keyword in normalized_education for keyword in keywords)

