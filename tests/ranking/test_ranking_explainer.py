from core.ranking.ranking_explainer import (
    build_ranking_reason,
    explain_candidate_priority,
    summarize_ranking_signals,
)


def _candidate_record():
    return {
        "candidate_id": "resume_001",
        "final_score": 8.6,
        "confidence": 0.91,
        "semantic_score": 0.88,
        "evidence_quality": 0.86,
        "evidence_coverage": 0.84,
        "retrieval_quality": 0.88,
        "hallucination_risk": 0.0,
        "recommendation": "Strong Match",
    }


def test_summarize_ranking_signals_extracts_key_fields():
    signals = summarize_ranking_signals(_candidate_record())

    assert signals["final_score"] == 8.6
    assert signals["confidence"] == 0.91
    assert signals["semantic_score"] == 0.88
    assert signals["evidence_quality"] == 0.86
    assert signals["evidence_coverage"] == 0.84
    assert signals["hallucination_risk"] == 0.0


def test_build_ranking_reason_mentions_retrieval_confidence_and_safety():
    reason = build_ranking_reason(_candidate_record())

    assert "strong overall hybrid score" in reason
    assert "strong retrieval alignment" in reason
    assert "high evidence coverage" in reason
    assert "high confidence" in reason
    assert "no hallucination penalty" in reason


def test_build_ranking_reason_mentions_safety_penalty():
    reason = build_ranking_reason({
        **_candidate_record(),
        "hallucination_risk": 0.5,
    })

    assert "safety penalty applied" in reason


def test_explain_candidate_priority_is_recruiter_readable():
    explanation = explain_candidate_priority(_candidate_record())

    assert explanation.startswith("resume_001: Strong Match.")
    assert "strong retrieval alignment" in explanation
