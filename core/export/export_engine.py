from typing import Any, Dict

from core.export.csv_exporter import export_to_csv
from core.export.export_schema import (
    DEFAULT_GENERATED_AT,
    normalize_export_payload,
    validate_export_payload,
)
from core.export.json_exporter import export_to_json
from core.export.report_builder import build_report_summary


def build_export_artifact(
    data: Any,
    report_type: str = "generic",
    generated_at: str = DEFAULT_GENERATED_AT,
) -> Dict[str, Any]:
    """
    Build an export-safe artifact without writing it to disk.
    """

    payload = normalize_export_payload(
        report_type=report_type,
        report_data=data,
        report_summary=build_report_summary(report_type, data),
        generated_at=generated_at,
    )

    if not validate_export_payload(payload):
        raise ValueError("Export artifact failed schema validation.")

    return payload


def export_report(
    data: Any,
    output_path: str,
    export_format: str = "json",
    report_type: str = "generic",
    generated_at: str = DEFAULT_GENERATED_AT,
) -> Dict[str, Any]:
    """
    Export platform reports in JSON or CSV format.
    """

    normalized_format = str(export_format).strip().lower()
    report_summary = build_report_summary(report_type, data)

    if normalized_format == "json":
        payload = export_to_json(
            data=data,
            output_path=output_path,
            report_type=report_type,
            report_summary=report_summary,
            generated_at=generated_at,
        )
        return {
            "export_format": "json",
            "output_path": output_path,
            "payload": payload,
        }

    if normalized_format == "csv":
        rows = export_to_csv(
            data=data,
            output_path=output_path,
        )
        return {
            "export_format": "csv",
            "output_path": output_path,
            "row_count": len(rows),
            "report_summary": report_summary,
        }

    raise ValueError("export_format must be 'json' or 'csv'.")

