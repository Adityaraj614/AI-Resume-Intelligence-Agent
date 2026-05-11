from core.recruiter.comparison_utils import (
    build_candidate_summary,
    compare_numeric_signal,
    normalize_candidate_skills,
    normalize_list_field,
    sort_candidates_for_comparison,
)


def test_normalize_list_field_is_deterministic_and_lowercase():
    assert normalize_list_field(["Python", "python", " SQL "]) == ["python", "sql"]


def test_normalize_candidate_skills_uses_safe_missing_default():
    assert normalize_candidate_skills({}) == []


def test_build_candidate_summary_normalizes_common_fields():
    summary = build_candidate_summary({
        "candidate_id": " resume_001 ",
        "candidate_name": " Asha ",
        "rank": 2,
        "final_score": 91.2,
        "confidence": 0.9,
        "hallucination_risk": 0.05,
        "evidence_quality": 0.8,
        "extracted_skills": ["Python"],
    })

    assert summary["candidate_id"] == "resume_001"
    assert summary["candidate_name"] == "Asha"
    assert summary["ranking_position"] == 2
    assert summary["final_score"] == 9.12
    assert summary["confidence_score"] == 0.9
    assert summary["skills"] == ["python"]


def test_compare_numeric_signal_supports_lower_is_better():
    comparison = compare_numeric_signal(
        {"risk": 0.1},
        {"risk": 0.3},
        "risk",
        higher_is_better=False,
    )

    assert comparison["preferred"] == "candidate_a"
    assert comparison["delta"] == -0.2


def test_sort_candidates_for_comparison_preserves_upstream_order():
    candidates = [
        {"candidate_id": "resume_002", "ranking_position": 2},
        {"candidate_id": "resume_001", "ranking_position": 1},
    ]

    ordered = sort_candidates_for_comparison(candidates)

    assert [candidate["candidate_id"] for candidate in ordered] == [
        "resume_001",
        "resume_002",
    ]

