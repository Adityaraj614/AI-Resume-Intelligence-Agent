from core.human_review.override_engine import apply_override
from core.human_review.override_history import append_override_event, summarize_override_history
from core.human_review.reviewer_registry import normalize_reviewer_metadata
from core.human_review.review_schema import OverrideDecision


def _ranked_candidate():
    return {
        "rank": 1,
        "candidate_id": "resume_001",
        "candidate_name": "Asha Rao",
        "final_score": 8.7,
        "confidence": 0.91,
        "recommendation": "Strong Match",
        "hallucination_risk": 0.02,
        "ranking_reason": "Strong retrieval alignment and high confidence.",
        "evidence_quality": 0.88,
        "bucket": "STRONG_MATCH",
    }


def test_human_review_layer_preserves_ranked_ai_output_for_audit():
    ranked_candidate = _ranked_candidate()
    decision = OverrideDecision(
        candidate_id="resume_001",
        override_type="recommendation_override",
        reviewer=normalize_reviewer_metadata("Priya Shah"),
        reason="Recruiter identified a location constraint after AI ranking.",
        timestamp="2026-05-11T09:00:00Z",
        override_recommendation="Hold for Review",
    )

    reviewed = apply_override(ranked_candidate, decision)

    assert reviewed["original_ai_output"] == ranked_candidate
    assert reviewed["final_presented_result"]["recommendation"] == "Hold for Review"
    assert reviewed["final_presented_result"]["rank"] == 1
    assert reviewed["final_presented_result"]["ranking_reason"] == (
        "Strong retrieval alignment and high confidence."
    )


def test_human_review_output_is_export_and_workflow_compatible():
    reviewed = apply_override(
        _ranked_candidate(),
        OverrideDecision(
            candidate_id="resume_001",
            override_type="recruiter_notes",
            reviewer=normalize_reviewer_metadata("Priya Shah"),
            reason="Add interview guidance.",
            review_notes="Ask about evidence behind production ML claims.",
        ),
    )
    final_result = reviewed["final_presented_result"]

    for key in (
        "candidate_id",
        "candidate_name",
        "final_score",
        "recommendation",
        "override_applied",
        "override_metadata",
    ):
        assert key in final_result

    history = append_override_event([], reviewed["audit_entry"])
    summary = summarize_override_history(history)

    assert summary["total_overrides"] == 1
    assert summary["candidate_ids"] == ["resume_001"]


def test_human_review_workflow_is_reproducible():
    decision = OverrideDecision(
        candidate_id="resume_001",
        override_type="score_override",
        reviewer=normalize_reviewer_metadata("Priya Shah"),
        reason="Manual calibration after hiring manager review.",
        timestamp="2026-05-11T09:00:00Z",
        override_score=9.1,
    )

    first = apply_override(_ranked_candidate(), decision)
    second = apply_override(_ranked_candidate(), decision)

    assert first == second
