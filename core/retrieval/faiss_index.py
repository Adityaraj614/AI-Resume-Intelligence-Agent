from pathlib import Path
from typing import Any, Dict, List, Optional

import faiss
import numpy as np


def create_faiss_index(embedding_dim: int):
    """
    Create a FAISS inner-product index for normalized embeddings.

    The project stores normalized MiniLM vectors. For normalized vectors,
    inner product is equivalent to cosine similarity, so ``IndexFlatIP`` is a
    simple and correct baseline for semantic retrieval.
    """

    if not isinstance(embedding_dim, int):
        raise TypeError("embedding_dim must be an integer.")

    if embedding_dim <= 0:
        raise ValueError("embedding_dim must be greater than 0.")

    return faiss.IndexFlatIP(embedding_dim)


def _extract_embedding(record: Dict[str, Any], index: int) -> np.ndarray:
    if not isinstance(record, dict):
        raise TypeError(f"Embedding record at index {index} must be a dict.")

    if "embedding" not in record:
        raise ValueError(f"Embedding record at index {index} is missing embedding.")

    embedding = np.asarray(record["embedding"], dtype=np.float32)

    if embedding.ndim != 1:
        raise ValueError(
            f"Embedding at index {index} must be a 1D vector."
        )

    return embedding


def _build_metadata_record(record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Preserve all non-vector metadata outside FAISS.

    FAISS stores only numeric vectors. Candidate ids, sections, chunk text, and
    other explainability fields must stay in a parallel metadata store.
    """

    return {
        key: value
        for key, value in record.items()
        if key != "embedding"
    }


def _stack_embeddings(embedding_records: List[Dict[str, Any]],
                      expected_dim: int) -> np.ndarray:
    if not embedding_records:
        return np.empty((0, expected_dim), dtype=np.float32)

    embeddings = [
        _extract_embedding(record, index)
        for index, record in enumerate(embedding_records)
    ]

    for index, embedding in enumerate(embeddings):
        if embedding.shape[0] != expected_dim:
            raise ValueError(
                f"Embedding at index {index} has dimension {embedding.shape[0]}, "
                f"expected {expected_dim}."
            )

    return np.vstack(embeddings).astype(np.float32)


def add_embeddings_to_index(faiss_index,
                            embedding_records: List[Dict[str, Any]],
                            metadata_store: Optional[List[Dict[str, Any]]] = None):
    """
    Add embedding records to a FAISS index and preserve external metadata.

    Returns a dictionary so later phases can pass both the index and metadata
    store together without hiding the fact that metadata is separate from FAISS.
    """

    if faiss_index is None:
        raise ValueError("faiss_index cannot be None.")

    if not isinstance(embedding_records, list):
        raise TypeError("embedding_records must be a list of dictionaries.")

    if metadata_store is None:
        metadata_store = []

    if not isinstance(metadata_store, list):
        raise TypeError("metadata_store must be a list.")

    embedding_dim = faiss_index.d
    embedding_matrix = _stack_embeddings(
        embedding_records=embedding_records,
        expected_dim=embedding_dim
    )

    if len(embedding_matrix):
        faiss_index.add(embedding_matrix)

    metadata_store.extend(
        _build_metadata_record(record)
        for record in embedding_records
    )

    if faiss_index.ntotal != len(metadata_store):
        raise RuntimeError(
            "FAISS vector count and metadata count are out of sync."
        )

    return {
        "index": faiss_index,
        "metadata_store": metadata_store,
    }


def _prepare_query_embedding(query_embedding: np.ndarray,
                             expected_dim: int) -> np.ndarray:
    query = np.asarray(query_embedding, dtype=np.float32)

    if query.ndim == 1:
        query = query.reshape(1, -1)

    if query.ndim != 2 or query.shape[0] != 1:
        raise ValueError("query_embedding must be a 1D vector or one-row matrix.")

    if query.shape[1] != expected_dim:
        raise ValueError(
            f"Query embedding has dimension {query.shape[1]}, "
            f"expected {expected_dim}."
        )

    return query.astype(np.float32)


def search_index(faiss_index,
                 query_embedding: np.ndarray,
                 metadata_store: List[Dict[str, Any]],
                 top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Search the FAISS index and return ranked metadata-rich results.
    """

    if faiss_index is None:
        raise ValueError("faiss_index cannot be None.")

    if not isinstance(metadata_store, list):
        raise TypeError("metadata_store must be a list.")

    if faiss_index.ntotal != len(metadata_store):
        raise ValueError(
            "FAISS vector count and metadata count must match before search."
        )

    if not isinstance(top_k, int) or top_k <= 0:
        raise ValueError("top_k must be a positive integer.")

    if faiss_index.ntotal == 0:
        return []

    query = _prepare_query_embedding(
        query_embedding=query_embedding,
        expected_dim=faiss_index.d
    )
    search_k = min(top_k, faiss_index.ntotal)
    scores, indices = faiss_index.search(query, search_k)
    results = []

    for score, metadata_index in zip(scores[0], indices[0]):
        if metadata_index < 0:
            continue

        metadata = metadata_store[int(metadata_index)]
        results.append({
            "score": float(score),
            **metadata,
        })

    return results


def save_faiss_index(faiss_index, file_path: str) -> None:
    """
    Persist a FAISS index to disk.
    """

    if faiss_index is None:
        raise ValueError("faiss_index cannot be None.")

    path = Path(file_path)

    if path.parent:
        path.parent.mkdir(parents=True, exist_ok=True)

    faiss.write_index(faiss_index, str(path))


def load_faiss_index(file_path: str):
    """
    Load a persisted FAISS index from disk.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"FAISS index file not found: {file_path}")

    return faiss.read_index(str(path))
