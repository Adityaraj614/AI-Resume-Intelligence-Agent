from core.recruiter.interview_recommender import (
    HOLD,
    HIGH_READINESS,
    LOW_READINESS,
    MEDIUM_READINESS,
    PRIORITY_INTERVIEW,
    REJECT,
    STANDARD_INTERVIEW,
    evaluate_hiring_readiness,
    normalize_decision_thresholds,
    recommend_interview_priority,
    suggest_interview_focus_areas,
)


def _candidate(**overrides):
    candidate = {
        "candidate_id": "resume_001",
        "final_score": 8.8,
        "confidence_score": 0.88,
        "hallucination_risk": 0.05,
        "evidence_quality": 0.82,
        "semantic_score": 0.88,
        "bucket": "STRONG_MATCH",
        "missing_skills": [],
        "weaknesses": [],
    }
    candidate.update(overrides)
    return candidate


def test_recommend_interview_priority_assigns_priority_interview():
    assert recommend_interview_priority(_candidate()) == PRIORITY_INTERVIEW


def test_recommend_interview_priority_assigns_standard_and_hold():
    assert recommend_interview_priority(_candidate(
        final_score=7.4,
        confidence_score=0.70,
        hallucination_risk=0.12,
        evidence_quality=0.65,
    )) == STANDARD_INTERVIEW
    assert recommend_interview_priority(_candidate(
        final_score=5.8,
        confidence_score=0.50,
        hallucination_risk=0.25,
        evidence_quality=0.50,
    )) == HOLD


def test_recommend_interview_priority_rejects_unsafe_candidate():
    assert recommend_interview_priority(_candidate(hallucination_risk=0.40)) == REJECT


def test_decision_thresholds_are_configurable():
    thresholds = normalize_decision_thresholds({
        PRIORITY_INTERVIEW: {"min_final_score": 9.5}
    })

    assert thresholds[PRIORITY_INTERVIEW]["min_final_score"] == 9.5


def test_evaluate_hiring_readiness_levels():
    assert evaluate_hiring_readiness(_candidate())["hiring_readiness"] == HIGH_READINESS
    assert evaluate_hiring_readiness(_candidate(
        final_score=6.5,
        confidence_score=0.60,
        hallucination_risk=0.20,
        evidence_quality=0.50,
        missing_skills=["docker", "kubernetes"],
    ))["hiring_readiness"] == MEDIUM_READINESS
    assert evaluate_hiring_readiness(_candidate(
        final_score=4.0,
        confidence_score=0.30,
        evidence_quality=0.20,
    ))["hiring_readiness"] == LOW_READINESS


def test_suggest_interview_focus_areas_uses_missing_skills_and_weaknesses():
    focus = suggest_interview_focus_areas(_candidate(
        missing_skills=["Docker"],
        weaknesses=["limited deployment evidence"],
    ))

    assert "Validate docker experience." in focus
    assert "Probe limited deployment evidence." in focus

