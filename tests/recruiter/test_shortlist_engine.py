from core.recruiter.shortlist_engine import (
    build_shortlist_reason,
    generate_shortlist,
    group_shortlist_by_bucket,
)
from core.recruiter.shortlist_rules import (
    GOOD_MATCH,
    STRONG_MATCH,
    WEAK_MATCH,
)
from core.recruiter.shortlist_schema import validate_shortlist_output


def _ranked_candidates():
    return [
        {
            "rank": 1,
            "candidate_id": "resume_001",
            "candidate_name": "Asha Rao",
            "final_score": 8.9,
            "confidence": 0.90,
            "hallucination_risk": 0.02,
            "evidence_quality": 0.88,
            "semantic_score": 0.90,
            "recommendation": "Strong Match",
            "ranking_reason": "Strong retrieval alignment.",
        },
        {
            "rank": 2,
            "candidate_id": "resume_002",
            "candidate_name": "Ben Lee",
            "final_score": 7.4,
            "confidence": 0.72,
            "hallucination_risk": 0.10,
            "evidence_quality": 0.66,
            "semantic_score": 0.76,
            "recommendation": "Moderate Match",
            "ranking_reason": "Moderate retrieval alignment.",
        },
        {
            "rank": 3,
            "candidate_id": "resume_unsafe",
            "candidate_name": "Casey Noor",
            "final_score": 9.4,
            "confidence": 0.91,
            "hallucination_risk": 0.70,
            "evidence_quality": 0.80,
            "semantic_score": 0.92,
            "recommendation": "Strong Match",
            "warning_flags": ["high_hallucination_risk"],
            "ranking_reason": "Unsafe analysis.",
        },
        {
            "rank": 4,
            "candidate_id": "resume_weak",
            "candidate_name": "Dev Kim",
            "final_score": 4.2,
            "confidence": 0.30,
            "hallucination_risk": 0.10,
            "evidence_quality": 0.35,
            "semantic_score": 0.40,
            "recommendation": "Weak Match",
            "ranking_reason": "Weak evidence.",
        },
    ]


def test_generate_shortlist_returns_recruiter_schema():
    shortlist = generate_shortlist(_ranked_candidates(), top_k=10)

    assert validate_shortlist_output(shortlist) is True
    assert shortlist[0]["candidate_id"] == "resume_001"
    assert shortlist[0]["bucket"] == STRONG_MATCH
    assert shortlist[0]["confidence_score"] == 0.90


def test_generate_shortlist_excludes_unsafe_candidates_by_default():
    shortlist = generate_shortlist(_ranked_candidates(), top_k=10)

    assert "resume_unsafe" not in {
        item["candidate_id"]
        for item in shortlist
    }


def test_generate_shortlist_filters_weak_candidates_by_default():
    shortlist = generate_shortlist(_ranked_candidates(), top_k=10)

    assert "resume_weak" not in {
        item["candidate_id"]
        for item in shortlist
    }


def test_generate_shortlist_can_include_weak_candidates_when_requested():
    shortlist = generate_shortlist(
        _ranked_candidates(),
        top_k=10,
        include_weak=True,
    )

    weak_item = [
        item
        for item in shortlist
        if item["candidate_id"] == "resume_weak"
    ][0]

    assert weak_item["bucket"] == WEAK_MATCH


def test_generate_shortlist_applies_top_k_truncation():
    shortlist = generate_shortlist(_ranked_candidates(), top_k=1)

    assert len(shortlist) == 1
    assert shortlist[0]["candidate_id"] == "resume_001"


def test_generate_shortlist_is_deterministic():
    first = generate_shortlist(_ranked_candidates(), top_k=10)
    second = generate_shortlist(_ranked_candidates(), top_k=10)

    assert first == second


def test_generate_shortlist_handles_empty_candidates():
    assert generate_shortlist([], top_k=10) == []


def test_build_shortlist_reason_is_recruiter_readable():
    reason = build_shortlist_reason(_ranked_candidates()[0], STRONG_MATCH)

    assert "strong semantic alignment" in reason
    assert "high evidence quality" in reason
    assert "low hallucination risk" in reason


def test_group_shortlist_by_bucket_groups_generated_items():
    shortlist = generate_shortlist(_ranked_candidates(), top_k=10)
    grouped = group_shortlist_by_bucket(shortlist)

    assert grouped[STRONG_MATCH][0]["candidate_id"] == "resume_001"
    assert grouped[GOOD_MATCH][0]["candidate_id"] == "resume_002"
