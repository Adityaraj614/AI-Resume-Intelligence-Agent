import csv
import io
from typing import Any, Dict, List

import streamlit as st

from core.export.csv_exporter import normalize_csv_rows, resolve_csv_fieldnames
from core.export.export_engine import build_export_artifact
from core.export.json_exporter import serialize_to_json


def render_export_buttons(
    workflow_result: Dict[str, Any],
    final_candidates: List[Dict[str, Any]],
    override_history: List[Dict[str, Any]],
    session_summary: Dict[str, Any],
) -> None:
    exports = build_export_downloads(
        workflow_result,
        final_candidates,
        override_history,
        session_summary,
    )
    columns = st.columns(3, gap="small")

    with columns[0]:
        st.download_button(
            "Download Workflow Outputs (JSON)",
            data=exports["workflow_json"],
            file_name="recruiter_workflow_outputs.json",
            mime="application/json",
            width="stretch",
        )

    with columns[1]:
        st.download_button(
            "Download Ranked Candidates (CSV)",
            data=exports["ranked_csv"],
            file_name="ranked_candidates.csv",
            mime="text/csv",
            width="stretch",
        )

    with columns[2]:
        st.download_button(
            "Download Recruiter Summary (JSON)",
            data=exports["summary_json"],
            file_name="recruiter_summary.json",
            mime="application/json",
            width="stretch",
        )


def build_export_downloads(
    workflow_result: Dict[str, Any],
    final_candidates: List[Dict[str, Any]],
    override_history: List[Dict[str, Any]],
    session_summary: Dict[str, Any],
) -> Dict[str, str]:
    generated_at = _generated_at(workflow_result)
    workflow_bundle = {
        "workflow_result": workflow_result or {},
        "final_ranked_candidates": final_candidates,
        "override_history": override_history,
        "session_summary": session_summary,
    }
    workflow_artifact = build_export_artifact(
        data=workflow_bundle,
        report_type="workflow_outputs",
        generated_at=generated_at,
    )
    recruiter_report = _build_summary_report(workflow_result, override_history, session_summary)
    summary_artifact = build_export_artifact(
        data=recruiter_report,
        report_type="recruiter_summary",
        generated_at=generated_at,
    )

    return {
        "workflow_json": serialize_to_json(workflow_artifact),
        "ranked_csv": _csv_string(final_candidates),
        "summary_json": serialize_to_json(summary_artifact),
    }


def _build_summary_report(
    workflow_result: Dict[str, Any],
    override_history: List[Dict[str, Any]],
    session_summary: Dict[str, Any],
) -> Dict[str, Any]:
    outputs = workflow_result.get("workflow_outputs", {}) if isinstance(workflow_result, dict) else {}
    recruiter_report = outputs.get("recruiter_report", {})

    if not isinstance(recruiter_report, dict):
        recruiter_report = {}

    recruiter_report = dict(recruiter_report)
    recruiter_report["session_summary"] = session_summary
    recruiter_report["override_count"] = len(override_history)
    recruiter_report["override_candidate_ids"] = sorted({
        str(entry.get("candidate_id", ""))
        for entry in override_history
        if isinstance(entry, dict) and entry.get("candidate_id")
    })

    return recruiter_report


def _csv_string(data: Any) -> str:
    rows = normalize_csv_rows(data)
    fieldnames = resolve_csv_fieldnames(rows)
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fieldnames)
    writer.writeheader()

    for row in rows:
        writer.writerow({
            field: row.get(field, "")
            for field in fieldnames
        })

    return buffer.getvalue()


def _generated_at(workflow_result: Dict[str, Any]) -> str:
    metadata = workflow_result.get("workflow_metadata", {}) if isinstance(workflow_result, dict) else {}
    return str(metadata.get("execution_timestamp", "not_provided"))
