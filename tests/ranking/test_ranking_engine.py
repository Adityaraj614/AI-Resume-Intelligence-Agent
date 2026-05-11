from core.ranking.ranking_engine import rank_candidates


def _scoring_outputs():
    return [
        {
            "candidate_id": "resume_001",
            "semantic_score": 0.88,
            "llm_match_score": 8.4,
            "final_score": 8.7,
            "confidence": 0.91,
            "recommendation": "Strong Match",
            "score_breakdown": {
                "retrieval_weight": 0.7,
                "llm_weight": 0.3,
            },
        },
        {
            "candidate_id": "resume_002",
            "semantic_score": 0.84,
            "llm_match_score": 8.0,
            "final_score": 8.5,
            "confidence": 0.88,
            "recommendation": "Strong Match",
            "score_breakdown": {
                "retrieval_weight": 0.7,
                "llm_weight": 0.3,
            },
        },
        {
            "candidate_id": "resume_003",
            "semantic_score": 0.70,
            "llm_match_score": 7.0,
            "final_score": 7.0,
            "confidence": 0.95,
            "recommendation": "Moderate Match",
            "score_breakdown": {
                "retrieval_weight": 0.7,
                "llm_weight": 0.3,
            },
        },
    ]


def test_rank_candidates_orders_by_hybrid_priority_deterministically():
    first = rank_candidates(_scoring_outputs())
    second = rank_candidates(_scoring_outputs())

    assert first == second
    assert [item["candidate_id"] for item in first] == [
        "resume_001",
        "resume_002",
        "resume_003",
    ]
    assert [item["rank"] for item in first] == [1, 2, 3]


def test_rank_candidates_applies_hallucination_penalty():
    safety_results = {
        "resume_001": {
            "is_safe": False,
            "hallucination_risk": 0.9,
            "unsupported_claims": [{"field": "strengths", "claim": "fake"}],
        },
        "resume_002": {
            "is_safe": True,
            "hallucination_risk": 0.0,
            "unsupported_claims": [],
        },
    }

    rankings = rank_candidates(
        scoring_outputs=_scoring_outputs()[:2],
        safety_results=safety_results,
    )

    assert rankings[0]["candidate_id"] == "resume_002"
    assert rankings[1]["candidate_id"] == "resume_001"
    assert "unsupported_claims_detected" in rankings[1]["warning_flags"]
    assert rankings[1]["hallucination_risk"] == 0.9


def test_rank_candidates_keeps_unsafe_candidate_below_safer_evidence_grounded_candidate():
    scoring_outputs = [
        {
            "candidate_id": "unsafe_high_score",
            "semantic_score": 0.95,
            "llm_match_score": 9.5,
            "final_score": 9.5,
            "confidence": 0.95,
            "recommendation": "Strong Match",
            "score_breakdown": {},
        },
        {
            "candidate_id": "safe_lower_score",
            "semantic_score": 0.75,
            "llm_match_score": 7.2,
            "final_score": 7.4,
            "confidence": 0.78,
            "recommendation": "Moderate Match",
            "score_breakdown": {},
        },
    ]
    safety_results = {
        "unsafe_high_score": {
            "is_safe": False,
            "hallucination_risk": 0.4,
            "unsupported_claims": [{"field": "summary", "claim": "unsupported"}],
        },
        "safe_lower_score": {
            "is_safe": True,
            "hallucination_risk": 0.0,
            "unsupported_claims": [],
        },
    }

    rankings = rank_candidates(scoring_outputs, safety_results=safety_results)

    assert rankings[0]["candidate_id"] == "safe_lower_score"
    assert rankings[1]["candidate_id"] == "unsafe_high_score"


def test_rank_candidates_uses_confidence_as_secondary_signal():
    scoring_outputs = [
        {
            "candidate_id": "resume_low_confidence",
            "semantic_score": 0.80,
            "llm_match_score": 8.0,
            "final_score": 8.0,
            "confidence": 0.30,
            "recommendation": "Strong Match",
            "score_breakdown": {},
        },
        {
            "candidate_id": "resume_high_confidence",
            "semantic_score": 0.80,
            "llm_match_score": 8.0,
            "final_score": 8.0,
            "confidence": 0.90,
            "recommendation": "Strong Match",
            "score_breakdown": {},
        },
    ]

    rankings = rank_candidates(scoring_outputs)

    assert rankings[0]["candidate_id"] == "resume_high_confidence"
    assert rankings[1]["candidate_id"] == "resume_low_confidence"
    assert "low_confidence" in rankings[1]["warning_flags"]


def test_rank_candidates_generates_recruiter_explanations():
    rankings = rank_candidates(_scoring_outputs()[:1])

    assert rankings[0]["ranking_reason"]
    assert "strong retrieval alignment" in rankings[0]["ranking_reason"]
    assert "high confidence" in rankings[0]["ranking_reason"]


def test_rank_candidates_uses_evidence_quality_signals():
    scoring_outputs = [
        {
            "candidate_id": "resume_low_evidence",
            "semantic_score": 0.80,
            "llm_match_score": 8.0,
            "final_score": 8.0,
            "confidence": 0.80,
            "recommendation": "Strong Match",
            "score_breakdown": {},
        },
        {
            "candidate_id": "resume_high_evidence",
            "semantic_score": 0.80,
            "llm_match_score": 8.0,
            "final_score": 8.0,
            "confidence": 0.80,
            "recommendation": "Strong Match",
            "score_breakdown": {},
        },
    ]
    evidence_quality_signals = {
        "resume_low_evidence": {
            "evidence_coverage": 0.20,
            "retrieval_quality": 0.55,
        },
        "resume_high_evidence": {
            "evidence_coverage": 0.90,
            "retrieval_quality": 0.90,
        },
    }

    rankings = rank_candidates(
        scoring_outputs=scoring_outputs,
        evidence_quality_signals=evidence_quality_signals,
    )

    assert rankings[0]["candidate_id"] == "resume_high_evidence"
    assert "high evidence coverage" in rankings[0]["ranking_reason"]
