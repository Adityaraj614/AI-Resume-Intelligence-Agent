import numpy as np

from core.embeddings.embedding_model import get_embedding_model

from core.embeddings.embedding_cache import (
    get_cached_embedding,
    store_embedding
)


def generate_embeddings(
    texts,
    batch_size=32
):
    """
    Generate normalized embeddings with caching.
    """

    if not texts:
        return np.array([])

    final_embeddings = []

    texts_to_embed = []
    uncached_indices = []

    # Step 1: Check cache
    for idx, text in enumerate(texts):

        cached_embedding = get_cached_embedding(text)

        if cached_embedding is not None:

            final_embeddings.append(cached_embedding)

        else:

            final_embeddings.append(None)

            texts_to_embed.append(text)
            uncached_indices.append(idx)

    # Step 2: Generate missing embeddings
    if texts_to_embed:
        embedding_model = get_embedding_model()

        new_embeddings = embedding_model.encode(
            texts_to_embed,
            batch_size=batch_size,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=True
        )

        # Step 3: Store + insert embeddings
        for idx, embedding in zip(
            uncached_indices,
            new_embeddings
        ):

            store_embedding(
                texts[idx],
                np.asarray(embedding, dtype=np.float32)
            )

            final_embeddings[idx] = np.asarray(embedding, dtype=np.float32)

    return np.asarray(final_embeddings, dtype=np.float32)
