from core.recruiter.filter_schema import validate_filter_result
from core.recruiter.recruiter_query_engine import (
    get_top_candidates,
    query_candidates,
)


def _candidates():
    return [
        {
            "candidate_id": "resume_001",
            "candidate_name": "Asha Rao",
            "ranking_position": 1,
            "final_score": 8.9,
            "confidence_score": 0.91,
            "hallucination_risk": 0.05,
            "evidence_quality": 0.86,
            "recommendation": "Strong Match",
            "bucket": "STRONG_MATCH",
            "shortlist_reason": "Strong match.",
            "extracted_skills": ["Python", "Machine Learning"],
            "years_experience": 4,
            "education": "B.Tech Computer Science",
        },
        {
            "candidate_id": "resume_002",
            "candidate_name": "Ben Lee",
            "ranking_position": 2,
            "final_score": 7.4,
            "confidence_score": 0.78,
            "hallucination_risk": 0.12,
            "evidence_quality": 0.70,
            "recommendation": "Moderate Match",
            "bucket": "GOOD_MATCH",
            "shortlist_reason": "Good match.",
            "extracted_skills": ["Python", "SQL"],
            "years_experience": 2,
            "education": "B.Sc Statistics",
        },
        {
            "candidate_id": "resume_003",
            "candidate_name": "Chen Wu",
            "ranking_position": 3,
            "final_score": 5.5,
            "confidence_score": 0.52,
            "hallucination_risk": 0.25,
            "evidence_quality": 0.50,
            "recommendation": "Weak Match",
            "bucket": "POTENTIAL_MATCH",
            "shortlist_reason": "Potential match.",
            "extracted_skills": ["Java"],
            "years_experience": 1,
            "education": "Diploma Software Engineering",
        },
    ]


def test_query_candidates_returns_structured_output():
    result = query_candidates(
        _candidates(),
        required_skills=["python"],
        min_confidence=0.75,
        allowed_buckets=["STRONG_MATCH", "GOOD_MATCH"],
    )

    assert validate_filter_result(result) is True
    assert result["candidate_count"] == 2
    assert [item["candidate_id"] for item in result["filtered_candidates"]] == [
        "resume_001",
        "resume_002",
    ]


def test_query_candidates_supports_empty_results():
    result = query_candidates(
        _candidates(),
        required_skills=["rust"],
    )

    assert result["candidate_count"] == 0
    assert result["filtered_candidates"] == []
    assert "Found 0 candidates" in result["query_summary"]


def test_query_candidates_applies_top_k_after_filters():
    result = query_candidates(
        _candidates(),
        top_k=1,
        required_skills=["python"],
        strict_skills=True,
    )

    assert result["candidate_count"] == 1
    assert result["filtered_candidates"][0]["candidate_id"] == "resume_001"


def test_query_candidates_filters_by_education_and_experience():
    result = query_candidates(
        _candidates(),
        education_keywords=["statistics"],
        min_years=2,
        max_years=3,
    )

    assert [item["candidate_id"] for item in result["filtered_candidates"]] == [
        "resume_002",
    ]


def test_query_candidates_is_deterministic():
    first = query_candidates(
        _candidates(),
        max_hallucination_risk="MEDIUM",
        min_evidence_quality=0.50,
    )
    second = query_candidates(
        _candidates(),
        max_hallucination_risk="MEDIUM",
        min_evidence_quality=0.50,
    )

    assert first == second


def test_get_top_candidates_preserves_ranking_order():
    result = get_top_candidates(list(reversed(_candidates())), top_k=2)

    assert [item["candidate_id"] for item in result["filtered_candidates"]] == [
        "resume_001",
        "resume_002",
    ]
