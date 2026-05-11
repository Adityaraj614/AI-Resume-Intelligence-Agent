from core.workflow.workflow_utils import (
    build_diagnostics,
    build_missing_candidate_warnings,
    build_workflow_id,
    build_workflow_metadata,
    build_workflow_summary,
)


def test_build_workflow_id_is_deterministic():
    candidates = [{"candidate_id": "a"}, {"candidate_id": "b"}]

    first = build_workflow_id(candidates, recruiter_filters={"min_confidence": 0.7})
    second = build_workflow_id(candidates, recruiter_filters={"min_confidence": 0.7})

    assert first == second
    assert first.startswith("workflow_")


def test_build_workflow_metadata_contains_session_fields():
    metadata = build_workflow_metadata(
        [{"candidate_id": "a"}],
        export_format="CSV",
        execution_timestamp="2026-01-01T00:00:00Z",
        completed_modules=["ranking"],
    )

    assert metadata["candidate_count"] == 1
    assert metadata["export_format"] == "csv"
    assert metadata["execution_timestamp"] == "2026-01-01T00:00:00Z"
    assert metadata["completed_modules"] == ["ranking"]


def test_build_diagnostics_reports_partial_failures_without_fake_warnings():
    diagnostics = build_diagnostics(
        modules_executed=["ranking", "export"],
        completed_modules=["ranking"],
        failed_modules={"export": "disk unavailable"},
        warnings=[],
        export_success=False,
    )

    assert diagnostics["workflow_status"] == "partial"
    assert diagnostics["pipeline_warnings"] == []
    assert diagnostics["failed_modules"] == {"export": "disk unavailable"}


def test_build_workflow_summary_is_template_based():
    assert build_workflow_summary(4, 2, 1) == (
        "Workflow completed successfully with 2 shortlisted candidates and "
        "1 priority interviews identified."
    )
    assert build_workflow_summary(0, 0, 0) == (
        "Workflow completed with no candidates available for recruiter review."
    )


def test_build_missing_candidate_warnings_counts_filtered_candidates():
    warnings = build_missing_candidate_warnings(
        [{"candidate_id": "a"}, {"candidate_id": "b"}],
        [{"candidate_id": "a"}],
    )

    assert warnings == ["1 candidates were removed by recruiter filters."]
