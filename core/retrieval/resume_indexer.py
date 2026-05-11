import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

from core.retrieval.faiss_index import (
    add_embeddings_to_index,
    create_faiss_index,
    load_faiss_index,
    save_faiss_index,
)


RESUME_INDEX_FILE_NAME = "resume_index.faiss"
RESUME_METADATA_FILE_NAME = "resume_metadata.json"


def _validate_index_bundle(index_bundle: Dict[str, Any]) -> None:
    if not isinstance(index_bundle, dict):
        raise TypeError("index_bundle must be a dictionary.")

    if "index" not in index_bundle:
        raise ValueError("index_bundle is missing index.")

    if "metadata_store" not in index_bundle:
        raise ValueError("index_bundle is missing metadata_store.")

    metadata_store = index_bundle["metadata_store"]

    if not isinstance(metadata_store, list):
        raise TypeError("metadata_store must be a list.")

    faiss_index = index_bundle["index"]

    if faiss_index.ntotal != len(metadata_store):
        raise ValueError(
            "FAISS vector count and metadata count are out of sync."
        )


def _prepare_embedding_record(record: Dict[str, Any],
                              record_index: int,
                              expected_dim: Optional[int] = None) -> Dict[str, Any]:
    """
    Validate and normalize one embedded resume record before FAISS ingestion.
    """

    if not isinstance(record, dict):
        raise TypeError(
            f"Embedded resume record at index {record_index} must be a dictionary."
        )

    if "embedding" not in record:
        raise ValueError(
            f"Embedded resume record at index {record_index} is missing embedding."
        )

    embedding = np.asarray(record["embedding"], dtype=np.float32)

    if embedding.ndim != 1:
        raise ValueError(
            f"Embedding at index {record_index} must be a 1D vector."
        )

    if embedding.shape[0] == 0:
        raise ValueError(
            f"Embedding at index {record_index} cannot be empty."
        )

    if expected_dim is not None and embedding.shape[0] != expected_dim:
        raise ValueError(
            f"Embedding at index {record_index} has dimension {embedding.shape[0]}, "
            f"expected {expected_dim}."
        )

    return {
        **record,
        "embedding": embedding.astype(np.float32, copy=False),
    }


def _prepare_embedding_records(
    embedded_resume_records: List[Dict[str, Any]],
    expected_dim: Optional[int] = None
) -> List[Dict[str, Any]]:
    if embedded_resume_records is None:
        raise ValueError("embedded_resume_records cannot be None.")

    if not isinstance(embedded_resume_records, list):
        raise TypeError(
            "embedded_resume_records must be a list of dictionaries."
        )

    prepared_records = []
    inferred_dim = expected_dim

    for record_index, record in enumerate(embedded_resume_records):
        prepared_record = _prepare_embedding_record(
            record=record,
            record_index=record_index,
            expected_dim=inferred_dim,
        )

        if inferred_dim is None:
            inferred_dim = prepared_record["embedding"].shape[0]

        prepared_records.append(prepared_record)

    return prepared_records


def _infer_embedding_dim(embedded_resume_records: List[Dict[str, Any]]) -> int:
    if not embedded_resume_records:
        raise ValueError(
            "At least one embedded resume record is required to infer dimension."
        )

    first_record = _prepare_embedding_record(
        record=embedded_resume_records[0],
        record_index=0,
    )

    return int(first_record["embedding"].shape[0])


def _json_safe(value: Any) -> Any:
    """
    Convert common NumPy values in metadata into JSON-serializable objects.
    """

    if isinstance(value, dict):
        return {
            str(key): _json_safe(nested_value)
            for key, nested_value in value.items()
        }

    if isinstance(value, list):
        return [_json_safe(item) for item in value]

    if isinstance(value, tuple):
        return [_json_safe(item) for item in value]

    if isinstance(value, np.ndarray):
        return value.tolist()

    if isinstance(value, np.generic):
        return value.item()

    return value


def build_resume_faiss_index(
    embedded_resume_records: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Build a new FAISS semantic database from embedded resume records.

    FAISS stores vectors only. The returned bundle keeps the FAISS index beside
    a metadata store whose list positions match FAISS vector ids.
    """

    embedding_dim = _infer_embedding_dim(embedded_resume_records)
    prepared_records = _prepare_embedding_records(
        embedded_resume_records=embedded_resume_records,
        expected_dim=embedding_dim,
    )

    faiss_index = create_faiss_index(embedding_dim)

    return add_embeddings_to_index(
        faiss_index=faiss_index,
        embedding_records=prepared_records,
    )


def index_resume_embeddings(
    embedded_resume_records: List[Dict[str, Any]],
    existing_index_bundle: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Add embedded resume records to a new or existing FAISS index bundle.

    This is the main scalable entry point for resume indexing. Passing an
    existing bundle appends new vectors and metadata without rebuilding the
    whole database.
    """

    if existing_index_bundle is None:
        return build_resume_faiss_index(embedded_resume_records)

    _validate_index_bundle(existing_index_bundle)

    if embedded_resume_records is None:
        raise ValueError("embedded_resume_records cannot be None.")

    if not isinstance(embedded_resume_records, list):
        raise TypeError(
            "embedded_resume_records must be a list of dictionaries."
        )

    if not embedded_resume_records:
        return existing_index_bundle

    faiss_index = existing_index_bundle["index"]
    metadata_store = existing_index_bundle["metadata_store"]
    prepared_records = _prepare_embedding_records(
        embedded_resume_records=embedded_resume_records,
        expected_dim=faiss_index.d,
    )

    return add_embeddings_to_index(
        faiss_index=faiss_index,
        embedding_records=prepared_records,
        metadata_store=metadata_store,
    )


def save_resume_index_bundle(index_bundle: Dict[str, Any],
                             output_dir: str) -> Dict[str, str]:
    """
    Save a resume FAISS index and its metadata store into one directory.
    """

    _validate_index_bundle(index_bundle)

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    index_path = output_path / RESUME_INDEX_FILE_NAME
    metadata_path = output_path / RESUME_METADATA_FILE_NAME

    save_faiss_index(
        faiss_index=index_bundle["index"],
        file_path=str(index_path),
    )

    metadata = _json_safe(index_bundle["metadata_store"])

    with metadata_path.open("w", encoding="utf-8") as metadata_file:
        json.dump(metadata, metadata_file, indent=2, ensure_ascii=False)

    return {
        "index_path": str(index_path),
        "metadata_path": str(metadata_path),
    }


def load_resume_index_bundle(input_dir: str) -> Dict[str, Any]:
    """
    Load a persisted resume FAISS index bundle from disk.
    """

    input_path = Path(input_dir)
    index_path = input_path / RESUME_INDEX_FILE_NAME
    metadata_path = input_path / RESUME_METADATA_FILE_NAME

    if not metadata_path.exists():
        raise FileNotFoundError(
            f"Resume metadata file not found: {metadata_path}"
        )

    faiss_index = load_faiss_index(str(index_path))

    with metadata_path.open("r", encoding="utf-8") as metadata_file:
        metadata_store = json.load(metadata_file)

    if not isinstance(metadata_store, list):
        raise ValueError("Loaded resume metadata must be a list.")

    index_bundle = {
        "index": faiss_index,
        "metadata_store": metadata_store,
    }

    _validate_index_bundle(index_bundle)

    return index_bundle
