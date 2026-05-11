from typing import Any, Dict, List

from core.recruiter.shortlist_utils import (
    bounded_float,
    get_confidence_score,
    get_ranking_position,
    normalize_score_to_10,
    sort_ranked_candidates,
)


def normalize_list_field(value: Any) -> List[str]:
    """
    Normalize list-like candidate fields into deterministic lowercase strings.
    """

    if value is None:
        return []

    if isinstance(value, str):
        values = [value]
    elif isinstance(value, list):
        values = value
    else:
        values = [value]

    normalized_values = {
        str(item).strip().lower()
        for item in values
        if str(item).strip()
    }

    return sorted(normalized_values)


def normalize_candidate_skills(candidate: Dict[str, Any]) -> List[str]:
    return normalize_list_field(candidate.get("extracted_skills", candidate.get("skills", [])))


def normalize_missing_skills(candidate: Dict[str, Any]) -> List[str]:
    return normalize_list_field(candidate.get("missing_skills", []))


def normalize_strengths(candidate: Dict[str, Any]) -> List[str]:
    return normalize_list_field(candidate.get("strengths", []))


def normalize_weaknesses(candidate: Dict[str, Any]) -> List[str]:
    return normalize_list_field(candidate.get("weaknesses", candidate.get("gaps", [])))


def get_evidence_quality(candidate: Dict[str, Any]) -> float:
    return bounded_float(
        candidate.get("evidence_quality", candidate.get("evidence_coverage", 0.0)),
        0.0,
        1.0,
    )


def get_semantic_score(candidate: Dict[str, Any]) -> float:
    return bounded_float(candidate.get("semantic_score", 0.0), 0.0, 1.0)


def get_hallucination_risk(candidate: Dict[str, Any]) -> float:
    return bounded_float(candidate.get("hallucination_risk", 0.0), 0.0, 1.0)


def build_candidate_summary(candidate: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build a stable comparison-ready candidate summary.
    """

    candidate_id = str(candidate.get("candidate_id", "unknown_candidate")).strip()
    candidate_id = candidate_id or "unknown_candidate"

    return {
        "candidate_id": candidate_id,
        "candidate_name": str(candidate.get("candidate_name", candidate_id)).strip() or candidate_id,
        "ranking_position": get_ranking_position(candidate),
        "final_score": round(normalize_score_to_10(candidate.get("final_score", 0.0)), 4),
        "semantic_score": get_semantic_score(candidate),
        "confidence_score": get_confidence_score(candidate),
        "hallucination_risk": get_hallucination_risk(candidate),
        "evidence_quality": get_evidence_quality(candidate),
        "recommendation": str(candidate.get("recommendation", "")).strip(),
        "bucket": str(candidate.get("bucket", "")).strip(),
        "skills": normalize_candidate_skills(candidate),
        "missing_skills": normalize_missing_skills(candidate),
        "strengths": normalize_strengths(candidate),
        "weaknesses": normalize_weaknesses(candidate),
    }


def compare_numeric_signal(candidate_a: Dict[str, Any],
                           candidate_b: Dict[str, Any],
                           field: str,
                           higher_is_better: bool = True) -> Dict[str, Any]:
    """
    Compare a numeric field and return a deterministic winner label.
    """

    value_a = float(candidate_a.get(field, 0.0))
    value_b = float(candidate_b.get(field, 0.0))
    delta = round(value_a - value_b, 4)

    if value_a == value_b:
        preferred = "tie"
    elif higher_is_better:
        preferred = "candidate_a" if value_a > value_b else "candidate_b"
    else:
        preferred = "candidate_a" if value_a < value_b else "candidate_b"

    return {
        "candidate_a": value_a,
        "candidate_b": value_b,
        "delta": delta,
        "preferred": preferred,
    }


def sort_candidates_for_comparison(candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Preserve upstream ranking order for comparison views.
    """

    if not isinstance(candidates, list):
        raise TypeError("candidates must be a list.")

    return sort_ranked_candidates(candidates)
