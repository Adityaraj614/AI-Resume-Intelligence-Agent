from core.recruiter.query_utils import (
    apply_top_k,
    build_query_summary,
    format_keyword_list,
    preserve_candidate_order,
)


def test_preserve_candidate_order_uses_ranking_position():
    candidates = [
        {"candidate_id": "resume_002", "ranking_position": 2},
        {"candidate_id": "resume_001", "ranking_position": 1},
    ]

    ordered = preserve_candidate_order(candidates)

    assert [item["candidate_id"] for item in ordered] == ["resume_001", "resume_002"]


def test_apply_top_k_truncates_results():
    assert apply_top_k([1, 2, 3], top_k=2) == [1, 2]


def test_format_keyword_list_is_deterministic():
    assert format_keyword_list(["Python", "ML"]) == "python, ml"


def test_build_query_summary_describes_filters():
    summary = build_query_summary(
        {
            "required_skills": ["Python"],
            "strict_skills": True,
            "min_confidence": 0.85,
            "max_hallucination_risk": "LOW",
            "allowed_buckets": ["STRONG_MATCH"],
            "top_k": 5,
        },
        candidate_count=2,
    )

    assert "strict skills: python" in summary
    assert "confidence >= 0.85" in summary
    assert "allowed buckets: strong_match" in summary
    assert "Found 2 candidates" in summary


def test_build_query_summary_handles_empty_query():
    summary = build_query_summary({}, candidate_count=3)

    assert summary == "Showing all recruiter-safe candidates. Found 3 candidates."

