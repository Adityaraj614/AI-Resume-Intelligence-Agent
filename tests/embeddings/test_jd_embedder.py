import numpy as np

from core.embeddings.jd_embedder import (
    build_jd_chunk_records,
    embed_jd_chunks,
)


def test_build_jd_chunk_records_from_raw_text():
    """
    Validate normalized JD chunk creation from raw job description text.
    """

    raw_jd_text = """
    Looking for ML engineer with experience in:

    * PyTorch
    * NLP
    * Transformers
    * FastAPI
    """

    chunk_records = build_jd_chunk_records(raw_jd_text)

    print("\nRaw JD chunk records:", chunk_records)

    assert len(chunk_records) == 5
    assert chunk_records[0]["section"] == "job_description"
    assert chunk_records[0]["chunk_index"] == 0
    assert chunk_records[1]["chunk_text"] == "PyTorch"


def test_embed_jd_chunks(monkeypatch):
    """
    Validate Phase 3C JD chunk embedding records.
    """

    monkeypatch.setenv("DISABLE_TRANSFORMER_MODEL", "1")

    jd_chunks = [
        {
            "section": "requirements",
            "chunk_text": "Experience with PyTorch and NLP",
            "importance": "high",
        },
        {
            "section": "responsibilities",
            "chunk_text": "Build APIs with FastAPI and deploy ML services",
            "importance": "medium",
        },
    ]

    chunk_records = build_jd_chunk_records(jd_chunks)
    embedded_records = embed_jd_chunks(
        chunk_records,
        batch_size=2
    )

    print("\nGenerated JD embedding records:", len(embedded_records))

    assert len(embedded_records) == len(jd_chunks)

    for index, record in enumerate(embedded_records):
        print(
            "JD Record",
            index,
            "| section:",
            record["section"],
            "| importance:",
            record["importance"],
            "| embedding shape:",
            record["embedding"].shape,
            "| dtype:",
            record["embedding"].dtype,
        )

        assert record["section"] == jd_chunks[index]["section"]
        assert record["chunk_text"] == jd_chunks[index]["chunk_text"]
        assert record["importance"] == jd_chunks[index]["importance"]
        assert record["chunk_index"] == index
        assert "embedding" in record
        assert isinstance(record["embedding"], np.ndarray)
        assert record["embedding"].shape == (384,)
        assert record["embedding"].dtype == np.float32
