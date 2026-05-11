from copy import deepcopy

from core.human_review.override_engine import apply_override
from core.human_review.reviewer_registry import normalize_reviewer_metadata
from core.human_review.review_schema import OverrideDecision


def _ai_output():
    return {
        "candidate_id": "resume_001",
        "candidate_name": "Asha Rao",
        "final_score": 8.2,
        "recommendation": "Strong Match",
        "ranking_position": 1,
        "bucket": "STRONG_MATCH",
    }


def _reviewer():
    return normalize_reviewer_metadata("Priya Shah")


def test_apply_score_override_preserves_original_ai_output():
    original = _ai_output()
    original_snapshot = deepcopy(original)
    decision = OverrideDecision(
        candidate_id="resume_001",
        override_type="score_override",
        reviewer=_reviewer(),
        reason="Verified stronger evidence in portfolio review.",
        override_score=8.9,
    )

    result = apply_override(original, decision)

    assert original == original_snapshot
    assert result["original_ai_output"] == original_snapshot
    assert result["final_presented_result"]["final_score"] == 8.9
    assert result["original_ai_output"]["final_score"] == 8.2
    assert result["override_applied"] is True


def test_apply_recommendation_override_changes_only_presented_result():
    decision = OverrideDecision(
        candidate_id="resume_001",
        override_type="recommendation_override",
        reviewer=_reviewer(),
        reason="Recruiter changed recommendation after reference check.",
        override_recommendation="Hold for Review",
    )

    result = apply_override(_ai_output(), decision)

    assert result["final_presented_result"]["recommendation"] == "Hold for Review"
    assert result["original_ai_output"]["recommendation"] == "Strong Match"


def test_apply_shortlist_override_sets_recruiter_visible_status():
    decision = OverrideDecision(
        candidate_id="resume_001",
        override_type="shortlist_override",
        reviewer=_reviewer(),
        reason="Hiring manager requested shortlist.",
        shortlist_status="shortlisted",
    )

    result = apply_override(_ai_output(), decision)

    assert result["final_presented_result"]["shortlist_status"] == "shortlisted"
    assert result["final_presented_result"]["is_shortlisted"] is True


def test_apply_recruiter_notes_attaches_notes_without_mutating_original():
    decision = OverrideDecision(
        candidate_id="resume_001",
        override_type="recruiter_notes",
        reviewer=_reviewer(),
        reason="Adding interview context.",
        review_notes="Ask about production monitoring experience.",
    )

    result = apply_override(_ai_output(), decision)

    assert result["final_presented_result"]["review_notes"] == (
        "Ask about production monitoring experience."
    )
    assert "review_notes" not in result["original_ai_output"]


def test_apply_override_is_deterministic():
    decision = OverrideDecision(
        candidate_id="resume_001",
        override_type="score_override",
        reviewer=_reviewer(),
        reason="Verified stronger evidence in portfolio review.",
        override_score=8.9,
    )

    first = apply_override(_ai_output(), decision)
    second = apply_override(_ai_output(), decision)

    assert first == second
