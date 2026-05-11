import numpy as np

from core.embeddings.resume_embedder import embed_resume_chunks


def test_embed_resume_chunks(monkeypatch):
    """
    Validate Phase 3B resume chunk embedding records.
    """

    monkeypatch.setenv("DISABLE_TRANSFORMER_MODEL", "1")

    fake_chunks = [
        {
            "candidate_id": "resume_001",
            "section": "projects",
            "chunk_text": "Built NLP pipeline using transformers",
        },
        {
            "candidate_id": "resume_001",
            "section": "skills",
            "chunk_text": "Python FastAPI PyTorch FAISS",
        },
    ]

    embedded_records = embed_resume_chunks(
        fake_chunks,
        batch_size=2
    )

    print("\nGenerated embedding records:", len(embedded_records))

    assert len(embedded_records) == len(fake_chunks)

    for index, record in enumerate(embedded_records):
        print(
            "Record",
            index,
            "| candidate:",
            record["candidate_id"],
            "| section:",
            record["section"],
            "| embedding shape:",
            record["embedding"].shape,
            "| dtype:",
            record["embedding"].dtype,
        )

        assert record["candidate_id"] == fake_chunks[index]["candidate_id"]
        assert record["section"] == fake_chunks[index]["section"]
        assert record["chunk_text"] == fake_chunks[index]["chunk_text"]
        assert "embedding" in record
        assert isinstance(record["embedding"], np.ndarray)
        assert record["embedding"].shape == (384,)
        assert record["embedding"].dtype == np.float32
