import pytest

from core.human_review.reviewer_registry import normalize_reviewer_metadata
from core.human_review.review_schema import (
    OverrideDecision,
    OverrideRecord,
    ReviewerMetadata,
    validate_override_decision,
    validate_reviewer_metadata,
)


def test_reviewer_metadata_is_serializable_and_valid():
    reviewer = ReviewerMetadata(
        reviewer_id="reviewer_001",
        reviewer_name="Priya Shah",
    )

    assert validate_reviewer_metadata(reviewer) is True
    assert reviewer.to_dict() == {
        "reviewer_id": "reviewer_001",
        "reviewer_name": "Priya Shah",
        "source": "human_review",
    }


def test_override_decision_normalizes_type_and_timestamp():
    reviewer = normalize_reviewer_metadata("Priya Shah")
    decision = OverrideDecision(
        candidate_id="resume_001",
        override_type="Score Override",
        reviewer=reviewer,
        reason="Recruiter verified stronger domain experience.",
        override_score=8.8,
    )

    assert decision.override_type == "score_override"
    assert decision.timestamp == "not_provided"
    assert validate_override_decision(decision) is True


def test_override_decision_requires_type_specific_values():
    reviewer = normalize_reviewer_metadata("Priya Shah")
    decision = OverrideDecision(
        candidate_id="resume_001",
        override_type="recommendation_override",
        reviewer=reviewer,
        reason="Panel feedback changed recommendation.",
    )

    assert validate_override_decision(decision) is False


def test_override_decision_rejects_unknown_override_type():
    reviewer = normalize_reviewer_metadata("Priya Shah")

    with pytest.raises(ValueError):
        OverrideDecision(
            candidate_id="resume_001",
            override_type="rerank_candidate",
            reviewer=reviewer,
            reason="Not supported.",
        )


def test_override_record_is_deterministic_and_serializable():
    record = OverrideRecord(
        reviewer_id="reviewer_001",
        reviewer_name="Priya Shah",
        candidate_id="resume_001",
        override_type="score_override",
        original_score=8.2,
        override_score=8.8,
        original_recommendation="Strong Match",
        reason="Manual review.",
    )

    assert record.to_dict()["override_type"] == "score_override"
    assert record.to_dict()["timestamp"] == "not_provided"
