from core.safety.hallucination_guard import (
    detect_unsupported_claims,
    extract_claims_from_analysis,
    hallucination_risk_score,
    validate_evidence_alignment,
)


def _candidate_metadata():
    return {
        "candidate_id": "resume_001",
        "aggregate_score": 0.82,
        "matches": [
            {
                "section": "skills",
                "chunk_text": "Experienced in Python, PyTorch, and NLP.",
                "jd_section": "requirements",
                "jd_chunk_text": "Python and NLP experience",
                "score": 0.91,
            },
            {
                "section": "projects",
                "chunk_text": "Built transformer-based text classifier.",
                "jd_section": "responsibilities",
                "jd_chunk_text": "Build transformer applications",
                "score": 0.84,
            },
        ],
    }


def _safe_analysis():
    return {
        "candidate_id": "resume_001",
        "summary": "Candidate has Python and NLP evidence.",
        "strengths": [
            "Python and PyTorch experience",
            "Transformer project evidence",
        ],
        "missing_skills": ["No retrieved evidence for Docker"],
        "evidence_used": [
            "skills section matched requirements",
            "projects section matched responsibilities",
        ],
        "recommendation": "Moderate Match",
    }


def test_extract_claims_from_analysis_is_deterministic():
    first = extract_claims_from_analysis(_safe_analysis())
    second = extract_claims_from_analysis(_safe_analysis())

    assert first == second
    assert any(claim["field"] == "summary" for claim in first)
    assert any(claim["field"] == "strengths" for claim in first)


def test_detect_unsupported_claims_flags_fabricated_skill():
    analysis = {
        **_safe_analysis(),
        "strengths": ["Kubernetes and AWS production expertise"],
    }

    unsupported_claims = detect_unsupported_claims(
        analysis=analysis,
        candidate_metadata=_candidate_metadata(),
    )

    assert unsupported_claims
    assert unsupported_claims[0]["field"] == "strengths"


def test_detect_unsupported_claims_flags_forbidden_certainty_phrase():
    analysis = {
        **_safe_analysis(),
        "summary": "Candidate is guaranteed to be a perfect fit.",
    }

    unsupported_claims = detect_unsupported_claims(
        analysis=analysis,
        candidate_metadata=_candidate_metadata(),
    )

    assert unsupported_claims
    assert unsupported_claims[0]["field"] == "summary"


def test_validate_evidence_alignment_accepts_safe_analysis():
    result = validate_evidence_alignment(
        analysis=_safe_analysis(),
        candidate_metadata=_candidate_metadata(),
    )

    assert result["is_safe"] is True
    assert result["unsupported_claims"] == []
    assert result["recommendation_supported"] is True


def test_validate_evidence_alignment_rejects_unsupported_recommendation():
    analysis = {
        **_safe_analysis(),
        "recommendation": "Strong Match",
    }

    result = validate_evidence_alignment(
        analysis=analysis,
        candidate_metadata=_candidate_metadata(),
    )

    assert result["is_safe"] is False
    assert result["recommendation_supported"] is False


def test_hallucination_risk_score_increases_for_unsupported_claims():
    safe_risk = hallucination_risk_score(
        analysis=_safe_analysis(),
        candidate_metadata=_candidate_metadata(),
    )
    unsafe_risk = hallucination_risk_score(
        analysis={
            **_safe_analysis(),
            "strengths": ["Kubernetes and AWS production expertise"],
        },
        candidate_metadata=_candidate_metadata(),
    )

    assert safe_risk == 0.0
    assert unsafe_risk > safe_risk
