from core.recruiter.risk_analyzer import (
    find_missing_critical_skills,
    generate_risk_flags,
    has_blocking_risk,
)


def test_find_missing_critical_skills_uses_missing_skills_only():
    candidate = {
        "missing_skills": ["Docker", "React"],
        "extracted_skills": ["Kubernetes"],
    }

    assert find_missing_critical_skills(candidate) == ["docker"]


def test_generate_risk_flags_detects_supported_risks():
    candidate = {
        "confidence_score": 0.40,
        "hallucination_risk": 0.35,
        "evidence_quality": 0.30,
        "semantic_score": 0.40,
        "missing_skills": ["Docker"],
        "warning_flags": ["unsupported_claims_detected"],
        "weaknesses": ["gap one", "gap two", "gap three"],
    }

    flags = generate_risk_flags(candidate)

    assert "LOW_EVIDENCE_QUALITY" in flags
    assert "LOW_CONFIDENCE" in flags
    assert "HIGH_HALLUCINATION_RISK" in flags
    assert "WEAK_SEMANTIC_ALIGNMENT" in flags
    assert "MISSING_CRITICAL_SKILLS" in flags
    assert "UNSUPPORTED_CLAIMS" in flags
    assert "MULTIPLE_PROFILE_WEAKNESSES" in flags


def test_has_blocking_risk_detects_safety_or_evidence_blockers():
    assert has_blocking_risk({"hallucination_risk": 0.40}) is True
    assert has_blocking_risk({"evidence_quality": 0.80}) is False

