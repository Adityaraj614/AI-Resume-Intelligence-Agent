import numpy as np
from pathlib import Path

from core.retrieval.faiss_index import (
    add_embeddings_to_index,
    create_faiss_index,
    load_faiss_index,
    save_faiss_index,
    search_index,
)


def _normalize(vector):
    vector = np.asarray(vector, dtype=np.float32)
    norm = np.linalg.norm(vector)

    if norm == 0:
        return vector

    return vector / norm


def test_faiss_index_lifecycle():
    """
    Validate Phase 3D FAISS vector store infrastructure.
    """

    embedding_dim = 4
    faiss_index = create_faiss_index(embedding_dim)

    assert faiss_index.d == embedding_dim
    assert faiss_index.ntotal == 0

    embedding_records = [
        {
            "candidate_id": "resume_001",
            "section": "projects",
            "chunk_index": 0,
            "chunk_text": "Built NLP pipeline using transformers",
            "embedding": _normalize([1.0, 0.0, 0.0, 0.0]),
        },
        {
            "candidate_id": "resume_002",
            "section": "skills",
            "chunk_index": 0,
            "chunk_text": "PyTorch machine learning model training",
            "embedding": _normalize([0.0, 1.0, 0.0, 0.0]),
        },
        {
            "candidate_id": "resume_003",
            "section": "experience",
            "chunk_index": 0,
            "chunk_text": "Built FastAPI services for ML deployment",
            "embedding": _normalize([0.0, 0.0, 1.0, 0.0]),
        },
    ]

    index_bundle = add_embeddings_to_index(
        faiss_index=faiss_index,
        embedding_records=embedding_records,
    )
    metadata_store = index_bundle["metadata_store"]

    print("\nFAISS vector count:", faiss_index.ntotal)
    print("Metadata count:", len(metadata_store))

    assert index_bundle["index"] is faiss_index
    assert faiss_index.ntotal == len(embedding_records)
    assert len(metadata_store) == len(embedding_records)
    assert metadata_store[0]["candidate_id"] == "resume_001"
    assert metadata_store[0]["section"] == "projects"
    assert metadata_store[0]["chunk_text"] == embedding_records[0]["chunk_text"]
    assert "embedding" not in metadata_store[0]

    query_embedding = _normalize([0.0, 1.0, 0.0, 0.0])
    results = search_index(
        faiss_index=faiss_index,
        query_embedding=query_embedding,
        metadata_store=metadata_store,
        top_k=2,
    )

    print("Search results:", results)

    assert len(results) == 2
    assert "score" in results[0]
    assert results[0]["candidate_id"] == "resume_002"
    assert results[0]["section"] == "skills"
    assert results[0]["chunk_text"] == embedding_records[1]["chunk_text"]

    index_path = Path("data/test_resume_chunks.index")

    save_faiss_index(
        faiss_index=faiss_index,
        file_path=str(index_path),
    )

    loaded_index = load_faiss_index(str(index_path))

    assert loaded_index.ntotal == faiss_index.ntotal
    assert loaded_index.d == faiss_index.d

    loaded_results = search_index(
        faiss_index=loaded_index,
        query_embedding=query_embedding,
        metadata_store=metadata_store,
        top_k=1,
    )

    print("Loaded index search result:", loaded_results)

    assert len(loaded_results) == 1
    assert loaded_results[0]["candidate_id"] == "resume_002"
