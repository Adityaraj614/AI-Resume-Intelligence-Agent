import hashlib
from typing import Any, Dict

from core.human_review.review_schema import AuditEntry, OverrideDecision
from core.human_review.review_utils import (
    clean_text,
    deterministic_serialize,
    normalize_timestamp,
    safe_deepcopy,
)


def build_audit_id(
    candidate_id: str,
    override_type: str,
    reviewer_id: str,
    timestamp: str,
    before: Dict[str, Any],
    after: Dict[str, Any],
) -> str:
    identity = {
        "candidate_id": candidate_id,
        "override_type": override_type,
        "reviewer_id": reviewer_id,
        "timestamp": timestamp,
        "before": before,
        "after": after,
    }
    digest = hashlib.sha256(
        deterministic_serialize(identity).encode("utf-8")
    ).hexdigest()[:12]

    return f"audit_{digest}"


def log_override_action(
    decision: OverrideDecision,
    before: Dict[str, Any],
    after: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Build a deterministic serializable audit entry for one override action.
    """

    timestamp = normalize_timestamp(decision.timestamp)
    entry = AuditEntry(
        audit_id=build_audit_id(
            candidate_id=decision.candidate_id,
            override_type=decision.override_type,
            reviewer_id=decision.reviewer.reviewer_id,
            timestamp=timestamp,
            before=before,
            after=after,
        ),
        reviewer=decision.reviewer.to_dict(),
        candidate_id=decision.candidate_id,
        override_type=decision.override_type,
        before=safe_deepcopy(before),
        after=safe_deepcopy(after),
        reason=clean_text(decision.reason),
        timestamp=timestamp,
        source=decision.source,
    )

    return entry.to_dict()
