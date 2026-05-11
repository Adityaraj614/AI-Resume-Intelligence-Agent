from typing import Any, Dict, List

from core.rubric.rubric_utils import clean_text


def format_percentage(value: Any, digits: int = 0) -> str:
    number = float(value or 0.0)

    if number <= 1.0:
        number *= 100.0

    return f"{number:.{digits}f}%"


def format_weighted_total(breakdown: Dict[str, Any]) -> str:
    summary = breakdown.get("summary", {}) if isinstance(breakdown, dict) else {}
    total = float(summary.get("total_weighted_score", 0.0) or 0.0)
    maximum = float(summary.get("max_weighted_score", 100.0) or 100.0)

    return f"{total:.2f} / {maximum:.2f}"


def format_rubric_table(breakdown: Dict[str, Any]) -> List[Dict[str, str]]:
    scores = breakdown.get("scores", []) if isinstance(breakdown, dict) else []
    rows = []

    for score in scores:
        if not isinstance(score, dict):
            continue

        rows.append({
            "Dimension": clean_text(score.get("dimension_name")),
            "Weight": format_percentage(score.get("weight", 0.0)),
            "Raw Score": format_percentage(float(score.get("raw_score", 0.0) or 0.0) / 100.0),
            "Weighted Score": f"{float(score.get('weighted_score', 0.0) or 0.0):.2f}",
            "Confidence": format_percentage(score.get("confidence", 0.0)),
            "Evidence Fields": ", ".join(score.get("source_fields", [])),
            "Explanation": clean_text(score.get("explanation")),
        })

    return rows


def format_rubric_summary(breakdown: Dict[str, Any]) -> str:
    summary = breakdown.get("summary", {}) if isinstance(breakdown, dict) else {}
    candidate_name = clean_text(summary.get("candidate_name", breakdown.get("candidate_name", "Candidate")))
    label = clean_text(summary.get("overall_label", "Unknown"))
    percentage = format_percentage(summary.get("overall_percentage", 0.0))
    strongest = clean_text(summary.get("strongest_dimension", "not available"))
    weakest = clean_text(summary.get("weakest_dimension", "not available"))

    return (
        f"{candidate_name} shows {label.lower()} rubric alignment at {percentage}. "
        f"Strongest dimension: {strongest}. Weakest dimension: {weakest}."
    )
