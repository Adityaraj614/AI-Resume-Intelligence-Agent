import pytest

from core.recruiter.filter_rules import (
    bucket_matches,
    education_matches,
    evidence_quality_matches,
    experience_matches,
    hallucination_risk_matches,
    recommendation_matches,
    skill_matches,
)


def _candidate(**overrides):
    candidate = {
        "candidate_id": "resume_001",
        "extracted_skills": ["Python", "Machine Learning", "FAISS"],
        "confidence_score": 0.88,
        "hallucination_risk": 0.08,
        "evidence_quality": 0.82,
        "recommendation": "Strong Match",
        "bucket": "STRONG_MATCH",
        "years_experience": 3,
        "education": "B.Tech Computer Science",
    }
    candidate.update(overrides)
    return candidate


def test_skill_matches_is_case_insensitive():
    assert skill_matches(_candidate(), ["python", "machine learning"]) is True


def test_skill_matches_supports_partial_matching():
    assert skill_matches(_candidate(), ["machine"], strict=False) is True
    assert skill_matches(_candidate(), ["machine"], strict=True) is False


def test_skill_matches_handles_missing_skills_safely():
    assert skill_matches({}, ["python"]) is False


def test_hallucination_risk_matches_named_levels():
    assert hallucination_risk_matches(_candidate(hallucination_risk=0.09), "LOW") is True
    assert hallucination_risk_matches(_candidate(hallucination_risk=0.20), "LOW") is False


def test_hallucination_risk_rejects_unknown_level():
    with pytest.raises(ValueError):
        hallucination_risk_matches(_candidate(), "UNKNOWN")


def test_evidence_quality_matches_minimum():
    assert evidence_quality_matches(_candidate(evidence_quality=0.70), 0.60) is True
    assert evidence_quality_matches(_candidate(evidence_quality=0.40), 0.60) is False


def test_recommendation_and_bucket_matching():
    assert recommendation_matches(_candidate(), ["strong match"]) is True
    assert bucket_matches(_candidate(), allowed_buckets=["STRONG_MATCH"]) is True
    assert bucket_matches(_candidate(), excluded_buckets=["STRONG_MATCH"]) is False


def test_experience_matches_range_and_missing_fields():
    assert experience_matches(_candidate(years_experience=4), min_years=2, max_years=5) is True
    assert experience_matches(_candidate(years_experience=1), min_years=2) is False
    assert experience_matches({}, min_years=1) is False


def test_education_matches_keywords():
    assert education_matches(_candidate(), ["computer science"]) is True
    assert education_matches(_candidate(), ["mba"]) is False

