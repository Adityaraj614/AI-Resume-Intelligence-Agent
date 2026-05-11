from core.rubric.rubric_formatter import (
    format_percentage,
    format_rubric_summary,
    format_rubric_table,
    format_weighted_total,
)
from core.rubric.rubric_mapper import map_candidate_to_rubric


def _breakdown():
    return map_candidate_to_rubric({
        "candidate_id": "resume_001",
        "candidate_name": "Asha Rao",
        "semantic_score": 0.9,
        "confidence_score": 0.8,
        "evidence_quality": 0.9,
        "extracted_skills": ["Python"],
        "experience": ["ML Engineer"],
        "education": ["MS Computer Science"],
        "projects": ["Search platform"],
        "profile_text": "Clear structured profile with projects and skills.",
    })


def test_format_percentage_supports_ratios_and_scores():
    assert format_percentage(0.3) == "30%"
    assert format_percentage(85) == "85%"
    assert format_percentage(0.875, digits=1) == "87.5%"


def test_format_rubric_table_is_export_friendly():
    rows = format_rubric_table(_breakdown())

    assert len(rows) == 5
    assert rows[0]["Dimension"] == "Skills Match"
    assert rows[0]["Weight"] == "30%"
    assert "Explanation" in rows[0]


def test_format_weighted_total_and_summary():
    breakdown = _breakdown()

    assert " / 100.00" in format_weighted_total(breakdown)
    assert "Asha Rao shows" in format_rubric_summary(breakdown)
    assert "Strongest dimension:" in format_rubric_summary(breakdown)
