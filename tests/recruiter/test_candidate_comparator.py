from core.recruiter.candidate_comparator import (
    analyze_ranking_difference,
    analyze_skill_overlap,
    compare_candidates,
    compare_confidence_and_safety,
    compare_missing_skills,
)


def _candidate_a():
    return {
        "candidate_id": "resume_001",
        "candidate_name": "Asha Rao",
        "ranking_position": 1,
        "final_score": 8.9,
        "semantic_score": 0.88,
        "confidence_score": 0.91,
        "hallucination_risk": 0.05,
        "evidence_quality": 0.86,
        "recommendation": "Strong Match",
        "bucket": "STRONG_MATCH",
        "extracted_skills": ["Python", "SQL", "TensorFlow"],
        "missing_skills": ["Docker"],
        "strengths": ["ML projects", "Python evidence"],
        "weaknesses": ["No Docker evidence"],
    }


def _candidate_b():
    return {
        "candidate_id": "resume_002",
        "candidate_name": "Ben Lee",
        "ranking_position": 2,
        "final_score": 7.6,
        "semantic_score": 0.74,
        "confidence_score": 0.80,
        "hallucination_risk": 0.12,
        "evidence_quality": 0.70,
        "recommendation": "Moderate Match",
        "bucket": "GOOD_MATCH",
        "extracted_skills": ["Python", "SQL", "Docker"],
        "missing_skills": ["TensorFlow"],
        "strengths": ["Backend coverage"],
        "weaknesses": ["Less ML evidence"],
    }


def test_analyze_skill_overlap_returns_shared_and_unique_skills():
    overlap = analyze_skill_overlap(_candidate_a(), _candidate_b())

    assert overlap["shared_skills"] == ["python", "sql"]
    assert overlap["candidate_a_unique_skills"] == ["tensorflow"]
    assert overlap["candidate_b_unique_skills"] == ["docker"]


def test_compare_missing_skills_returns_candidate_specific_gaps():
    comparison = compare_missing_skills(_candidate_a(), _candidate_b())

    assert comparison["candidate_a_missing_only"] == ["docker"]
    assert comparison["candidate_b_missing_only"] == ["tensorflow"]
    assert comparison["candidate_a_missing_count"] == 1


def test_compare_confidence_and_safety_prefers_safer_evidence_backed_candidate():
    safety = compare_confidence_and_safety(_candidate_a(), _candidate_b())

    assert safety["confidence"]["preferred"] == "candidate_a"
    assert safety["evidence_quality"]["preferred"] == "candidate_a"
    assert safety["hallucination_risk"]["preferred"] == "candidate_a"


def test_analyze_ranking_difference_explains_upstream_rank_and_score_delta():
    ranking = analyze_ranking_difference(_candidate_a(), _candidate_b())

    assert ranking["higher_ranked"] == "candidate_a"
    assert ranking["ranking_delta"] == 1
    assert "Candidate A ranks higher upstream" in ranking["ranking_explanation"]


def test_compare_candidates_returns_recruiter_safe_structured_output():
    comparison = compare_candidates(_candidate_a(), _candidate_b())

    assert comparison["candidate_a"]["candidate_id"] == "resume_001"
    assert comparison["candidate_b"]["candidate_id"] == "resume_002"
    assert "Asha Rao is ranked higher" in comparison["comparison_summary"]
    assert comparison["skill_overlap"]["shared_skills"] == ["python", "sql"]


def test_compare_candidates_handles_missing_fields_safely():
    comparison = compare_candidates({"candidate_id": "a"}, {"candidate_id": "b"})

    assert comparison["candidate_a"]["skills"] == []
    assert comparison["candidate_b"]["missing_skills"] == []
    assert comparison["ranking_analysis"]["higher_ranked"] == "tie"

