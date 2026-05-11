from typing import Any, Dict


REQUIRED_STABILITY_KEYS = (
    "consistency_metrics",
    "drift_analysis",
    "movement_analysis",
    "normalization_validation",
    "ranking_position_validation",
    "stability_insights",
)


def normalize_stability_report(report: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(report, dict):
        raise TypeError("report must be a dictionary.")

    return {
        "consistency_metrics": report.get("consistency_metrics", {}),
        "drift_analysis": report.get("drift_analysis", []),
        "movement_analysis": report.get("movement_analysis", {}),
        "normalization_validation": report.get("normalization_validation", {}),
        "ranking_position_validation": report.get("ranking_position_validation", {}),
        "stability_insights": [
            str(insight).strip()
            for insight in report.get("stability_insights", [])
            if str(insight).strip()
        ],
    }


def validate_stability_report(report: Dict[str, Any]) -> bool:
    if not isinstance(report, dict):
        return False

    for key in REQUIRED_STABILITY_KEYS:
        if key not in report:
            return False

    metrics = report["consistency_metrics"]

    if not isinstance(metrics, dict):
        return False

    for metric in (
        "consistency_score",
        "stability_ratio",
        "deterministic_ordering_score",
    ):
        if metric in metrics and not 0 <= metrics[metric] <= 1:
            return False

    if not isinstance(report["drift_analysis"], list):
        return False

    if not isinstance(report["movement_analysis"], dict):
        return False

    if not isinstance(report["normalization_validation"], dict):
        return False

    if not isinstance(report["ranking_position_validation"], dict):
        return False

    if not isinstance(report["stability_insights"], list):
        return False

    return True

