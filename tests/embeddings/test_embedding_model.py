import os

import numpy as np
import pytest

import core.embeddings.embedding_model as embedding_model_module
from core.embeddings.embedder import generate_embeddings
from core.embeddings.embedding_model import get_embedding_model


def _reset_embedding_model_singleton(monkeypatch):
    monkeypatch.setattr(embedding_model_module, "_embedding_model", None)
    monkeypatch.setattr(embedding_model_module, "_embedding_model_load_error", None)


def test_fake_embedding_fallback_is_deterministic(monkeypatch):
    monkeypatch.setenv("DISABLE_TRANSFORMER_MODEL", "1")
    _reset_embedding_model_singleton(monkeypatch)

    first = generate_embeddings(["offline test text"], batch_size=1)
    second = generate_embeddings(["offline test text"], batch_size=1)

    assert first.shape == (1, 384)
    assert second.shape == (1, 384)
    assert first.dtype == np.float32
    assert second.dtype == np.float32
    assert np.allclose(first, second)


def test_fake_embedding_model_uses_singleton(monkeypatch):
    monkeypatch.setenv("DISABLE_TRANSFORMER_MODEL", "1")
    _reset_embedding_model_singleton(monkeypatch)

    first_model = get_embedding_model()
    second_model = get_embedding_model()

    assert first_model is second_model


def test_real_embedding_model_path_when_available(monkeypatch):
    """
    Optional developer check for the real SentenceTransformer path.

    Enable with RUN_REAL_EMBEDDING_MODEL_TEST=1 when the model is cached locally
    or the machine can reach Hugging Face.
    """

    if os.getenv("RUN_REAL_EMBEDDING_MODEL_TEST") != "1":
        pytest.skip("Set RUN_REAL_EMBEDDING_MODEL_TEST=1 to test the real model path.")

    monkeypatch.delenv("DISABLE_TRANSFORMER_MODEL", raising=False)
    _reset_embedding_model_singleton(monkeypatch)

    model = get_embedding_model()
    embeddings = model.encode(
        ["real embedding model smoke test"],
        batch_size=1,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False,
    )

    embeddings = np.asarray(embeddings, dtype=np.float32)

    assert embeddings.shape == (1, 384)
    assert embeddings.dtype == np.float32
