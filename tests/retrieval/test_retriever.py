import numpy as np

from core.retrieval.resume_indexer import build_resume_faiss_index
from core.retrieval.retriever import (
    aggregate_candidate_scores,
    group_results_by_candidate,
    retrieve_resume_matches,
    retrieve_top_chunks,
)


def _normalize(vector):
    vector = np.asarray(vector, dtype=np.float32)
    norm = np.linalg.norm(vector)

    if norm == 0:
        return vector

    return vector / norm


def _resume_records():
    return [
        {
            "candidate_id": "resume_001",
            "candidate_name": "Asha Rao",
            "section": "skills",
            "chunk_index": 0,
            "chunk_text": "PyTorch model development and NLP pipelines.",
            "embedding": _normalize([1.0, 0.0, 0.0, 0.0]),
        },
        {
            "candidate_id": "resume_001",
            "candidate_name": "Asha Rao",
            "section": "projects",
            "chunk_index": 1,
            "chunk_text": "Built semantic resume parsing with transformers.",
            "embedding": _normalize([0.9, 0.1, 0.0, 0.0]),
        },
        {
            "candidate_id": "resume_002",
            "candidate_name": "Ben Lee",
            "section": "experience",
            "chunk_index": 0,
            "chunk_text": "Created dashboard reports and analytics workflows.",
            "embedding": _normalize([0.0, 1.0, 0.0, 0.0]),
        },
    ]


def _jd_records():
    return [
        {
            "section": "requirements",
            "chunk_index": 0,
            "chunk_text": "Experience with PyTorch and NLP.",
            "embedding": _normalize([1.0, 0.0, 0.0, 0.0]),
        },
        {
            "section": "responsibilities",
            "chunk_index": 1,
            "chunk_text": "Build transformer based parsing pipelines.",
            "embedding": _normalize([0.8, 0.2, 0.0, 0.0]),
        },
    ]


def test_retrieve_resume_matches_returns_explainable_chunk_results():
    resume_index_bundle = build_resume_faiss_index(_resume_records())

    results = retrieve_resume_matches(
        jd_embedding_records=_jd_records(),
        resume_index_bundle=resume_index_bundle,
        top_k=2,
    )

    assert len(results) == 4
    assert results[0]["candidate_id"] == "resume_001"
    assert results[0]["section"] == "skills"
    assert results[0]["jd_section"] == "requirements"
    assert results[0]["jd_chunk_text"] == "Experience with PyTorch and NLP."
    assert results[0]["chunk_text"] == "PyTorch model development and NLP pipelines."
    assert "score" in results[0]
    assert isinstance(results[0]["score"], float)


def test_retrieve_top_chunks_sorts_globally_by_score():
    resume_index_bundle = build_resume_faiss_index(_resume_records())
    results = retrieve_resume_matches(
        jd_embedding_records=_jd_records(),
        resume_index_bundle=resume_index_bundle,
        top_k=2,
    )

    top_chunks = retrieve_top_chunks(results, top_k=2)

    assert len(top_chunks) == 2
    assert top_chunks[0]["score"] >= top_chunks[1]["score"]
    assert top_chunks[0]["candidate_id"] == "resume_001"
    assert top_chunks[0]["section"] == "skills"


def test_group_results_by_candidate_preserves_candidate_matches():
    resume_index_bundle = build_resume_faiss_index(_resume_records())
    results = retrieve_resume_matches(
        jd_embedding_records=_jd_records(),
        resume_index_bundle=resume_index_bundle,
        top_k=3,
    )

    grouped_results = group_results_by_candidate(results)

    assert set(grouped_results.keys()) == {"resume_001", "resume_002"}
    assert len(grouped_results["resume_001"]) == 4
    assert len(grouped_results["resume_002"]) == 2
    assert grouped_results["resume_001"][0]["jd_chunk_text"]
    assert grouped_results["resume_001"][0]["chunk_text"]


def test_aggregate_candidate_scores_selects_top_candidate():
    resume_index_bundle = build_resume_faiss_index(_resume_records())
    results = retrieve_resume_matches(
        jd_embedding_records=_jd_records(),
        resume_index_bundle=resume_index_bundle,
        top_k=3,
    )

    candidate_scores = aggregate_candidate_scores(
        retrieval_results=results,
        aggregation_method="average",
        top_n=2,
    )

    assert len(candidate_scores) == 2
    assert candidate_scores[0]["candidate_id"] == "resume_001"
    assert candidate_scores[0]["aggregate_score"] >= candidate_scores[1]["aggregate_score"]
    assert candidate_scores[0]["match_count"] == 4
    assert candidate_scores[0]["top_match"]["candidate_id"] == "resume_001"
    assert "jd_chunk_text" in candidate_scores[0]["top_match"]
    assert "chunk_text" in candidate_scores[0]["top_match"]


def test_aggregate_candidate_scores_supports_max_and_weighted_methods():
    resume_index_bundle = build_resume_faiss_index(_resume_records())
    results = retrieve_resume_matches(
        jd_embedding_records=_jd_records(),
        resume_index_bundle=resume_index_bundle,
        top_k=3,
    )

    max_scores = aggregate_candidate_scores(
        retrieval_results=results,
        aggregation_method="max",
        top_n=3,
    )
    weighted_scores = aggregate_candidate_scores(
        retrieval_results=results,
        aggregation_method="weighted",
        top_n=3,
    )

    assert max_scores[0]["candidate_id"] == "resume_001"
    assert weighted_scores[0]["candidate_id"] == "resume_001"
    assert max_scores[0]["aggregate_score"] >= weighted_scores[0]["aggregate_score"]
