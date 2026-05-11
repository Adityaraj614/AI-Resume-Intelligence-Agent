from core.scoring.scoring_schema import (
    normalize_scoring_schema,
    validate_scoring_output,
)


def test_validate_scoring_output_accepts_complete_schema():
    scoring_output = {
        "candidate_id": "resume_001",
        "semantic_score": 0.87,
        "llm_match_score": 8.4,
        "final_score": 8.1,
        "confidence": 0.89,
        "recommendation": "Strong Match",
        "score_breakdown": {
            "retrieval_weight": 0.7,
            "llm_weight": 0.3,
        },
    }

    assert validate_scoring_output(scoring_output) is True


def test_validate_scoring_output_rejects_missing_breakdown():
    scoring_output = {
        "candidate_id": "resume_001",
        "semantic_score": 0.87,
        "llm_match_score": 8.4,
        "final_score": 8.1,
        "confidence": 0.89,
        "recommendation": "Strong Match",
    }

    assert validate_scoring_output(scoring_output) is False


def test_normalize_scoring_schema_clamps_numeric_ranges():
    normalized = normalize_scoring_schema({
        "candidate_id": "resume_001",
        "semantic_score": 2.0,
        "llm_match_score": 12.0,
        "final_score": -1.0,
        "confidence": 1.5,
        "recommendation": " Strong Match ",
        "score_breakdown": {
            "retrieval_weight": 0.7,
        },
    })

    assert normalized["semantic_score"] == 1.0
    assert normalized["llm_match_score"] == 10.0
    assert normalized["final_score"] == 0.0
    assert normalized["confidence"] == 1.0
    assert normalized["recommendation"] == "Strong Match"
