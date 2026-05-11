from core.recruiter.comparison_schema import (
    normalize_comparison_output,
    normalize_multi_comparison_output,
    validate_candidate_summary,
    validate_comparison_output,
    validate_multi_comparison_output,
)
from core.recruiter.comparison_utils import build_candidate_summary


def test_validate_candidate_summary_accepts_normalized_summary():
    summary = build_candidate_summary({
        "candidate_id": "resume_001",
        "final_score": 8.2,
        "semantic_score": 0.8,
        "confidence_score": 0.9,
        "hallucination_risk": 0.1,
        "evidence_quality": 0.8,
    })

    assert validate_candidate_summary(summary) is True


def test_validate_comparison_output_rejects_missing_keys():
    assert validate_comparison_output({"candidate_a": {}}) is False


def test_normalize_comparison_output_builds_candidate_summaries():
    normalized = normalize_comparison_output({
        "candidate_a": {"candidate_id": "a", "final_score": 8.0},
        "candidate_b": {"candidate_id": "b", "final_score": 7.0},
        "comparison_summary": "A ranks higher.",
        "skill_overlap": {},
        "missing_skill_comparison": {},
        "confidence_and_safety": {},
        "ranking_analysis": {},
    })

    assert normalized["candidate_a"]["candidate_id"] == "a"
    assert normalized["candidate_b"]["final_score"] == 7.0


def test_validate_multi_comparison_output_accepts_empty_comparison():
    normalized = normalize_multi_comparison_output({
        "candidate_count": 0,
        "ranking_overview": [],
        "comparison_table": [],
        "skill_distribution": {},
        "strength_distribution": {},
        "comparison_summary": "No candidates available for comparison.",
    })

    assert validate_multi_comparison_output(normalized) is True


def test_validate_multi_comparison_output_rejects_count_mismatch():
    normalized = normalize_multi_comparison_output({
        "candidate_count": 2,
        "ranking_overview": [],
        "comparison_table": [],
        "skill_distribution": {},
        "strength_distribution": {},
        "comparison_summary": "Mismatch.",
    })

    assert validate_multi_comparison_output(normalized) is False

