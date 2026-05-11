from core.analytics.insight_generator import (
    build_analytics_report,
    generate_recruiter_insights,
    generate_recruiter_insights_from_analytics,
)


def _candidates():
    return [
        {
            "candidate_id": "resume_001",
            "ranking_position": 1,
            "final_score": 9.0,
            "confidence_score": 0.90,
            "hallucination_risk": 0.05,
            "evidence_quality": 0.85,
            "bucket": "STRONG_MATCH",
            "extracted_skills": ["Python", "SQL"],
            "missing_skills": ["Docker"],
        },
        {
            "candidate_id": "resume_002",
            "ranking_position": 2,
            "final_score": 5.0,
            "confidence_score": 0.40,
            "hallucination_risk": 0.35,
            "evidence_quality": 0.30,
            "bucket": "WEAK_MATCH",
            "extracted_skills": ["Python"],
            "missing_skills": ["Docker"],
        },
    ]


def test_generate_recruiter_insights_is_deterministic():
    first = generate_recruiter_insights(_candidates())
    second = generate_recruiter_insights(_candidates())

    assert first == second
    assert "1 of 2 candidates are in the STRONG_MATCH bucket." in first
    assert "1 candidates show elevated hallucination risk." in first


def test_generate_recruiter_insights_handles_empty_candidates():
    assert generate_recruiter_insights([]) == [
        "No candidates available for analytics."
    ]


def test_generate_recruiter_insights_from_existing_analytics():
    insights = generate_recruiter_insights_from_analytics({
        "candidate_pool_summary": {"total_candidates": 1},
        "bucket_analytics": {"strong_match_count": 0},
        "confidence_analytics": {"average_confidence": 0.9, "low_confidence_count": 0},
        "hallucination_analytics": {"high_risk_count": 0},
        "evidence_analytics": {"strong_evidence_count": 1, "weak_evidence_count": 0},
        "skill_analytics": {"top_skills": [{"skill": "python", "count": 1}]},
        "missing_skill_analytics": {"top_missing_skills": []},
    })

    assert "Candidate pool has high average confidence." in insights
    assert "python is the most common retrieved skill across candidates." in insights


def test_build_analytics_report_includes_insights():
    report = build_analytics_report(_candidates())

    assert "recruiter_insights" in report
    assert report["candidate_pool_summary"]["total_candidates"] == 2

