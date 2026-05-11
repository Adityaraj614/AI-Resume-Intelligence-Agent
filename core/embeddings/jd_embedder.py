from typing import Any, Dict, List, Union

import numpy as np


REQUIRED_JD_CHUNK_FIELDS = (
    "section",
    "chunk_text",
)


def validate_jd_chunk_record(chunk: Dict[str, Any], index: int) -> None:
    """
    Validate one Job Description chunk before embedding.

    JD embeddings will later be compared against resume chunk embeddings in
    FAISS, so each record must keep stable section metadata and non-empty text.
    """

    if not isinstance(chunk, dict):
        raise TypeError(f"JD chunk at index {index} must be a dictionary.")

    missing_fields = [
        field
        for field in REQUIRED_JD_CHUNK_FIELDS
        if field not in chunk
    ]

    if missing_fields:
        raise ValueError(
            f"JD chunk at index {index} is missing required fields: "
            f"{', '.join(missing_fields)}"
        )

    if not isinstance(chunk["section"], str) or not chunk["section"].strip():
        raise ValueError(
            f"section at index {index} must be a non-empty string."
        )

    if not isinstance(chunk["chunk_text"], str):
        raise TypeError(
            f"chunk_text at index {index} must be a string."
        )

    if not chunk["chunk_text"].strip():
        raise ValueError(
            f"chunk_text at index {index} cannot be empty."
        )


def _normalize_section_name(section: str) -> str:
    """
    Normalize JD section labels for stable downstream filtering.
    """

    return " ".join(section.strip().lower().split()).replace(" ", "_")


def _split_raw_jd_text(raw_jd_text: str) -> List[str]:
    """
    Split raw JD text into simple line-based chunks.

    This keeps Phase 3C focused on embeddings, not JD parsing. More advanced JD
    section extraction can be added later without changing the embedding record
    format.
    """

    return [
        line.strip(" \t-*•")
        for line in raw_jd_text.splitlines()
        if line.strip(" \t-*•")
    ]


def build_jd_chunk_records(
    jd_input: Union[str, List[Dict[str, Any]]],
    default_section: str = "job_description"
) -> List[Dict[str, Any]]:
    """
    Build normalized JD chunk records from raw text or structured chunk data.

    Accepted inputs:
    - raw JD text as a string
    - list of dictionaries containing ``section`` and ``chunk_text``
    """

    if isinstance(jd_input, str):
        lines = _split_raw_jd_text(jd_input)

        return [
            {
                "section": _normalize_section_name(default_section),
                "chunk_index": index,
                "chunk_text": line,
            }
            for index, line in enumerate(lines)
        ]

    if not isinstance(jd_input, list):
        raise TypeError(
            "jd_input must be raw text or a list of JD chunk dictionaries."
        )

    chunk_records = []

    for index, chunk in enumerate(jd_input):
        validate_jd_chunk_record(chunk, index)

        normalized_chunk = {
            **chunk,
            "section": _normalize_section_name(chunk["section"]),
            "chunk_index": chunk.get("chunk_index", index),
            "chunk_text": chunk["chunk_text"].strip(),
        }

        chunk_records.append(normalized_chunk)

    return chunk_records


def embed_jd_chunks(chunk_records: List[Dict[str, Any]],
                    batch_size: int = 32) -> List[Dict[str, Any]]:
    """
    Generate retrieval-ready embedding records for JD chunks.

    Ordering and metadata are preserved. Embeddings are explicitly converted to
    ``float32`` because FAISS indexes expect float32 vectors.
    """

    if chunk_records is None:
        raise ValueError("chunk_records cannot be None.")

    if not isinstance(chunk_records, list):
        raise TypeError("chunk_records must be a list of dictionaries.")

    if not chunk_records:
        return []

    for index, chunk in enumerate(chunk_records):
        validate_jd_chunk_record(chunk, index)

    chunk_texts = [
        chunk["chunk_text"].strip()
        for chunk in chunk_records
    ]

    # Import lazily so record-building utilities remain usable without loading
    # the Sentence Transformers model.
    from core.embeddings.embedder import generate_embeddings

    embeddings = generate_embeddings(
        texts=chunk_texts,
        batch_size=batch_size
    )

    if len(embeddings) != len(chunk_records):
        raise RuntimeError(
            "Embedding count does not match JD chunk record count."
        )

    embedded_records = []

    for chunk, embedding in zip(chunk_records, embeddings):
        embedded_records.append({
            **chunk,
            "chunk_text": chunk["chunk_text"].strip(),
            "embedding": np.asarray(embedding, dtype=np.float32),
        })

    return embedded_records


def embed_job_description(
    jd_input: Union[str, List[Dict[str, Any]]],
    batch_size: int = 32,
    default_section: str = "job_description"
) -> List[Dict[str, Any]]:
    """
    Convenience pipeline: build JD records and embed them.
    """

    chunk_records = build_jd_chunk_records(
        jd_input=jd_input,
        default_section=default_section
    )

    return embed_jd_chunks(
        chunk_records=chunk_records,
        batch_size=batch_size
    )
