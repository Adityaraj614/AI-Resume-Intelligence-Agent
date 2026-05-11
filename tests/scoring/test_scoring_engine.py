import pytest

from core.scoring.scoring_engine import (
    calculate_llm_match_score,
    score_candidate,
)


def _candidate_metadata():
    return {
        "candidate_id": "resume_001",
        "aggregate_score": 0.82,
        "jd_match_coverage": 0.80,
        "match_count": 3,
        "matched_sections": ["skills", "projects"],
        "matches": [
            {"score": 0.90},
            {"score": 0.84},
            {"score": 0.80},
        ],
    }


def _candidate_analysis():
    return {
        "candidate_id": "resume_001",
        "summary": "Candidate has evidence-backed NLP and Python alignment.",
        "strengths": [
            "Python evidence",
            "NLP project evidence",
            "PyTorch evidence",
        ],
        "missing_skills": ["No Docker evidence"],
        "evidence_used": [
            "skills section matched requirements",
            "projects section matched responsibilities",
            "experience section matched ML workflow",
        ],
        "recommendation": "Moderate Match",
    }


def test_calculate_llm_match_score_is_deterministic():
    first = calculate_llm_match_score(_candidate_analysis())
    second = calculate_llm_match_score(_candidate_analysis())

    assert first == second
    assert 0 <= first <= 10


def test_score_candidate_uses_hybrid_weighting():
    scoring_output = score_candidate(
        candidate_metadata=_candidate_metadata(),
        candidate_analysis=_candidate_analysis(),
        retrieval_weight=0.7,
        llm_weight=0.3,
    )

    semantic_score_10 = scoring_output["score_breakdown"]["semantic_score_10_point"]
    expected_final_score = (
        semantic_score_10 * 0.7
        + scoring_output["llm_match_score"] * 0.3
    )

    assert scoring_output["candidate_id"] == "resume_001"
    assert scoring_output["semantic_score"] == 0.82
    assert scoring_output["final_score"] == pytest.approx(expected_final_score)
    assert scoring_output["score_breakdown"]["retrieval_weight"] == 0.7
    assert scoring_output["score_breakdown"]["llm_weight"] == 0.3
    assert 0 <= scoring_output["confidence"] <= 1
    assert scoring_output["recommendation"] in {
        "Strong Match",
        "Moderate Match",
        "Weak Match",
        "Poor Match",
    }


def test_score_candidate_normalizes_custom_weights():
    scoring_output = score_candidate(
        candidate_metadata=_candidate_metadata(),
        candidate_analysis=_candidate_analysis(),
        retrieval_weight=7,
        llm_weight=3,
    )

    assert scoring_output["score_breakdown"]["retrieval_weight"] == 0.7
    assert scoring_output["score_breakdown"]["llm_weight"] == 0.3


def test_score_candidate_rejects_invalid_analysis():
    invalid_analysis = {
        "candidate_id": "resume_001",
        "summary": "Missing required fields.",
    }

    with pytest.raises(ValueError):
        score_candidate(_candidate_metadata(), invalid_analysis)
