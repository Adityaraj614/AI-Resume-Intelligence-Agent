from core.recruiter.shortlist_rules import (
    GOOD_MATCH,
    POTENTIAL_MATCH,
    STRONG_MATCH,
    WEAK_MATCH,
    assign_shortlist_bucket,
    normalize_shortlist_thresholds,
    should_exclude_candidate,
)


def _candidate(**overrides):
    candidate = {
        "candidate_id": "resume_001",
        "final_score": 8.8,
        "confidence": 0.86,
        "hallucination_risk": 0.05,
        "evidence_quality": 0.82,
        "semantic_score": 0.88,
        "recommendation": "Strong Match",
        "rank": 1,
    }
    candidate.update(overrides)
    return candidate


def test_assign_shortlist_bucket_returns_strong_match_for_high_quality_candidate():
    assert assign_shortlist_bucket(_candidate()) == STRONG_MATCH


def test_assign_shortlist_bucket_handles_threshold_edges():
    bucket = assign_shortlist_bucket(_candidate(
        final_score=7.0,
        confidence=0.65,
        hallucination_risk=0.20,
        evidence_quality=0.60,
    ))

    assert bucket == GOOD_MATCH


def test_assign_shortlist_bucket_demotes_moderate_candidate_to_potential():
    bucket = assign_shortlist_bucket(_candidate(
        final_score=6.0,
        confidence=0.50,
        hallucination_risk=0.25,
        evidence_quality=0.50,
    ))

    assert bucket == POTENTIAL_MATCH


def test_assign_shortlist_bucket_uses_weak_match_for_low_confidence():
    bucket = assign_shortlist_bucket(_candidate(confidence=0.20))

    assert bucket == WEAK_MATCH


def test_should_exclude_candidate_detects_unsupported_claims():
    candidate = _candidate(warning_flags=["unsupported_claims_detected"])

    assert should_exclude_candidate(candidate) is True


def test_custom_thresholds_are_configurable():
    thresholds = normalize_shortlist_thresholds({
        STRONG_MATCH: {
            "min_final_score": 9.5,
        }
    })

    assert thresholds[STRONG_MATCH]["min_final_score"] == 9.5
    assert thresholds[GOOD_MATCH]["min_final_score"] == 7.0

