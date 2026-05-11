from core.recruiter.comparison_engine import (
    build_comparison_table,
    build_multi_comparison_summary,
    build_ranking_overview,
    build_skill_distribution,
    compare_multiple_candidates,
)


def _candidates():
    return [
        {
            "candidate_id": "resume_002",
            "candidate_name": "Ben Lee",
            "ranking_position": 2,
            "final_score": 7.5,
            "semantic_score": 0.74,
            "confidence_score": 0.78,
            "hallucination_risk": 0.12,
            "evidence_quality": 0.70,
            "bucket": "GOOD_MATCH",
            "extracted_skills": ["Python", "Docker"],
            "strengths": ["Backend coverage"],
        },
        {
            "candidate_id": "resume_001",
            "candidate_name": "Asha Rao",
            "ranking_position": 1,
            "final_score": 8.9,
            "semantic_score": 0.88,
            "confidence_score": 0.91,
            "hallucination_risk": 0.05,
            "evidence_quality": 0.86,
            "bucket": "STRONG_MATCH",
            "extracted_skills": ["Python", "TensorFlow"],
            "strengths": ["ML projects"],
        },
        {
            "candidate_id": "resume_003",
            "candidate_name": "Chen Wu",
            "ranking_position": 3,
            "final_score": 6.2,
            "semantic_score": 0.60,
            "confidence_score": 0.60,
            "hallucination_risk": 0.20,
            "evidence_quality": 0.55,
            "bucket": "POTENTIAL_MATCH",
            "extracted_skills": ["SQL"],
            "strengths": ["Data analysis"],
        },
    ]


def test_build_ranking_overview_preserves_upstream_order():
    overview = build_ranking_overview(_candidates())

    assert [item["candidate_id"] for item in overview] == [
        "resume_001",
        "resume_002",
        "resume_003",
    ]


def test_build_comparison_table_contains_normalized_candidate_rows():
    table = build_comparison_table(_candidates())

    assert table[0]["candidate_id"] == "resume_001"
    assert table[0]["skills"] == ["python", "tensorflow"]


def test_build_skill_distribution_maps_skills_to_candidates():
    distribution = build_skill_distribution(_candidates())

    assert distribution["python"] == ["resume_001", "resume_002"]
    assert distribution["sql"] == ["resume_003"]


def test_build_multi_comparison_summary_handles_empty_candidates():
    assert build_multi_comparison_summary([]) == "No candidates available for comparison."


def test_compare_multiple_candidates_returns_structured_deterministic_output():
    first = compare_multiple_candidates(_candidates())
    second = compare_multiple_candidates(_candidates())

    assert first == second
    assert first["candidate_count"] == 3
    assert first["comparison_table"][0]["candidate_id"] == "resume_001"
    assert "Asha Rao is first by upstream ranking" in first["comparison_summary"]


def test_compare_multiple_candidates_handles_empty_list():
    comparison = compare_multiple_candidates([])

    assert comparison["candidate_count"] == 0
    assert comparison["comparison_table"] == []
    assert comparison["skill_distribution"] == {}
