from core.recruiter.decision_support import (
    build_candidate_decision_support,
    generate_recruiter_decision_report,
    summarize_risks,
)


def _candidates():
    return [
        {
            "candidate_id": "resume_002",
            "candidate_name": "Ben Lee",
            "ranking_position": 2,
            "final_score": 7.4,
            "semantic_score": 0.72,
            "confidence_score": 0.72,
            "hallucination_risk": 0.12,
            "evidence_quality": 0.66,
            "missing_skills": ["docker"],
            "weaknesses": ["limited ml evidence"],
        },
        {
            "candidate_id": "resume_001",
            "candidate_name": "Asha Rao",
            "ranking_position": 1,
            "final_score": 8.9,
            "semantic_score": 0.90,
            "confidence_score": 0.91,
            "hallucination_risk": 0.05,
            "evidence_quality": 0.86,
            "strengths": ["python evidence"],
            "missing_skills": [],
        },
        {
            "candidate_id": "resume_003",
            "candidate_name": "Chen Wu",
            "ranking_position": 3,
            "final_score": 8.5,
            "semantic_score": 0.82,
            "confidence_score": 0.90,
            "hallucination_risk": 0.40,
            "evidence_quality": 0.82,
            "warning_flags": ["unsupported_claims_detected"],
        },
    ]


def test_build_candidate_decision_support_returns_structured_output():
    decision = build_candidate_decision_support(_candidates()[1])

    assert decision["candidate_id"] == "resume_001"
    assert decision["interview_priority"] == "PRIORITY_INTERVIEW"
    assert decision["hiring_readiness"] == "HIGH"
    assert decision["action_recommendation"] == "Schedule priority interview."


def test_build_candidate_decision_support_is_hallucination_aware():
    decision = build_candidate_decision_support(_candidates()[2])

    assert decision["interview_priority"] == "REJECT"
    assert "HIGH_HALLUCINATION_RISK" in decision["risk_flags"]
    assert "UNSUPPORTED_CLAIMS" in decision["risk_flags"]


def test_summarize_risks_counts_flags_deterministically():
    risk_summary = summarize_risks([
        {"risk_flags": ["LOW_CONFIDENCE", "LOW_EVIDENCE_QUALITY"]},
        {"risk_flags": ["LOW_CONFIDENCE"]},
    ])

    assert risk_summary == {
        "LOW_CONFIDENCE": 2,
        "LOW_EVIDENCE_QUALITY": 1,
    }


def test_generate_recruiter_decision_report_preserves_ranking_order():
    report = generate_recruiter_decision_report(_candidates())

    assert report["candidate_count"] == 3
    assert [decision["candidate_id"] for decision in report["candidate_decisions"]] == [
        "resume_001",
        "resume_002",
        "resume_003",
    ]
    assert report["prioritized_interviews"][0]["candidate_id"] == "resume_001"
    assert report["hiring_ready_candidates"][0]["candidate_id"] == "resume_001"


def test_generate_recruiter_decision_report_handles_empty_candidates():
    report = generate_recruiter_decision_report([])

    assert report["candidate_count"] == 0
    assert report["candidate_decisions"] == []
    assert report["report_summary"] == (
        "No candidates available for recruiter decision support."
    )


def test_generate_recruiter_decision_report_is_deterministic():
    first = generate_recruiter_decision_report(_candidates())
    second = generate_recruiter_decision_report(_candidates())

    assert first == second
