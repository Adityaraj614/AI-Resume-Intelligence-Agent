from core.workflow.recruiter_pipeline import (
    DEFAULT_MODULE_ORDER,
    RecruiterPipeline,
    RecruiterPipelineDependencies,
)
from core.workflow.workflow_schema import validate_workflow_result


def _ranked_candidates():
    return [
        {
            "candidate_id": "resume_001",
            "candidate_name": "Asha Rao",
            "ranking_position": 1,
            "final_score": 9.0,
            "semantic_score": 0.90,
            "confidence_score": 0.92,
            "confidence": 0.92,
            "hallucination_risk": 0.04,
            "evidence_quality": 0.88,
            "recommendation": "Strong Match",
            "extracted_skills": ["Python", "ML"],
            "missing_skills": [],
            "strengths": ["retrieval evidence"],
            "years_experience": 5,
        },
        {
            "candidate_id": "resume_002",
            "candidate_name": "Ben Lee",
            "ranking_position": 2,
            "final_score": 7.4,
            "semantic_score": 0.76,
            "confidence_score": 0.74,
            "confidence": 0.74,
            "hallucination_risk": 0.12,
            "evidence_quality": 0.66,
            "recommendation": "Moderate Match",
            "extracted_skills": ["Python", "SQL"],
            "missing_skills": ["Docker"],
            "years_experience": 3,
        },
        {
            "candidate_id": "resume_003",
            "candidate_name": "Chen Wu",
            "ranking_position": 3,
            "final_score": 4.0,
            "semantic_score": 0.40,
            "confidence_score": 0.35,
            "confidence": 0.35,
            "hallucination_risk": 0.10,
            "evidence_quality": 0.30,
            "recommendation": "Weak Match",
            "extracted_skills": ["Java"],
            "missing_skills": ["Python"],
            "years_experience": 1,
        },
    ]


def test_recruiter_pipeline_runs_end_to_end_workflow():
    result = RecruiterPipeline().run(
        _ranked_candidates(),
        recruiter_filters={"required_skills": ["python"], "strict_skills": False},
        execution_timestamp="2026-01-01T00:00:00Z",
    )

    assert validate_workflow_result(result) is True
    assert result["workflow_metadata"]["candidate_count"] == 3
    assert result["diagnostics"]["workflow_status"] == "completed"
    assert result["diagnostics"]["modules_executed"] == list(DEFAULT_MODULE_ORDER)
    assert [item["candidate_id"] for item in result["workflow_outputs"]["filtered_candidates"]] == [
        "resume_001",
        "resume_002",
    ]
    assert "Workflow completed successfully" in result["workflow_summary"]


def test_recruiter_pipeline_preserves_upstream_ranking_order():
    result = RecruiterPipeline().run(_ranked_candidates(), include_weak=True)

    assert [item["candidate_id"] for item in result["workflow_outputs"]["ranked_candidates"]] == [
        "resume_001",
        "resume_002",
        "resume_003",
    ]
    assert [item["candidate_id"] for item in result["workflow_outputs"]["shortlist"]] == [
        "resume_001",
        "resume_002",
        "resume_003",
    ]


def test_recruiter_pipeline_handles_empty_candidate_pool():
    result = RecruiterPipeline().run([])

    assert result["workflow_metadata"]["candidate_count"] == 0
    assert result["workflow_outputs"]["shortlist"] == []
    assert result["workflow_summary"] == (
        "Workflow completed with no candidates available for recruiter review."
    )
    assert result["diagnostics"]["workflow_status"] == "completed"


def test_recruiter_pipeline_exports_workflow_report():
    export_calls = []

    def export_writer(**kwargs):
        export_calls.append(kwargs)
        return {
            "export_format": kwargs["export_format"],
            "output_path": kwargs["output_path"],
        }

    output_path = "tests/export_outputs/workflow_report.json"
    dependencies = RecruiterPipelineDependencies(export_writer=export_writer)
    result = RecruiterPipeline(dependencies=dependencies).run(
        _ranked_candidates(),
        export_path=output_path,
        execution_timestamp="2026-01-01T00:00:00Z",
    )

    assert export_calls[0]["report_type"] == "recruiter_workflow"
    assert result["diagnostics"]["export_success"] is True
    assert result["workflow_outputs"]["export_metadata"]["output_path"] == output_path


def test_recruiter_pipeline_reports_export_failure_safely():
    def failing_export(**kwargs):
        raise OSError("export blocked")

    dependencies = RecruiterPipelineDependencies(export_writer=failing_export)
    result = RecruiterPipeline(dependencies=dependencies).run(
        _ranked_candidates(),
        export_path="tests/workflow_outputs/blocked.json",
    )

    assert result["diagnostics"]["workflow_status"] == "partial"
    assert result["diagnostics"]["failed_modules"] == {"export": "export blocked"}
    assert result["diagnostics"]["export_success"] is False


def test_recruiter_pipeline_continues_after_optional_module_failure():
    def failing_analytics(candidates):
        raise ValueError("analytics unavailable")

    dependencies = RecruiterPipelineDependencies(analytics_builder=failing_analytics)
    result = RecruiterPipeline(dependencies=dependencies).run(_ranked_candidates())

    assert result["diagnostics"]["workflow_status"] == "partial"
    assert result["workflow_outputs"]["analytics_report"] == {}
    assert "analytics" in result["diagnostics"]["failed_modules"]
    assert result["workflow_outputs"]["recruiter_report"]


def test_recruiter_pipeline_outputs_are_deterministic():
    first = RecruiterPipeline().run(_ranked_candidates())
    second = RecruiterPipeline().run(_ranked_candidates())

    assert first == second


def test_recruiter_pipeline_records_timing_metrics():
    result = RecruiterPipeline().run(_ranked_candidates())
    metrics = result["workflow_metrics"]

    assert metrics["ranking_duration"] == 1
    assert metrics["analytics_duration"] == 1
    assert metrics["export_duration"] == 1
    assert metrics["total_workflow_duration"] == len(DEFAULT_MODULE_ORDER)


def test_recruiter_pipeline_generates_filter_warnings_only_when_candidates_removed():
    result = RecruiterPipeline().run(
        _ranked_candidates(),
        recruiter_filters={"min_confidence": 0.90},
    )

    assert result["diagnostics"]["pipeline_warnings"] == [
        "1 candidates were removed by recruiter filters."
    ]


def test_recruiter_pipeline_does_not_leave_export_file_when_building_artifact_only():
    result = RecruiterPipeline().run(_ranked_candidates())

    assert result["workflow_outputs"]["export_metadata"]["output_path"] == ""
