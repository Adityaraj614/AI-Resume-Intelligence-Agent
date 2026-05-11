import hashlib
import os

import numpy as np
from sentence_transformers import SentenceTransformer


EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIMENSION = 384
DISABLE_TRANSFORMER_MODEL_ENV = "DISABLE_TRANSFORMER_MODEL"


_embedding_model = None
_embedding_model_load_error = None


class DeterministicFakeEmbeddingModel:
    """
    Small test-only replacement for SentenceTransformer.

    This is enabled only when DISABLE_TRANSFORMER_MODEL=1. It keeps offline
    tests deterministic without changing the production embedding path.
    """

    def encode(
        self,
        texts,
        batch_size=32,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=True,
    ):
        if isinstance(texts, str):
            texts = [texts]

        embeddings = [
            self._embedding_for_text(text, normalize_embeddings)
            for text in texts
        ]

        if convert_to_numpy:
            return np.asarray(embeddings, dtype=np.float32)

        return embeddings

    @staticmethod
    def _embedding_for_text(text: str, normalize_embeddings: bool) -> np.ndarray:
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        repeated_bytes = (digest * ((EMBEDDING_DIMENSION // len(digest)) + 1))
        raw_values = np.frombuffer(
            repeated_bytes[:EMBEDDING_DIMENSION],
            dtype=np.uint8,
        ).astype(np.float32)

        # Center values around zero so fake vectors behave more like embeddings
        # in similarity tests than simple positive-only byte arrays.
        embedding = (raw_values - 127.5) / 127.5

        if normalize_embeddings:
            norm = np.linalg.norm(embedding)

            if norm > 0:
                embedding = embedding / norm

        return embedding.astype(np.float32)


def _is_test_fallback_enabled() -> bool:
    return os.getenv(DISABLE_TRANSFORMER_MODEL_ENV) == "1"


def _format_model_load_error(first_error: Exception,
                             cache_error: Exception) -> str:
    return (
        "Embedding model is unavailable.\n"
        f"Model: {EMBEDDING_MODEL_NAME}\n"
        "The model is not cached locally, or Hugging Face is unreachable from "
        "this environment.\n"
        "Run the project once while online to download and cache the model, "
        "then retry offline.\n"
        "For offline tests only, set DISABLE_TRANSFORMER_MODEL=1 to use "
        "deterministic fake embeddings.\n"
        f"Initial load error: {type(first_error).__name__}: {first_error}\n"
        f"Local-cache load error: {type(cache_error).__name__}: {cache_error}"
    )


def _load_sentence_transformer():
    print(f"[INFO] Loading embedding model: {EMBEDDING_MODEL_NAME}")
    print("[INFO] First attempt may download the model if it is not cached.")

    try:
        model = SentenceTransformer(EMBEDDING_MODEL_NAME)
        print("[INFO] Embedding model loaded successfully.")
        return model
    except Exception as first_error:
        print("[WARN] Normal embedding model load failed.")
        print(f"[WARN] Reason: {type(first_error).__name__}: {first_error}")
        print("[INFO] Retrying with local_files_only=True to use local cache.")

        try:
            model = SentenceTransformer(
                EMBEDDING_MODEL_NAME,
                local_files_only=True,
            )
            print("[INFO] Embedding model loaded from local cache.")
            return model
        except Exception as cache_error:
            print("[ERROR] Embedding model is not available from local cache.")
            print("[ERROR] Internet may be unavailable or the model was never cached.")
            raise RuntimeError(
                _format_model_load_error(first_error, cache_error)
            ) from cache_error


def get_embedding_model():
    """
    Lazily load and reuse the embedding model.

    Production uses SentenceTransformer. Tests can opt into a deterministic
    fake model with DISABLE_TRANSFORMER_MODEL=1.
    """

    global _embedding_model
    global _embedding_model_load_error

    if _embedding_model is not None:
        return _embedding_model

    if _is_test_fallback_enabled():
        print(
            "[INFO] DISABLE_TRANSFORMER_MODEL=1 detected. "
            "Using deterministic fake embeddings for tests."
        )
        _embedding_model = DeterministicFakeEmbeddingModel()
        return _embedding_model

    if _embedding_model_load_error is not None:
        raise _embedding_model_load_error

    try:
        _embedding_model = _load_sentence_transformer()
        return _embedding_model
    except RuntimeError as error:
        _embedding_model_load_error = error
        raise
