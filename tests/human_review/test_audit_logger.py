from core.human_review.audit_logger import log_override_action
from core.human_review.reviewer_registry import normalize_reviewer_metadata
from core.human_review.review_schema import OverrideDecision
from core.human_review.review_utils import deterministic_serialize


def _decision():
    return OverrideDecision(
        candidate_id="resume_001",
        override_type="score_override",
        reviewer=normalize_reviewer_metadata("Priya Shah"),
        reason="Verified project depth during phone screen.",
        timestamp="2026-05-11T09:00:00Z",
        override_score=8.8,
    )


def test_log_override_action_creates_structured_audit_entry():
    entry = log_override_action(
        decision=_decision(),
        before={"final_score": 8.2},
        after={"final_score": 8.8},
    )

    assert entry["audit_id"].startswith("audit_")
    assert entry["candidate_id"] == "resume_001"
    assert entry["override_type"] == "score_override"
    assert entry["before"] == {"final_score": 8.2}
    assert entry["after"] == {"final_score": 8.8}
    assert entry["reviewer"]["reviewer_name"] == "Priya Shah"


def test_log_override_action_is_deterministic():
    first = log_override_action(_decision(), {"final_score": 8.2}, {"final_score": 8.8})
    second = log_override_action(_decision(), {"final_score": 8.2}, {"final_score": 8.8})

    assert first == second


def test_audit_entry_serializes_with_stable_key_order():
    entry = log_override_action(_decision(), {"final_score": 8.2}, {"final_score": 8.8})

    assert deterministic_serialize(entry) == deterministic_serialize(entry)
