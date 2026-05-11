from core.analytics.stability_schema import (
    normalize_stability_report,
    validate_stability_report,
)


def _report():
    return {
        "consistency_metrics": {
            "consistency_score": 1.0,
            "stability_ratio": 1.0,
            "deterministic_ordering_score": 1.0,
        },
        "drift_analysis": [],
        "movement_analysis": {},
        "normalization_validation": {},
        "ranking_position_validation": {},
        "stability_insights": ["Stable."],
    }


def test_normalize_stability_report_cleans_insights():
    report = normalize_stability_report({
        **_report(),
        "stability_insights": [" Stable. ", ""],
    })

    assert report["stability_insights"] == ["Stable."]


def test_validate_stability_report_accepts_complete_report():
    assert validate_stability_report(_report()) is True


def test_validate_stability_report_rejects_invalid_metric_range():
    report = _report()
    report["consistency_metrics"]["consistency_score"] = 2.0

    assert validate_stability_report(report) is False

