from core.human_review.audit_logger import log_override_action
from core.human_review.override_history import (
    append_override_event,
    get_override_history,
    summarize_override_history,
)
from core.human_review.reviewer_registry import normalize_reviewer_metadata
from core.human_review.review_schema import OverrideDecision


def _audit_entry(candidate_id="resume_001", timestamp="2026-05-11T09:00:00Z"):
    decision = OverrideDecision(
        candidate_id=candidate_id,
        override_type="recommendation_override",
        reviewer=normalize_reviewer_metadata("Priya Shah"),
        reason="Manual review.",
        timestamp=timestamp,
        override_recommendation="Hold for Review",
    )

    return log_override_action(
        decision=decision,
        before={"recommendation": "Strong Match"},
        after={"recommendation": "Hold for Review"},
    )


def test_append_override_event_keeps_chronological_order():
    later = _audit_entry(timestamp="2026-05-11T10:00:00Z")
    earlier = _audit_entry(timestamp="2026-05-11T09:00:00Z")

    history = append_override_event([], later)
    history = append_override_event(history, earlier)

    assert [entry["timestamp"] for entry in history] == [
        "2026-05-11T09:00:00Z",
        "2026-05-11T10:00:00Z",
    ]


def test_get_override_history_filters_by_candidate():
    history = [
        _audit_entry(candidate_id="resume_001"),
        _audit_entry(candidate_id="resume_002"),
    ]

    candidate_history = get_override_history(history, "resume_001")

    assert candidate_history["candidate_id"] == "resume_001"
    assert len(candidate_history["entries"]) == 1
    assert candidate_history["entries"][0]["candidate_id"] == "resume_001"


def test_summarize_override_history_counts_types_and_candidates():
    history = [
        _audit_entry(candidate_id="resume_001"),
        _audit_entry(candidate_id="resume_002"),
    ]

    summary = summarize_override_history(history)

    assert summary == {
        "total_overrides": 2,
        "override_counts": {"recommendation_override": 2},
        "candidate_ids": ["resume_001", "resume_002"],
    }
