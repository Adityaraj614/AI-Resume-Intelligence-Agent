from statistics import median
from typing import Any, Dict, Iterable, List

from core.recruiter.comparison_utils import (
    get_evidence_quality,
    get_hallucination_risk,
    normalize_candidate_skills,
    normalize_missing_skills,
)
from core.recruiter.shortlist_utils import (
    bounded_float,
    get_confidence_score,
    normalize_score_to_10,
    sort_ranked_candidates,
)


SCORE_BUCKETS = {
    "excellent": (8.5, 10.0),
    "strong": (7.0, 8.5),
    "moderate": (5.5, 7.0),
    "weak": (0.0, 5.5),
}

RISK_BUCKETS = {
    "low": (0.0, 0.10),
    "medium": (0.10, 0.30),
    "high": (0.30, 1.0),
}

EVIDENCE_BUCKETS = {
    "strong": (0.75, 1.0),
    "usable": (0.45, 0.75),
    "weak": (0.0, 0.45),
}


def safe_round(value: float, digits: int = 4) -> float:
    return round(float(value), digits)


def safe_average(values: Iterable[float]) -> float:
    values = list(values)

    if not values:
        return 0.0

    return safe_round(sum(values) / len(values))


def safe_median(values: Iterable[float]) -> float:
    values = list(values)

    if not values:
        return 0.0

    return safe_round(float(median(values)))


def normalized_scores(candidates: List[Dict[str, Any]]) -> List[float]:
    return [
        safe_round(normalize_score_to_10(candidate.get("final_score", 0.0)))
        for candidate in candidates
    ]


def normalized_confidences(candidates: List[Dict[str, Any]]) -> List[float]:
    return [
        get_confidence_score(candidate)
        for candidate in candidates
    ]


def normalized_evidence_scores(candidates: List[Dict[str, Any]]) -> List[float]:
    return [
        get_evidence_quality(candidate)
        for candidate in candidates
    ]


def normalized_hallucination_risks(candidates: List[Dict[str, Any]]) -> List[float]:
    return [
        get_hallucination_risk(candidate)
        for candidate in candidates
    ]


def count_values(values: Iterable[str]) -> Dict[str, int]:
    counts: Dict[str, int] = {}

    for value in values:
        normalized_value = str(value).strip().lower()

        if not normalized_value:
            continue

        counts[normalized_value] = counts.get(normalized_value, 0) + 1

    return {
        key: counts[key]
        for key in sorted(counts)
    }


def top_count_items(counts: Dict[str, int],
                    limit: int = 10) -> List[Dict[str, Any]]:
    return [
        {"value": key, "count": count}
        for key, count in sorted(
            counts.items(),
            key=lambda item: (-item[1], item[0]),
        )[:limit]
    ]


def count_candidate_skills(candidates: List[Dict[str, Any]]) -> Dict[str, int]:
    skills = []

    for candidate in candidates:
        skills.extend(normalize_candidate_skills(candidate))

    return count_values(skills)


def count_missing_skills(candidates: List[Dict[str, Any]]) -> Dict[str, int]:
    missing_skills = []

    for candidate in candidates:
        missing_skills.extend(normalize_missing_skills(candidate))

    return count_values(missing_skills)


def bucket_numeric_values(values: List[float],
                          buckets: Dict[str, tuple]) -> Dict[str, int]:
    distribution = {bucket_name: 0 for bucket_name in buckets}

    for value in values:
        normalized_value = float(value)

        for bucket_name, (minimum, maximum) in buckets.items():
            is_last_bucket = bucket_name == list(buckets.keys())[-1]

            if minimum <= normalized_value <= maximum if is_last_bucket else minimum <= normalized_value < maximum:
                distribution[bucket_name] += 1
                break

    return distribution


def candidate_ratio(count: int,
                    total: int) -> float:
    if total <= 0:
        return 0.0

    return safe_round(count / total)


def sort_candidates_for_analytics(candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if not isinstance(candidates, list):
        raise TypeError("candidates must be a list.")

    return sort_ranked_candidates(candidates)


def get_bucket(candidate: Dict[str, Any]) -> str:
    return str(candidate.get("bucket", "UNBUCKETED")).strip() or "UNBUCKETED"


def get_bounded_semantic_score(candidate: Dict[str, Any]) -> float:
    return bounded_float(candidate.get("semantic_score", 0.0), 0.0, 1.0)

