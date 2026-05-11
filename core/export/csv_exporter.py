import csv
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


PREFERRED_CSV_FIELDS = (
    "ranking_position",
    "rank",
    "candidate_id",
    "candidate_name",
    "final_score",
    "confidence_score",
    "confidence",
    "semantic_score",
    "evidence_quality",
    "hallucination_risk",
    "recommendation",
    "bucket",
    "interview_priority",
    "hiring_readiness",
    "action_recommendation",
)


def _stringify_csv_value(value: Any) -> str:
    if value is None:
        return ""

    if isinstance(value, (list, tuple, set)):
        return "; ".join(str(item) for item in value)

    if isinstance(value, dict):
        return json.dumps(value, sort_keys=True, ensure_ascii=True)

    return str(value)


def flatten_record(record: Dict[str, Any],
                   parent_key: str = "") -> Dict[str, str]:
    """
    Flatten nested dictionaries into deterministic CSV-safe keys.
    """

    if not isinstance(record, dict):
        raise TypeError("record must be a dictionary.")

    flattened: Dict[str, str] = {}

    for key in sorted(record):
        value = record[key]
        flattened_key = f"{parent_key}.{key}" if parent_key else str(key)

        if isinstance(value, dict):
            flattened.update(flatten_record(value, flattened_key))
        else:
            flattened[flattened_key] = _stringify_csv_value(value)

    return flattened


def normalize_csv_rows(data: Any) -> List[Dict[str, str]]:
    """
    Convert common report shapes into flat CSV rows.
    """

    if isinstance(data, list):
        records = data
    elif isinstance(data, dict):
        for key in (
            "filtered_candidates",
            "candidate_decisions",
            "prioritized_interviews",
            "comparison_table",
            "ranking_overview",
            "drift_analysis",
        ):
            if isinstance(data.get(key), list):
                records = data[key]
                break
        else:
            records = [data]
    else:
        records = [{"value": data}]

    return [
        flatten_record(record if isinstance(record, dict) else {"value": record})
        for record in records
    ]


def resolve_csv_fieldnames(rows: List[Dict[str, str]],
                           fieldnames: Optional[Iterable[str]] = None) -> List[str]:
    if fieldnames:
        return [str(field) for field in fieldnames]

    discovered_fields = {
        field
        for row in rows
        for field in row
    }
    preferred = [
        field
        for field in PREFERRED_CSV_FIELDS
        if field in discovered_fields
    ]
    remaining = sorted(discovered_fields.difference(preferred))

    return preferred + remaining


def export_to_csv(
    data: Any,
    output_path: str,
    fieldnames: Optional[Iterable[str]] = None,
) -> List[Dict[str, str]]:
    """
    Export recruiter-friendly tabular rows to CSV.
    """

    rows = normalize_csv_rows(data)
    resolved_fieldnames = resolve_csv_fieldnames(rows, fieldnames)
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=resolved_fieldnames)
        writer.writeheader()

        for row in rows:
            writer.writerow({
                field: row.get(field, "")
                for field in resolved_fieldnames
            })

    return rows

