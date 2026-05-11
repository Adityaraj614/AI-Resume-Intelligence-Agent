from typing import Any, Dict, List, Optional

import numpy as np


REQUIRED_CHUNK_FIELDS = (
    "candidate_id",
    "section",
    "chunk_text",
)


def validate_chunk_record(chunk: Dict[str, Any], index: int) -> None:
    """
    Validate one resume chunk before embedding.

    The embedding pipeline is intentionally strict about required fields because
    FAISS indexing later will depend on stable metadata for filtering,
    attribution, and explainable candidate scoring.
    """

    if not isinstance(chunk, dict):
        raise TypeError(f"Chunk at index {index} must be a dictionary.")

    missing_fields = [
        field
        for field in REQUIRED_CHUNK_FIELDS
        if field not in chunk
    ]

    if missing_fields:
        raise ValueError(
            f"Chunk at index {index} is missing required fields: "
            f"{', '.join(missing_fields)}"
        )

    if not isinstance(chunk["chunk_text"], str):
        raise TypeError(
            f"chunk_text at index {index} must be a string."
        )

    if not chunk["chunk_text"].strip():
        raise ValueError(
            f"chunk_text at index {index} cannot be empty."
        )


def embed_resume_chunks(chunk_records: List[Dict[str, Any]],
                        batch_size: int = 32) -> List[Dict[str, Any]]:
    """
    Generate retrieval-ready embedding records for resume chunks.

    Input records are preserved in order. All existing metadata fields are
    copied into the output record, and a normalized NumPy embedding is added
    under the ``embedding`` key.
    """

    if chunk_records is None:
        raise ValueError("chunk_records cannot be None.")

    if not isinstance(chunk_records, list):
        raise TypeError("chunk_records must be a list of dictionaries.")

    if not chunk_records:
        return []

    for index, chunk in enumerate(chunk_records):
        validate_chunk_record(chunk, index)

    chunk_texts = [
        chunk["chunk_text"].strip()
        for chunk in chunk_records
    ]

    # Import lazily so metadata-only helpers in this module remain usable even
    # before the Sentence Transformers runtime is loaded.
    from core.embeddings.embedder import generate_embeddings

    embeddings = generate_embeddings(
        texts=chunk_texts,
        batch_size=batch_size
    )

    if len(embeddings) != len(chunk_records):
        raise RuntimeError(
            "Embedding count does not match chunk record count."
        )

    embedded_records = []

    for chunk, embedding in zip(chunk_records, embeddings):
        embedded_record = {
            **chunk,
            "chunk_text": chunk["chunk_text"].strip(),
            "embedding": np.asarray(embedding, dtype=np.float32),
        }

        embedded_records.append(embedded_record)

    return embedded_records


def build_chunk_records_from_resume_data(
    resume_data: Dict[str, Any],
    candidate_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Convert the existing structured resume object into chunk records.

    This helper keeps Phase 3B compatible with the current parser output while
    avoiding any redesign of the preprocessing pipeline.
    """

    if not isinstance(resume_data, dict):
        raise TypeError("resume_data must be a dictionary.")

    section_chunks = resume_data.get("section_chunks", {})

    if not isinstance(section_chunks, dict):
        raise TypeError("resume_data['section_chunks'] must be a dictionary.")

    resolved_candidate_id = (
        candidate_id
        or resume_data.get("candidate_id")
        or resume_data.get("file_name")
        or resume_data.get("candidate_name")
        or "unknown_candidate"
    )

    chunk_records = []

    for section_name, chunks in section_chunks.items():
        if not isinstance(chunks, list):
            continue

        for chunk_index, chunk_text in enumerate(chunks):
            if not isinstance(chunk_text, str) or not chunk_text.strip():
                continue

            chunk_records.append({
                "candidate_id": resolved_candidate_id,
                "candidate_name": resume_data.get("candidate_name", ""),
                "file_name": resume_data.get("file_name", ""),
                "section": section_name,
                "chunk_index": chunk_index,
                "chunk_text": chunk_text.strip(),
            })

    return chunk_records
