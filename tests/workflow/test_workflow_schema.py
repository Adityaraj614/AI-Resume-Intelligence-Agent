from core.workflow.workflow_schema import (
    normalize_workflow_result,
    validate_workflow_metadata,
    validate_workflow_result,
)


def _metadata():
    return {
        "workflow_id": "workflow_123",
        "execution_timestamp": "not_provided",
        "candidate_count": 0,
        "export_format": "json",
        "completed_modules": [],
        "schema_version": "1.0",
    }


def test_validate_workflow_metadata_accepts_required_fields():
    assert validate_workflow_metadata(_metadata()) is True


def test_normalize_workflow_result_adds_required_output_keys():
    result = normalize_workflow_result(
        workflow_metadata=_metadata(),
        workflow_summary="Workflow completed.",
        workflow_outputs={},
        workflow_metrics={"total_workflow_duration": 0},
        diagnostics={"workflow_status": "completed"},
    )

    assert validate_workflow_result(result) is True
    assert "shortlist" in result["workflow_outputs"]
    assert "export_metadata" in result["workflow_outputs"]


def test_validate_workflow_result_rejects_missing_metadata_fields():
    result = normalize_workflow_result(
        workflow_metadata={"workflow_id": "workflow_123"},
        workflow_summary="Workflow completed.",
        workflow_outputs={},
        workflow_metrics={},
        diagnostics={},
    )

    assert validate_workflow_result(result) is False
