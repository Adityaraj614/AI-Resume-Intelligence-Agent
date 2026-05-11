import numpy as np
import pytest

from core.retrieval.resume_indexer import build_resume_faiss_index
from core.retrieval.retriever import (
    aggregate_candidate_scores,
    retrieve_resume_matches,
)


def _normalize(vector):
    vector = np.asarray(vector, dtype=np.float32)
    norm = np.linalg.norm(vector)

    if norm == 0:
        return vector

    return vector / norm


def _match(candidate_id, score, jd_index, jd_section, resume_section, chunk_text):
    section_weights = {
        "projects": 1.5,
        "experience": 1.5,
        "skills": 1.2,
        "education": 0.8,
    }
    section_weight = section_weights.get(resume_section, 1.0)

    return {
        "candidate_id": candidate_id,
        "score": float(score),
        "weighted_score": float(score * section_weight),
        "section_weight": section_weight,
        "jd_section": jd_section,
        "jd_chunk_index": jd_index,
        "jd_chunk_text": f"JD chunk {jd_index}",
        "jd_total_chunks": 3,
        "section": resume_section,
        "chunk_text": chunk_text,
    }


def test_low_score_candidate_elimination_happens_after_aggregation():
    retrieval_results = [
        _match("resume_001", 0.80, 0, "requirements", "skills", "PyTorch skills"),
        _match("resume_002", 0.20, 0, "requirements", "skills", "Weak match"),
    ]

    candidate_scores = aggregate_candidate_scores(
        retrieval_results,
        aggregation_method="average",
        minimum_candidate_score=0.50,
        use_section_weights=False,
    )

    assert len(candidate_scores) == 1
    assert candidate_scores[0]["candidate_id"] == "resume_001"
    assert "eliminated_reason" not in candidate_scores[0]


def test_jd_coverage_filtering_removes_narrow_matches():
    retrieval_results = [
        _match("resume_001", 0.80, 0, "requirements", "skills", "PyTorch"),
        _match("resume_001", 0.82, 1, "responsibilities", "projects", "Parser project"),
        _match("resume_002", 0.95, 0, "requirements", "experience", "Only one strong area"),
    ]

    candidate_scores = aggregate_candidate_scores(
        retrieval_results,
        aggregation_method="average",
        minimum_jd_coverage=0.50,
        coverage_similarity_threshold=0.45,
        use_section_weights=False,
        total_jd_chunks=3,
    )

    assert len(candidate_scores) == 1
    assert candidate_scores[0]["candidate_id"] == "resume_001"
    assert candidate_scores[0]["jd_match_coverage"] == 2 / 3


def test_section_weighting_improves_project_and_experience_ranking():
    retrieval_results = [
        _match("resume_001", 0.70, 0, "requirements", "projects", "Production ML project"),
        _match("resume_002", 0.80, 0, "requirements", "education", "Coursework"),
    ]

    weighted_scores = aggregate_candidate_scores(
        retrieval_results,
        aggregation_method="weighted_average",
        use_section_weights=True,
    )

    unweighted_scores = aggregate_candidate_scores(
        retrieval_results,
        aggregation_method="average",
        use_section_weights=False,
    )

    assert weighted_scores[0]["candidate_id"] == "resume_001"
    assert unweighted_scores[0]["candidate_id"] == "resume_002"
    assert weighted_scores[0]["top_match"]["score"] == 0.70
    assert weighted_scores[0]["top_match"]["weighted_score"] == pytest.approx(1.05)


def test_duplicate_chunk_suppression_prevents_score_inflation():
    retrieval_results = [
        _match("resume_001", 0.90, 0, "requirements", "skills", "PyTorch NLP"),
        _match("resume_001", 0.88, 1, "requirements", "skills", "PyTorch NLP"),
        _match("resume_001", 0.86, 2, "responsibilities", "projects", "Transformer parser"),
    ]

    candidate_scores = aggregate_candidate_scores(
        retrieval_results,
        aggregation_method="average",
        suppress_exact_duplicates=True,
        use_section_weights=False,
        top_n=3,
    )

    assert candidate_scores[0]["match_count"] == 2
    assert [
        match["chunk_text"]
        for match in candidate_scores[0]["matches"]
    ] == ["PyTorch NLP", "Transformer parser"]


def test_retrieval_threshold_filters_weak_faiss_matches():
    resume_records = [
        {
            "candidate_id": "resume_001",
            "section": "skills",
            "chunk_text": "Relevant PyTorch work",
            "embedding": _normalize([1.0, 0.0, 0.0]),
        },
        {
            "candidate_id": "resume_002",
            "section": "hobbies",
            "chunk_text": "Unrelated profile",
            "embedding": _normalize([0.0, 1.0, 0.0]),
        },
    ]
    jd_records = [
        {
            "section": "requirements",
            "chunk_index": 0,
            "chunk_text": "PyTorch experience",
            "embedding": _normalize([1.0, 0.0, 0.0]),
        }
    ]
    index_bundle = build_resume_faiss_index(resume_records)

    results = retrieve_resume_matches(
        jd_embedding_records=jd_records,
        resume_index_bundle=index_bundle,
        top_k=2,
        minimum_similarity_score=0.45,
    )

    assert len(results) == 1
    assert results[0]["candidate_id"] == "resume_001"
    assert results[0]["score"] >= 0.45


def test_required_jd_section_enforcement_eliminates_missing_requirement_match():
    retrieval_results = [
        _match("resume_001", 0.80, 0, "requirements", "skills", "PyTorch"),
        _match("resume_002", 0.95, 1, "responsibilities", "projects", "Built APIs"),
    ]

    candidate_scores = aggregate_candidate_scores(
        retrieval_results,
        aggregation_method="average",
        required_jd_sections=["requirements"],
        use_section_weights=False,
    )

    assert len(candidate_scores) == 1
    assert candidate_scores[0]["candidate_id"] == "resume_001"


def test_hybrid_max_average_produces_stable_candidate_ranking():
    retrieval_results = [
        _match("resume_001", 0.90, 0, "requirements", "skills", "PyTorch"),
        _match("resume_001", 0.82, 1, "responsibilities", "projects", "Parser"),
        _match("resume_002", 0.96, 0, "requirements", "skills", "PyTorch only"),
        _match("resume_002", 0.30, 1, "responsibilities", "education", "Course"),
    ]

    candidate_scores = aggregate_candidate_scores(
        retrieval_results,
        aggregation_method="hybrid_max_average",
        use_section_weights=False,
        top_n=2,
    )

    assert candidate_scores[0]["candidate_id"] == "resume_001"
    assert candidate_scores[0]["aggregate_score"] > candidate_scores[1]["aggregate_score"]
    assert candidate_scores[0]["matched_sections"] == ["projects", "skills"]
