import json

import pytest

from core.export.export_engine import (
    build_export_artifact,
    export_report,
)


EXPORT_OUTPUT_DIR = "tests/export_outputs"


def test_build_export_artifact_adds_summary_and_metadata():
    artifact = build_export_artifact(
        data=[{"candidate_id": "resume_001"}],
        report_type="ranked_candidates",
        generated_at="2026-01-01T00:00:00Z",
    )

    assert artifact["export_metadata"]["report_type"] == "ranked_candidates"
    assert artifact["report_summary"] == "Ranking export contains 1 candidates."


def test_export_report_supports_json():
    output_path = f"{EXPORT_OUTPUT_DIR}/analytics.json"
    result = export_report(
        data={"candidate_pool_summary": {"total_candidates": 1}},
        output_path=output_path,
        export_format="json",
        report_type="analytics",
    )
    with open(output_path, encoding="utf-8") as json_file:
        written = json.load(json_file)

    assert result["export_format"] == "json"
    assert written["export_metadata"]["report_type"] == "analytics"


def test_export_report_supports_csv():
    output_path = f"{EXPORT_OUTPUT_DIR}/decision.csv"
    result = export_report(
        data={
            "candidate_decisions": [
                {
                    "candidate_id": "resume_001",
                    "candidate_name": "Asha Rao",
                    "interview_priority": "PRIORITY_INTERVIEW",
                }
            ]
        },
        output_path=output_path,
        export_format="csv",
        report_type="decision_support",
    )

    assert result["export_format"] == "csv"
    assert result["row_count"] == 1
    with open(output_path, encoding="utf-8") as csv_file:
        assert "PRIORITY_INTERVIEW" in csv_file.read()


def test_export_report_rejects_unknown_format():
    with pytest.raises(ValueError):
        export_report(
            data=[],
            output_path=f"{EXPORT_OUTPUT_DIR}/report.txt",
            export_format="xml",
        )
