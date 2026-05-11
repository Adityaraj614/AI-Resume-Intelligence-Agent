from core.recruiter.decision_schema import (
    normalize_decision_output,
    validate_decision_output,
    validate_decision_report,
)


def _decision():
    return {
        "candidate_id": "resume_001",
        "candidate_name": "Asha Rao",
        "ranking_position": 1,
        "interview_priority": "PRIORITY_INTERVIEW",
        "hiring_readiness": "HIGH",
        "readiness_reason": "Strong evidence.",
        "risk_flags": [],
        "interview_focus_areas": [],
        "decision_summary": "Strong candidate.",
        "action_recommendation": "Schedule priority interview.",
    }


def test_normalize_decision_output_stabilizes_fields():
    normalized = normalize_decision_output({
        **_decision(),
        "candidate_id": " resume_001 ",
        "candidate_name": " Asha Rao ",
    })

    assert normalized["candidate_id"] == "resume_001"
    assert normalized["candidate_name"] == "Asha Rao"


def test_validate_decision_output_accepts_complete_decision():
    assert validate_decision_output(_decision()) is True


def test_validate_decision_output_rejects_invalid_priority():
    decision = {
        **_decision(),
        "interview_priority": "MAYBE",
    }

    assert validate_decision_output(decision) is False


def test_validate_decision_report_checks_counts_and_nested_decisions():
    report = {
        "candidate_count": 1,
        "prioritized_interviews": [_decision()],
        "hiring_ready_candidates": [_decision()],
        "risk_summary": {},
        "candidate_decisions": [_decision()],
        "report_summary": "1 candidate.",
    }

    assert validate_decision_report(report) is True
    assert validate_decision_report({**report, "candidate_count": 2}) is False

