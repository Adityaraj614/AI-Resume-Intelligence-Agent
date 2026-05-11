from core.ranking.ranking_utils import (
    apply_confidence_penalty,
    apply_hallucination_penalty,
    calculate_evidence_quality,
    calculate_ranking_priority,
    calculate_recommendation_quality,
    normalize_final_rankings,
    safety_priority_bucket,
    sort_candidates_by_priority,
)


def test_apply_confidence_penalty_reduces_low_confidence_score():
    high_confidence = apply_confidence_penalty(8.0, 0.9)
    low_confidence = apply_confidence_penalty(8.0, 0.3)

    assert high_confidence > low_confidence
    assert 0 <= low_confidence <= 10


def test_apply_hallucination_penalty_reduces_priority():
    safe_priority = apply_hallucination_penalty(8.0, 0.0)
    unsafe_priority = apply_hallucination_penalty(8.0, 0.5)

    assert safe_priority == 8.0
    assert unsafe_priority < safe_priority


def test_calculate_evidence_quality_is_bounded():
    evidence_quality = calculate_evidence_quality({
        "semantic_score": 0.85,
        "confidence": 0.90,
        "hallucination_risk": 0.0,
    })

    assert 0 <= evidence_quality <= 1
    assert evidence_quality > 0.8


def test_sort_candidates_by_priority_is_deterministic():
    candidates = [
        {
            "candidate_id": "resume_002",
            "ranking_priority": 7.5,
            "final_score": 8.0,
            "confidence": 0.8,
            "hallucination_risk": 0.0,
        },
        {
            "candidate_id": "resume_001",
            "ranking_priority": 7.5,
            "final_score": 8.0,
            "confidence": 0.8,
            "hallucination_risk": 0.0,
        },
    ]

    sorted_candidates = sort_candidates_by_priority(candidates)

    assert sorted_candidates[0]["candidate_id"] == "resume_001"
    assert sorted_candidates[1]["candidate_id"] == "resume_002"


def test_calculate_ranking_priority_penalizes_hallucination_risk():
    safe_priority = calculate_ranking_priority({
        "final_score": 8.0,
        "confidence": 0.8,
        "semantic_score": 0.8,
        "hallucination_risk": 0.0,
    })
    unsafe_priority = calculate_ranking_priority({
        "final_score": 8.0,
        "confidence": 0.8,
        "semantic_score": 0.8,
        "hallucination_risk": 0.6,
    })

    assert safe_priority > unsafe_priority


def test_calculate_recommendation_quality_is_bounded_and_label_based():
    strong_quality = calculate_recommendation_quality({
        "recommendation": "Strong Match",
    })
    weak_quality = calculate_recommendation_quality({
        "recommendation": "Weak Match",
    })

    assert strong_quality > weak_quality
    assert 0 <= weak_quality <= 1


def test_safety_priority_bucket_groups_risky_candidates_after_safe_candidates():
    safe_bucket = safety_priority_bucket({
        "hallucination_risk": 0.0,
        "evidence_quality": 0.80,
        "warning_flags": [],
    })
    unsafe_bucket = safety_priority_bucket({
        "hallucination_risk": 0.40,
        "evidence_quality": 0.90,
        "warning_flags": ["unsupported_claims_detected"],
    })

    assert safe_bucket < unsafe_bucket


def test_normalize_final_rankings_assigns_sequential_ranks():
    rankings = normalize_final_rankings([
        {"candidate_id": "resume_001"},
        {"candidate_id": "resume_002"},
    ])

    assert rankings[0]["rank"] == 1
    assert rankings[1]["rank"] == 2
