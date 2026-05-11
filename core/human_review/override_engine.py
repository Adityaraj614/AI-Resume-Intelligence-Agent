from typing import Any, Dict

from core.human_review.audit_logger import log_override_action
from core.human_review.review_schema import (
    OverrideDecision,
    OverrideRecord,
    validate_override_decision,
)
from core.human_review.review_utils import safe_deepcopy


def apply_override(
    original_ai_output: Dict[str, Any],
    decision: OverrideDecision,
) -> Dict[str, Any]:
    """
    Apply a human review override as a presentation-layer adjustment.

    The original AI output is deep-copied and preserved unchanged for audit,
    reproducibility, and downstream analytics integrity.
    """

    if not isinstance(original_ai_output, dict):
        raise TypeError("original_ai_output must be a dictionary.")

    if not validate_override_decision(decision):
        raise ValueError("Override decision failed schema validation.")

    original_snapshot = safe_deepcopy(original_ai_output)
    final_result = safe_deepcopy(original_ai_output)
    before_values = _extract_before_values(original_ai_output, decision)

    if decision.override_type == "score_override":
        final_result["final_score"] = float(decision.override_score)

    if decision.override_type == "recommendation_override":
        final_result["recommendation"] = decision.override_recommendation

    if decision.override_type == "shortlist_override":
        final_result["shortlist_status"] = decision.shortlist_status
        final_result["is_shortlisted"] = decision.shortlist_status.lower() in (
            "shortlisted",
            "include",
            "included",
            "yes",
        )

    if decision.override_type == "recruiter_notes":
        final_result["review_notes"] = decision.review_notes

    after_values = _extract_after_values(final_result, decision)
    override_record = _build_override_record(original_ai_output, decision)
    audit_entry = log_override_action(
        decision=decision,
        before=before_values,
        after=after_values,
    )
    final_result["override_applied"] = True
    final_result["override_metadata"] = override_record.to_dict()

    return {
        "candidate_id": decision.candidate_id,
        "original_ai_output": original_snapshot,
        "final_presented_result": final_result,
        "override_applied": True,
        "override_metadata": override_record.to_dict(),
        "audit_entry": audit_entry,
    }


def _extract_original_score(original_ai_output: Dict[str, Any]) -> Any:
    if "final_score" in original_ai_output:
        return original_ai_output.get("final_score")

    return original_ai_output.get("score")


def _extract_before_values(
    original_ai_output: Dict[str, Any],
    decision: OverrideDecision,
) -> Dict[str, Any]:
    before = {}

    if decision.override_type == "score_override":
        before["final_score"] = _extract_original_score(original_ai_output)

    if decision.override_type == "recommendation_override":
        before["recommendation"] = original_ai_output.get("recommendation", "")

    if decision.override_type == "shortlist_override":
        before["shortlist_status"] = original_ai_output.get("shortlist_status", "")
        before["is_shortlisted"] = original_ai_output.get("is_shortlisted")

    if decision.override_type == "recruiter_notes":
        before["review_notes"] = original_ai_output.get("review_notes", "")

    return before


def _extract_after_values(
    final_result: Dict[str, Any],
    decision: OverrideDecision,
) -> Dict[str, Any]:
    return _extract_before_values(final_result, decision)


def _build_override_record(
    original_ai_output: Dict[str, Any],
    decision: OverrideDecision,
) -> OverrideRecord:
    return OverrideRecord(
        reviewer_id=decision.reviewer.reviewer_id,
        reviewer_name=decision.reviewer.reviewer_name,
        candidate_id=decision.candidate_id,
        override_type=decision.override_type,
        original_score=_extract_original_score(original_ai_output),
        override_score=decision.override_score,
        original_recommendation=original_ai_output.get("recommendation", ""),
        override_recommendation=decision.override_recommendation,
        reason=decision.reason,
        timestamp=decision.timestamp,
        review_notes=decision.review_notes,
        confidence=decision.confidence,
        source=decision.source,
    )
