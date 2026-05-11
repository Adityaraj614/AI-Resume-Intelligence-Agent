from core.ranking.ranking_schema import (
    normalize_ranking_schema,
    validate_ranking_output,
)


def test_validate_ranking_output_accepts_complete_ranked_list():
    ranking_output = [
        {
            "rank": 1,
            "candidate_id": "resume_001",
            "final_score": 8.7,
            "confidence": 0.91,
            "recommendation": "Strong Match",
            "hallucination_risk": 0.0,
            "ranking_reason": "Strong retrieval alignment.",
        }
    ]

    assert validate_ranking_output(ranking_output) is True


def test_validate_ranking_output_rejects_nonsequential_rank():
    ranking_output = [
        {
            "rank": 2,
            "candidate_id": "resume_001",
            "final_score": 8.7,
            "confidence": 0.91,
            "recommendation": "Strong Match",
            "hallucination_risk": 0.0,
            "ranking_reason": "Strong retrieval alignment.",
        }
    ]

    assert validate_ranking_output(ranking_output) is False


def test_normalize_ranking_schema_clamps_values():
    normalized = normalize_ranking_schema({
        "rank": "1",
        "candidate_id": " resume_001 ",
        "final_score": 11.0,
        "confidence": -0.2,
        "recommendation": " Strong Match ",
        "hallucination_risk": 2.0,
        "ranking_reason": " Ranked safely. ",
    })

    assert normalized["rank"] == 1
    assert normalized["candidate_id"] == "resume_001"
    assert normalized["final_score"] == 10.0
    assert normalized["confidence"] == 0.0
    assert normalized["hallucination_risk"] == 1.0
    assert normalized["ranking_reason"] == "Ranked safely."


def test_validate_ranking_output_rejects_invalid_warning_flags():
    ranking_output = [
        {
            "rank": 1,
            "candidate_id": "resume_001",
            "final_score": 8.7,
            "confidence": 0.91,
            "recommendation": "Strong Match",
            "hallucination_risk": 0.0,
            "ranking_reason": "Strong retrieval alignment.",
            "warning_flags": "unsupported_claims_detected",
        }
    ]

    assert validate_ranking_output(ranking_output) is False
