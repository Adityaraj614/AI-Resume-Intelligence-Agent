from core.analysis.candidate_analyzer import analyze_candidate_match
from core.analysis.reasoning_utils import (
    build_evidence_trace,
    interpret_similarity_score,
    recommend_from_scores,
)
from core.llm.evidence_builder import build_evidence_context
from core.llm.llm_client import LLMClient
from core.llm.providers import LLMProvider


def _jd_chunks():
    return [
        {
            "section": "requirements",
            "chunk_text": "Python and NLP experience",
        },
        {
            "section": "responsibilities",
            "chunk_text": "Build transformer applications",
        },
    ]


def _matches():
    return [
        {
            "candidate_id": "resume_001",
            "section": "skills",
            "score": 0.91,
            "jd_section": "requirements",
            "jd_chunk_text": "Python and NLP experience",
            "chunk_text": "Experienced in Python, NLP, and PyTorch.",
        },
        {
            "candidate_id": "resume_001",
            "section": "projects",
            "score": 0.84,
            "jd_section": "responsibilities",
            "jd_chunk_text": "Build transformer applications",
            "chunk_text": "Built transformer-based text classifier.",
        },
    ]


def _candidate_metadata():
    return {
        "candidate_id": "resume_001",
        "aggregate_score": 0.82,
        "jd_match_coverage": 1.0,
        "match_count": 2,
        "matched_sections": ["skills", "projects"],
        "matches": _matches(),
    }


def test_candidate_analyzer_returns_structured_mock_analysis():
    context = build_evidence_context(
        jd_chunks=_jd_chunks(),
        candidate_result=_candidate_metadata(),
    )
    client = LLMClient(provider=LLMProvider.MOCK)

    analysis = analyze_candidate_match(
        structured_evidence_context=context,
        candidate_metadata=_candidate_metadata(),
        jd_chunks=_jd_chunks(),
        llm_client=client,
    )

    assert analysis["candidate_id"] == "resume_001"
    assert analysis["summary"]
    assert analysis["strengths"]
    assert analysis["missing_skills"]
    assert analysis["recommendation"] == "Moderate Match"
    assert analysis["evidence_used"]
    assert "skills section matched requirements" in analysis["evidence_used"][0]


def test_candidate_analyzer_is_deterministic_with_mock_provider():
    context = build_evidence_context(
        jd_chunks=_jd_chunks(),
        candidate_result=_candidate_metadata(),
    )
    client = LLMClient(provider=LLMProvider.MOCK)

    first = analyze_candidate_match(
        structured_evidence_context=context,
        candidate_metadata=_candidate_metadata(),
        jd_chunks=_jd_chunks(),
        llm_client=client,
    )
    second = analyze_candidate_match(
        structured_evidence_context=context,
        candidate_metadata=_candidate_metadata(),
        jd_chunks=_jd_chunks(),
        llm_client=client,
    )

    assert first == second


def test_evidence_trace_preserves_retrieval_metadata():
    trace = build_evidence_trace(_matches())

    assert trace == [
        "skills section matched requirements (strong semantic match, score 0.91)",
        "projects section matched responsibilities (moderate semantic match, score 0.84)",
    ]


def test_similarity_interpretation_and_recommendation_are_conservative():
    assert interpret_similarity_score(0.90) == "strong semantic match"
    assert interpret_similarity_score(0.70) == "moderate semantic match"
    assert interpret_similarity_score(0.50) == "weak semantic match"
    assert interpret_similarity_score(0.20) == "low-confidence match"

    assert recommend_from_scores({
        "aggregate_score": 0.90,
        "jd_match_coverage": 0.80,
    }) == "Strong Match"
    assert recommend_from_scores({
        "aggregate_score": 0.70,
        "jd_match_coverage": 0.50,
    }) == "Moderate Match"
    assert recommend_from_scores({
        "aggregate_score": 0.40,
        "jd_match_coverage": 0.20,
    }) == "Needs Review"


def test_candidate_analyzer_rejects_empty_context():
    client = LLMClient(provider=LLMProvider.MOCK)

    try:
        analyze_candidate_match(
            structured_evidence_context="",
            candidate_metadata=_candidate_metadata(),
            jd_chunks=_jd_chunks(),
            llm_client=client,
        )
        assert False
    except ValueError as error:
        assert "structured_evidence_context cannot be empty" in str(error)
