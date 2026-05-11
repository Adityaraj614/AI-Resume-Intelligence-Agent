from typing import Any, Dict, List, Optional

from core.analytics.analytics_utils import candidate_ratio, safe_average, safe_round
from core.analytics.drift_detector import (
    analyze_candidate_movement,
    detect_ranking_drift,
)
from core.analytics.normalization_validator import (
    validate_ranking_positions,
    validate_score_normalization,
)
from core.analytics.stability_schema import (
    normalize_stability_report,
    validate_stability_report,
)
from core.analytics.tie_breaker import validate_tie_break_order


def validate_ranking_consistency(rankings: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Validate one ranking output for deterministic ordering and rank integrity.
    """

    if not isinstance(rankings, list):
        raise TypeError("rankings must be a list.")

    if not rankings:
        return {
            "is_consistent": True,
            "consistency_score": 1.0,
            "deterministic_ordering_score": 1.0,
            "candidate_count": 0,
        }

    position_validation = validate_ranking_positions(rankings)
    deterministic_order = validate_tie_break_order(rankings)
    valid_position_score = 1.0 if position_validation["is_valid"] else 0.0
    deterministic_ordering_score = 1.0 if deterministic_order else 0.0
    consistency_score = safe_round(
        (valid_position_score + deterministic_ordering_score) / 2
    )

    return {
        "is_consistent": consistency_score == 1.0,
        "consistency_score": consistency_score,
        "deterministic_ordering_score": deterministic_ordering_score,
        "candidate_count": len(rankings),
    }


def check_reproducibility(first_run: List[Dict[str, Any]],
                          second_run: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Check whether repeated ranking outputs are exactly reproducible by candidate order.
    """

    first_order = [
        str(candidate.get("candidate_id", ""))
        for candidate in first_run
    ]
    second_order = [
        str(candidate.get("candidate_id", ""))
        for candidate in second_run
    ]
    is_reproducible = first_order == second_order

    return {
        "is_reproducible": is_reproducible,
        "first_order": first_order,
        "second_order": second_order,
        "reproducibility_score": 1.0 if is_reproducible else 0.0,
    }


def calculate_stability_metrics(drift_records: List[Dict[str, Any]],
                                deterministic_ordering_score: float = 1.0) -> Dict[str, Any]:
    if not drift_records:
        return {
            "average_rank_shift": 0.0,
            "stability_ratio": 1.0,
            "volatile_candidate_count": 0,
            "deterministic_ordering_score": deterministic_ordering_score,
        }

    average_rank_shift = safe_average(
        record["absolute_rank_shift"]
        for record in drift_records
    )
    volatile_count = len([
        record
        for record in drift_records
        if record["is_significant"]
    ])
    stable_count = len([
        record
        for record in drift_records
        if record["movement"] == "stable"
    ])

    return {
        "average_rank_shift": average_rank_shift,
        "stability_ratio": candidate_ratio(stable_count, len(drift_records)),
        "volatile_candidate_count": volatile_count,
        "deterministic_ordering_score": deterministic_ordering_score,
    }


def generate_stability_insights(report: Dict[str, Any]) -> List[str]:
    insights = []
    metrics = report.get("consistency_metrics", {})
    movement = report.get("movement_analysis", {})
    normalization = report.get("normalization_validation", {})

    if metrics.get("consistency_score", 1.0) >= 0.90:
        insights.append("Ranking consistency remains high.")
    else:
        insights.append("Ranking consistency needs review.")

    volatile_count = movement.get("volatile_count", 0)

    if volatile_count:
        insights.append(f"{volatile_count} candidates experienced significant ranking drift.")
    else:
        insights.append("No significant ranking drift detected.")

    stable_count = movement.get("stable_count", 0)

    if stable_count:
        insights.append(f"{stable_count} candidates remained stable across runs.")

    if not normalization.get("is_valid", True):
        insights.append(
            f"{normalization.get('anomaly_count', 0)} score normalization anomalies detected."
        )
    else:
        insights.append("Score normalization validation passed.")

    return insights


def build_ranking_stability_report(
    current_rankings: List[Dict[str, Any]],
    previous_rankings: Optional[List[Dict[str, Any]]] = None,
    significant_shift: int = 3,
) -> Dict[str, Any]:
    """
    Build production-safe ranking stability diagnostics.
    """

    previous_rankings = previous_rankings or []
    consistency = validate_ranking_consistency(current_rankings)
    drift_records = detect_ranking_drift(
        previous_rankings,
        current_rankings,
        significant_shift=significant_shift,
    )
    movement = analyze_candidate_movement(drift_records)
    stability_metrics = calculate_stability_metrics(
        drift_records,
        deterministic_ordering_score=consistency["deterministic_ordering_score"],
    )
    consistency_metrics = {
        **consistency,
        **stability_metrics,
    }
    report = normalize_stability_report({
        "consistency_metrics": consistency_metrics,
        "drift_analysis": drift_records,
        "movement_analysis": movement,
        "normalization_validation": validate_score_normalization(current_rankings),
        "ranking_position_validation": validate_ranking_positions(current_rankings),
    })
    report["stability_insights"] = generate_stability_insights(report)

    if not validate_stability_report(report):
        raise ValueError("Ranking stability report failed schema validation.")

    return report

