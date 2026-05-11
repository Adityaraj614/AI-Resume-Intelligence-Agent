from core.analytics.tie_breaker import (
    stable_ranking_sort,
    tie_break_key,
    validate_tie_break_order,
)


def _candidates():
    return [
        {
            "candidate_id": "candidate_b",
            "final_score": 8.0,
            "confidence_score": 0.80,
            "hallucination_risk": 0.10,
            "evidence_quality": 0.80,
        },
        {
            "candidate_id": "candidate_a",
            "final_score": 8.0,
            "confidence_score": 0.90,
            "hallucination_risk": 0.10,
            "evidence_quality": 0.80,
        },
        {
            "candidate_id": "candidate_c",
            "final_score": 8.0,
            "confidence_score": 0.90,
            "hallucination_risk": 0.20,
            "evidence_quality": 0.80,
        },
    ]


def test_tie_break_key_prefers_confidence_then_risk_then_evidence_then_id():
    key = tie_break_key(_candidates()[0])

    assert key == (-0.80, 0.10, -0.80, "candidate_b")


def test_stable_ranking_sort_is_deterministic():
    sorted_candidates = stable_ranking_sort(_candidates())

    assert [candidate["candidate_id"] for candidate in sorted_candidates] == [
        "candidate_a",
        "candidate_c",
        "candidate_b",
    ]


def test_validate_tie_break_order_detects_stable_order():
    sorted_candidates = stable_ranking_sort(_candidates())

    assert validate_tie_break_order(sorted_candidates) is True
    assert validate_tie_break_order(_candidates()) is False

