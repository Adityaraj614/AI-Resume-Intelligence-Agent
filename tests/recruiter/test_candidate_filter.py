from core.recruiter.candidate_filter import (
    filter_by_bucket,
    filter_by_confidence,
    filter_by_education,
    filter_by_experience,
    filter_by_recommendation,
    filter_by_skills,
    filter_candidates,
)


def _candidates():
    return [
        {
            "candidate_id": "resume_001",
            "ranking_position": 1,
            "extracted_skills": ["Python", "Machine Learning"],
            "confidence_score": 0.90,
            "hallucination_risk": 0.05,
            "evidence_quality": 0.85,
            "recommendation": "Strong Match",
            "bucket": "STRONG_MATCH",
            "years_experience": 4,
            "education": "B.Tech Computer Science",
        },
        {
            "candidate_id": "resume_002",
            "ranking_position": 2,
            "extracted_skills": ["Python", "SQL"],
            "confidence_score": 0.72,
            "hallucination_risk": 0.18,
            "evidence_quality": 0.66,
            "recommendation": "Moderate Match",
            "bucket": "GOOD_MATCH",
            "years_experience": 2,
            "education": "B.Sc Statistics",
        },
        {
            "candidate_id": "resume_003",
            "ranking_position": 3,
            "extracted_skills": [],
            "confidence_score": 0.40,
            "hallucination_risk": 0.45,
            "evidence_quality": 0.30,
            "recommendation": "Weak Match",
            "bucket": "WEAK_MATCH",
            "years_experience": 1,
            "education": "",
        },
    ]


def test_filter_by_skills_strict_and_partial():
    strict_results = filter_by_skills(_candidates(), ["machine"], strict=True)
    partial_results = filter_by_skills(_candidates(), ["machine"], strict=False)

    assert strict_results == []
    assert [item["candidate_id"] for item in partial_results] == ["resume_001"]


def test_filter_by_confidence_combines_safety_and_evidence():
    results = filter_by_confidence(
        _candidates(),
        min_confidence=0.70,
        max_hallucination_risk=0.20,
        min_evidence_quality=0.60,
    )

    assert [item["candidate_id"] for item in results] == ["resume_001", "resume_002"]


def test_filter_by_recommendation_and_bucket():
    recommendation_results = filter_by_recommendation(
        _candidates(),
        ["Moderate Match"],
    )
    bucket_results = filter_by_bucket(
        _candidates(),
        excluded_buckets=["WEAK_MATCH"],
    )

    assert [item["candidate_id"] for item in recommendation_results] == ["resume_002"]
    assert [item["candidate_id"] for item in bucket_results] == ["resume_001", "resume_002"]


def test_filter_by_experience_and_education():
    experience_results = filter_by_experience(_candidates(), min_years=2)
    education_results = filter_by_education(_candidates(), ["statistics"])

    assert [item["candidate_id"] for item in experience_results] == ["resume_001", "resume_002"]
    assert [item["candidate_id"] for item in education_results] == ["resume_002"]


def test_filter_candidates_composes_multiple_filters_and_preserves_order():
    results = filter_candidates(
        _candidates(),
        required_skills=["python"],
        min_confidence=0.70,
        max_hallucination_risk="MEDIUM",
        allowed_buckets=["STRONG_MATCH", "GOOD_MATCH"],
        min_years=2,
    )

    assert [item["candidate_id"] for item in results] == ["resume_001", "resume_002"]


def test_filter_candidates_handles_empty_candidates():
    assert filter_candidates([], required_skills=["python"]) == []

