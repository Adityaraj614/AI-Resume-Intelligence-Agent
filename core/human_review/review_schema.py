from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

from core.human_review.review_utils import (
    DEFAULT_REVIEW_TIMESTAMP,
    clean_text,
    normalize_override_type,
    normalize_timestamp,
)


@dataclass(frozen=True)
class ReviewerMetadata:
    reviewer_id: str
    reviewer_name: str
    source: str = "human_review"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class OverrideDecision:
    candidate_id: str
    override_type: str
    reviewer: ReviewerMetadata
    reason: str
    timestamp: str = DEFAULT_REVIEW_TIMESTAMP
    override_score: Optional[float] = None
    override_recommendation: str = ""
    shortlist_status: str = ""
    review_notes: str = ""
    confidence: float = 1.0
    source: str = "human_review"

    def __post_init__(self) -> None:
        object.__setattr__(self, "candidate_id", clean_text(self.candidate_id))
        object.__setattr__(self, "override_type", normalize_override_type(self.override_type))
        object.__setattr__(self, "reason", clean_text(self.reason))
        object.__setattr__(self, "timestamp", normalize_timestamp(self.timestamp))
        object.__setattr__(self, "override_recommendation", clean_text(self.override_recommendation))
        object.__setattr__(self, "shortlist_status", clean_text(self.shortlist_status))
        object.__setattr__(self, "review_notes", clean_text(self.review_notes))
        object.__setattr__(self, "source", clean_text(self.source) or "human_review")

    def to_dict(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            "reviewer": self.reviewer.to_dict(),
        }


@dataclass(frozen=True)
class OverrideRecord:
    reviewer_id: str
    reviewer_name: str
    candidate_id: str
    override_type: str
    original_score: Optional[float] = None
    override_score: Optional[float] = None
    original_recommendation: str = ""
    override_recommendation: str = ""
    reason: str = ""
    timestamp: str = DEFAULT_REVIEW_TIMESTAMP
    review_notes: str = ""
    confidence: float = 1.0
    source: str = "human_review"

    def __post_init__(self) -> None:
        object.__setattr__(self, "override_type", normalize_override_type(self.override_type))
        object.__setattr__(self, "timestamp", normalize_timestamp(self.timestamp))

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AuditEntry:
    audit_id: str
    reviewer: Dict[str, Any]
    candidate_id: str
    override_type: str
    before: Dict[str, Any]
    after: Dict[str, Any]
    reason: str
    timestamp: str = DEFAULT_REVIEW_TIMESTAMP
    source: str = "human_review"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class OverrideHistory:
    candidate_id: str
    entries: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def validate_reviewer_metadata(reviewer: ReviewerMetadata) -> bool:
    if not isinstance(reviewer, ReviewerMetadata):
        return False

    return bool(reviewer.reviewer_id.strip() and reviewer.reviewer_name.strip())


def validate_override_decision(decision: OverrideDecision) -> bool:
    if not isinstance(decision, OverrideDecision):
        return False

    if not decision.candidate_id:
        return False

    if not decision.reason:
        return False

    if not validate_reviewer_metadata(decision.reviewer):
        return False

    if decision.override_type == "score_override" and decision.override_score is None:
        return False

    if decision.override_type == "recommendation_override" and not decision.override_recommendation:
        return False

    if decision.override_type == "shortlist_override" and not decision.shortlist_status:
        return False

    if decision.override_type == "recruiter_notes" and not decision.review_notes:
        return False

    return 0.0 <= float(decision.confidence) <= 1.0
