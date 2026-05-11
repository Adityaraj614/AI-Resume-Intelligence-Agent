from core.recruiter.recruiter_summary import (
    build_action_recommendation,
    build_candidate_decision_summary,
    summarize_decision_report,
)


def _candidate(**overrides):
    candidate = {
        "candidate_id": "resume_001",
        "candidate_name": "Asha Rao",
        "final_score": 8.8,
        "semantic_score": 0.88,
        "confidence_score": 0.88,
        "hallucination_risk": 0.05,
        "evidence_quality": 0.82,
        "strengths": ["python evidence"],
        "missing_skills": ["docker"],
    }
    candidate.update(overrides)
    return candidate


def test_build_candidate_decision_summary_is_template_based():
    summary = build_candidate_decision_summary(_candidate())

    assert "Asha Rao shows strong semantic alignment" in summary
    assert "strongest provided signal: python evidence" in summary
    assert "review missing skill: docker" in summary


def test_build_action_recommendation_is_safety_aware():
    assert build_action_recommendation(_candidate()) == "Schedule priority interview."
    assert build_action_recommendation(_candidate(hallucination_risk=0.40)) == (
        "Do not advance until unsupported or unsafe claims are resolved."
    )


def test_summarize_decision_report_handles_empty_and_counts():
    assert summarize_decision_report([]) == (
        "No candidates available for recruiter decision support."
    )
    summary = summarize_decision_report([
        {
            "interview_priority": "PRIORITY_INTERVIEW",
            "hiring_readiness": "HIGH",
        },
        {
            "interview_priority": "STANDARD_INTERVIEW",
            "hiring_readiness": "MEDIUM",
        },
    ])

    assert summary == (
        "1 of 2 candidates are priority interview candidates; "
        "1 candidates are hiring-ready."
    )

