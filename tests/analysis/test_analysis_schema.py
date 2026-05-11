from core.analysis.analysis_schema import (
    normalize_analysis_schema,
    validate_analysis_output,
)


def test_validate_analysis_output_accepts_complete_schema():
    analysis = {
        "candidate_id": "resume_001",
        "summary": "Evidence-grounded summary.",
        "strengths": ["Python evidence"],
        "missing_skills": ["No Docker evidence"],
        "evidence_used": ["Skills section matched requirements"],
        "recommendation": "Moderate Match",
    }

    assert validate_analysis_output(analysis) is True


def test_validate_analysis_output_rejects_missing_evidence_trace():
    analysis = {
        "candidate_id": "resume_001",
        "summary": "Evidence-grounded summary.",
        "strengths": ["Python evidence"],
        "missing_skills": [],
        "recommendation": "Moderate Match",
    }

    assert validate_analysis_output(analysis) is False


def test_normalize_analysis_schema_converts_strings_to_lists():
    raw_analysis = {
        "candidate_id": "resume_001",
        "summary": " Candidate aligns with retrieved evidence. ",
        "strengths": "Python evidence",
        "missing_skills": None,
        "evidence_used": "Skills section matched requirements",
        "recommendation": " Moderate Match ",
    }

    normalized = normalize_analysis_schema(raw_analysis)

    assert normalized["summary"] == "Candidate aligns with retrieved evidence."
    assert normalized["strengths"] == ["Python evidence"]
    assert normalized["missing_skills"] == []
    assert normalized["evidence_used"] == ["Skills section matched requirements"]
    assert normalized["recommendation"] == "Moderate Match"
