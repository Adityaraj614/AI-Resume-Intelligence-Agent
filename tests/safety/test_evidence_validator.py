from core.safety.evidence_validator import (
    evidence_exists_for_claim,
    validate_analysis_evidence,
    validate_recommendation_support,
)


def _candidate_metadata():
    return {
        "candidate_id": "resume_001",
        "aggregate_score": 0.82,
        "jd_match_coverage": 0.75,
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


def test_evidence_exists_for_claim_uses_retrieved_context():
    assert evidence_exists_for_claim("Python NLP experience", _candidate_metadata()["matches"])
    assert not evidence_exists_for_claim("Kubernetes production deployment", _candidate_metadata()["matches"])


def test_validate_analysis_evidence_accepts_supported_outputs():
    analysis = {
        "summary": "Candidate has Python and NLP evidence.",
        "strengths": ["Python and PyTorch experience"],
        "missing_skills": ["No retrieved evidence for Docker"],
        "evidence_used": ["skills section matched requirements"],
        "recommendation": "Moderate Match",
    }

    validation = validate_analysis_evidence(analysis, _candidate_metadata())

    assert validation["is_valid"] is True
    assert validation["unsupported_items"] == []


def test_validate_analysis_evidence_flags_unsupported_strengths():
    analysis = {
        "summary": "Candidate has Python evidence.",
        "strengths": ["Kubernetes and AWS production expertise"],
        "missing_skills": [],
        "evidence_used": ["skills section matched requirements"],
        "recommendation": "Moderate Match",
    }

    validation = validate_analysis_evidence(analysis, _candidate_metadata())

    assert validation["is_valid"] is False
    assert validation["unsupported_items"][0]["field"] == "strengths"


def test_validate_analysis_evidence_flags_missing_skill_claim_present_in_evidence():
    analysis = {
        "summary": "Candidate has Python evidence.",
        "strengths": ["Python experience"],
        "missing_skills": ["Python"],
        "evidence_used": ["skills section matched requirements"],
        "recommendation": "Moderate Match",
    }

    validation = validate_analysis_evidence(analysis, _candidate_metadata())

    assert validation["is_valid"] is False
    assert validation["unsupported_items"][0]["field"] == "missing_skills"


def test_validate_recommendation_support_checks_retrieval_score():
    assert validate_recommendation_support(
        {"recommendation": "Moderate Match"},
        _candidate_metadata(),
    )
    assert not validate_recommendation_support(
        {"recommendation": "Strong Match"},
        _candidate_metadata(),
    )
