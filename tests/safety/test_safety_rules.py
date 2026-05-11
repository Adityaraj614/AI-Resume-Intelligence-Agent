from core.safety.safety_rules import (
    FORBIDDEN_CLAIM_PATTERNS,
    MIN_EVIDENCE_REQUIRED,
    SAFE_ANALYSIS_RULES,
    SAFE_PROMPT_HEADER,
)


def test_safety_rules_include_retrieval_grounding():
    assert "Use ONLY retrieved evidence." in SAFE_ANALYSIS_RULES
    assert "Use ONLY retrieved evidence." in SAFE_PROMPT_HEADER
    assert MIN_EVIDENCE_REQUIRED >= 1


def test_forbidden_claim_patterns_cover_certainty_and_fabrication():
    assert "guaranteed" in FORBIDDEN_CLAIM_PATTERNS
    assert "worked at" in FORBIDDEN_CLAIM_PATTERNS
    assert "certified in" in FORBIDDEN_CLAIM_PATTERNS
