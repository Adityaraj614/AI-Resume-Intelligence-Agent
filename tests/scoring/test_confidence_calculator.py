from core.scoring.confidence_calculator import (
    calculate_confidence,
    confidence_from_evidence_density,
    normalize_confidence,
)


def _candidate_metadata():
    return {
        "candidate_id": "resume_001",
        "aggregate_score": 0.82,
        "jd_match_coverage": 0.80,
        "match_count": 3,
        "matched_sections": ["skills", "projects"],
        "matches": [
            {"score": 0.90},
            {"score": 0.84},
            {"score": 0.80},
        ],
    }


def _analysis():
    return {
        "candidate_id": "resume_001",
        "summary": "Evidence-grounded analysis.",
        "strengths": ["Python", "NLP"],
        "missing_skills": ["Docker"],
        "evidence_used": ["skills matched requirements", "projects matched responsibilities"],
        "recommendation": "Moderate Match",
    }


def test_normalize_confidence_clamps_values():
    assert normalize_confidence(-0.5) == 0.0
    assert normalize_confidence(0.5) == 0.5
    assert normalize_confidence(1.5) == 1.0


def test_confidence_from_evidence_density_is_bounded():
    confidence = confidence_from_evidence_density(
        match_count=3,
        matched_section_count=2,
        evidence_trace_count=2,
    )

    assert 0 <= confidence <= 1
    assert confidence > 0.5


def test_calculate_confidence_is_deterministic_and_explainable():
    first = calculate_confidence(_candidate_metadata(), _analysis())
    second = calculate_confidence(_candidate_metadata(), _analysis())

    assert first == second
    assert 0 <= first <= 1
    assert first > 0.6
