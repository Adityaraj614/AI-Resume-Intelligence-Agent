from typing import Any, Dict, List

from core.recruiter.comparison_utils import (
    get_evidence_quality,
    get_hallucination_risk,
)
from core.recruiter.shortlist_utils import (
    get_confidence_score,
    normalize_score_to_10,
)


def tie_break_key(candidate: Dict[str, Any]) -> tuple:
    """
    Deterministic tie-break key for ranking validation diagnostics.
    """

    return (
        -get_confidence_score(candidate),
        get_hallucination_risk(candidate),
        -get_evidence_quality(candidate),
        str(candidate.get("candidate_id", "")),
    )


def stable_ranking_sort(candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Sort candidates by score, then deterministic tie-breakers.
    """

    if not isinstance(candidates, list):
        raise TypeError("candidates must be a list.")

    return sorted(
        candidates,
        key=lambda candidate: (
            -normalize_score_to_10(candidate.get("final_score", 0.0)),
            *tie_break_key(candidate),
        ),
    )


def validate_tie_break_order(candidates: List[Dict[str, Any]]) -> bool:
    """
    Check whether equally scored candidates follow deterministic tie-break order.
    """

    if not isinstance(candidates, list):
        return False

    expected_order = [
        str(candidate.get("candidate_id", ""))
        for candidate in stable_ranking_sort(candidates)
    ]
    actual_order = [
        str(candidate.get("candidate_id", ""))
        for candidate in candidates
    ]

    return actual_order == expected_order

