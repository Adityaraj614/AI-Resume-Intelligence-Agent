from core.workflow.workflow_manager import WorkflowManager, run_recruiter_workflow


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
            "extracted_skills": ["Python"],
        }
    ]


def test_run_recruiter_workflow_facade_returns_unified_output():
    result = run_recruiter_workflow(_ranked_candidates())

    assert result["workflow_metadata"]["candidate_count"] == 1
    assert "decision_support" in result["workflow_outputs"]
    assert "workflow_status" in result["diagnostics"]


def test_workflow_manager_orchestrates_recruiter_session():
    manager = WorkflowManager()
    result = manager.run_recruiter_workflow(
        _ranked_candidates(),
        export_format="csv",
    )

    assert result["workflow_metadata"]["export_format"] == "csv"
    assert result["workflow_outputs"]["export_metadata"]["export_format"] == "csv"
