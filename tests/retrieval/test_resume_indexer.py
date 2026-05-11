import json
from pathlib import Path

import numpy as np

from core.retrieval.faiss_index import search_index
from core.retrieval.resume_indexer import (
    RESUME_INDEX_FILE_NAME,
    RESUME_METADATA_FILE_NAME,
    build_resume_faiss_index,
    index_resume_embeddings,
    load_resume_index_bundle,
    save_resume_index_bundle,
)


def _normalize(vector):
    vector = np.asarray(vector, dtype=np.float32)
    norm = np.linalg.norm(vector)

    if norm == 0:
        return vector

    return vector / norm


def _synthetic_resume_records():
    return [
        {
            "candidate_id": "resume_001",
            "candidate_name": "Asha Rao",
            "file_name": "asha_resume.pdf",
            "section": "projects",
            "chunk_index": 0,
            "chunk_text": "Built a transformer NLP resume parser.",
            "embedding": _normalize([1.0, 0.0, 0.0, 0.0]),
        },
        {
            "candidate_id": "resume_002",
            "candidate_name": "Ben Lee",
            "file_name": "ben_resume.pdf",
            "section": "skills",
            "chunk_index": 0,
            "chunk_text": "Python PyTorch FAISS semantic search.",
            "embedding": _normalize([0.0, 1.0, 0.0, 0.0]),
        },
    ]


def _test_output_dir(name):
    output_dir = Path("data") / "test_resume_indexer" / name
    output_dir.mkdir(parents=True, exist_ok=True)

    return output_dir


def test_build_resume_faiss_index_creates_metadata_synced_bundle():
    records = _synthetic_resume_records()

    index_bundle = build_resume_faiss_index(records)

    assert index_bundle["index"].d == 4
    assert index_bundle["index"].ntotal == len(records)
    assert len(index_bundle["metadata_store"]) == len(records)
    assert index_bundle["metadata_store"][0]["candidate_id"] == "resume_001"
    assert index_bundle["metadata_store"][0]["section"] == "projects"
    assert index_bundle["metadata_store"][0]["chunk_text"] == records[0]["chunk_text"]
    assert "embedding" not in index_bundle["metadata_store"][0]


def test_index_resume_embeddings_supports_incremental_indexing():
    initial_records = _synthetic_resume_records()
    index_bundle = index_resume_embeddings(initial_records)

    new_records = [
        {
            "candidate_id": "resume_003",
            "candidate_name": "Cara Smith",
            "file_name": "cara_resume.pdf",
            "section": "experience",
            "chunk_index": 0,
            "chunk_text": "Deployed FastAPI machine learning services.",
            "embedding": _normalize([0.0, 0.0, 1.0, 0.0]).astype(np.float64),
        }
    ]

    updated_bundle = index_resume_embeddings(
        embedded_resume_records=new_records,
        existing_index_bundle=index_bundle,
    )

    assert updated_bundle["index"] is index_bundle["index"]
    assert updated_bundle["metadata_store"] is index_bundle["metadata_store"]
    assert updated_bundle["index"].ntotal == 3
    assert len(updated_bundle["metadata_store"]) == 3
    assert updated_bundle["metadata_store"][-1]["candidate_id"] == "resume_003"
    assert updated_bundle["index"].ntotal == len(updated_bundle["metadata_store"])


def test_save_resume_index_bundle_persists_metadata_separately():
    index_bundle = build_resume_faiss_index(_synthetic_resume_records())
    output_dir = _test_output_dir("save")

    saved_paths = save_resume_index_bundle(
        index_bundle=index_bundle,
        output_dir=str(output_dir),
    )

    assert saved_paths["index_path"].endswith(RESUME_INDEX_FILE_NAME)
    assert saved_paths["metadata_path"].endswith(RESUME_METADATA_FILE_NAME)
    assert (output_dir / RESUME_INDEX_FILE_NAME).exists()
    assert (output_dir / RESUME_METADATA_FILE_NAME).exists()

    with (output_dir / RESUME_METADATA_FILE_NAME).open("r", encoding="utf-8") as file:
        metadata = json.load(file)

    assert len(metadata) == 2
    assert metadata[1]["candidate_id"] == "resume_002"
    assert "embedding" not in metadata[1]


def test_load_resume_index_bundle_keeps_retrieval_working():
    index_bundle = build_resume_faiss_index(_synthetic_resume_records())
    output_dir = _test_output_dir("load")

    save_resume_index_bundle(
        index_bundle=index_bundle,
        output_dir=str(output_dir),
    )

    loaded_bundle = load_resume_index_bundle(str(output_dir))

    assert loaded_bundle["index"].ntotal == index_bundle["index"].ntotal
    assert loaded_bundle["index"].d == index_bundle["index"].d
    assert len(loaded_bundle["metadata_store"]) == loaded_bundle["index"].ntotal

    results = search_index(
        faiss_index=loaded_bundle["index"],
        query_embedding=_normalize([0.0, 1.0, 0.0, 0.0]),
        metadata_store=loaded_bundle["metadata_store"],
        top_k=1,
    )

    assert len(results) == 1
    assert results[0]["candidate_id"] == "resume_002"
    assert results[0]["section"] == "skills"
