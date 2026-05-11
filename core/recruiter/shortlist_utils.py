from typing import Any, Dict, List


BUCKET_PRIORITY = {
    "STRONG_MATCH": 0,
    "GOOD_MATCH": 1,
    "POTENTIAL_MATCH": 2,
    "WEAK_MATCH": 3,
}


def bounded_float(value: Any,
                  minimum: float,
                  maximum: float) -> float:
    number = float(value)

    return float(min(max(number, minimum), maximum))


def normalize_score_to_10(score: Any) -> float:
    """
    Normalize ranking scores to a 0-10 scale while accepting 0-100 inputs.
    """

    number = float(score)

    if number > 10:
        number = number / 10

    return bounded_float(number, 0.0, 10.0)


def get_confidence_score(candidate: Dict[str, Any]) -> float:
    """
    Support both ranking confidence and recruiter confidence_score fields.
    """

    return bounded_float(
        candidate.get("confidence_score", candidate.get("confidence", 0.0)),
        0.0,
        1.0,
    )


def get_ranking_position(candidate: Dict[str, Any]) -> int:
    """
    Preserve the upstream deterministic ranking position.
    """

    return int(candidate.get("ranking_position", candidate.get("rank", 0)) or 0)


def get_warning_flags(candidate: Dict[str, Any]) -> List[str]:
    warning_flags = candidate.get("warning_flags", [])

    if not isinstance(warning_flags, list):
        return []

    return [str(flag) for flag in warning_flags]


def sort_ranked_candidates(ranked_candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Sort by upstream rank first, then deterministic tie-breakers.
    """

    if not isinstance(ranked_candidates, list):
        raise TypeError("ranked_candidates must be a list.")

    return sorted(
        ranked_candidates,
        key=lambda candidate: (
            get_ranking_position(candidate) or 10**9,
            -normalize_score_to_10(candidate.get("final_score", 0.0)),
            -get_confidence_score(candidate),
            bounded_float(candidate.get("hallucination_risk", 0.0), 0.0, 1.0),
            str(candidate.get("candidate_id", "")),
        ),
    )


def truncate_shortlist(shortlist_items: List[Dict[str, Any]],
                       top_k: int) -> List[Dict[str, Any]]:
    if top_k < 0:
        raise ValueError("top_k cannot be negative.")

    return shortlist_items[:top_k]

