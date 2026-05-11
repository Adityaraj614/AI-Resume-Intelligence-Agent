import json
from io import BytesIO

import pytest

from app.pages.dashboard import run_dashboard_analysis
from core.workflow.dashboard_workflow import DashboardWorkflowError, run_dashboard_workflow
from core.workflow.workflow_schema import validate_workflow_result


class UploadedBytes(BytesIO):
    def __init__(self, name, payload):
        super().__init__(payload)
        self.name = name

    def getvalue(self):
        return super().getvalue()


def _linkedin_upload(name="john.json"):
    profile = {
        "name": "John Doe",
        "headline": "Machine Learning Engineer",
        "summary": "Builds retrieval systems with Python and FAISS.",
        "skills": ["Python", "Machine Learning", "FAISS"],
        "experience": [
            {
                "title": "ML Engineer",
                "company": "Example AI",
                "description": "Built retrieval systems and semantic search workflows.",
            }
        ],
        "education": [
            {
                "school": "Example University",
                "degree": "MS",
                "field_of_study": "Computer Science",
            }
        ],
        "projects": ["Resume intelligence platform with FAISS retrieval"],
    }

    return UploadedBytes(name, json.dumps(profile).encode("utf-8"))


def _inputs():
    return {
        "job_description": "Python machine learning engineer with FAISS retrieval experience",
        "jd_file": None,
        "resume_files": [],
        "linkedin_files": [_linkedin_upload()],
    }


def test_dashboard_workflow_runs_real_orchestration_for_linkedin_candidate(monkeypatch):
    monkeypatch.setenv("DISABLE_TRANSFORMER_MODEL", "1")

    workflow_result = run_dashboard_workflow(_inputs())

    assert validate_workflow_result(workflow_result) is True
    assert workflow_result["workflow_metadata"]["candidate_count"] == 1
    ranked = workflow_result["workflow_outputs"]["ranked_candidates"]
    assert ranked[0]["candidate_name"] == "John Doe"
    assert ranked[0]["source"] == "linkedin"
    assert ranked[0]["matches"]
    assert workflow_result["workflow_outputs"]["analytics_report"]
    assert workflow_result["workflow_outputs"]["recruiter_report"]


def test_dashboard_page_entrypoint_delegates_to_backend_workflow(monkeypatch):
    monkeypatch.setenv("DISABLE_TRANSFORMER_MODEL", "1")

    workflow_result = run_dashboard_analysis(_inputs())

    assert validate_workflow_result(workflow_result) is True
    assert workflow_result["workflow_outputs"]["pipeline_debug"]["ranked_candidate_count"] == 1


def test_dashboard_workflow_reports_invalid_inputs_cleanly(monkeypatch):
    monkeypatch.setenv("DISABLE_TRANSFORMER_MODEL", "1")

    with pytest.raises(DashboardWorkflowError) as exc:
        run_dashboard_workflow({
            "job_description": "",
            "jd_file": None,
            "resume_files": [],
            "linkedin_files": [_linkedin_upload()],
        })

    assert "job description" in str(exc.value).lower()


def test_dashboard_workflow_preserves_warnings_for_bad_linkedin_file(monkeypatch):
    monkeypatch.setenv("DISABLE_TRANSFORMER_MODEL", "1")
    inputs = _inputs()
    inputs["linkedin_files"].append(UploadedBytes("broken.json", b"{not json"))

    workflow_result = run_dashboard_workflow(inputs)

    assert validate_workflow_result(workflow_result) is True
    warnings = workflow_result["diagnostics"]["pipeline_warnings"]
    assert any("broken.json could not be processed" in warning for warning in warnings)
