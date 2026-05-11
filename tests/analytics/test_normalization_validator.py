from core.analytics.normalization_validator import (
    validate_ranking_positions,
    validate_score_normalization,
)


def test_validate_score_normalization_accepts_valid_ranges():
    result = validate_score_normalization([
        {
            "candidate_id": "resume_001",
            "final_score": 8.5,
            "confidence_score": 0.9,
            "hallucination_risk": 0.1,
            "evidence_quality": 0.8,
            "semantic_score": 0.8,
        }
    ])

    assert result["is_valid"] is True
    assert result["anomaly_count"] == 0


def test_validate_score_normalization_detects_score_anomalies():
    result = validate_score_normalization([
        {
            "candidate_id": "resume_001",
            "final_score": 120,
            "confidence_score": 0.9,
            "hallucination_risk": 0.1,
            "evidence_quality": 0.8,
            "semantic_score": 0.8,
        }
    ])

    assert result["is_valid"] is False
    assert result["anomalies"][0]["field"] == "final_score"


def test_validate_ranking_positions_detects_missing_and_duplicate_ranks():
    result = validate_ranking_positions([
        {"candidate_id": "resume_001", "ranking_position": 1},
        {"candidate_id": "resume_002", "ranking_position": 1},
        {"candidate_id": "resume_003", "ranking_position": 0},
    ])

    assert result["is_valid"] is False
    assert result["anomaly_count"] == 2

