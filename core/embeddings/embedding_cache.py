import hashlib


embedding_cache = {}


def generate_text_hash(text):
    """
    Generate deterministic hash for text.
    """

    return hashlib.sha256(
        text.encode("utf-8")
    ).hexdigest()


def get_cached_embedding(text):
    """
    Retrieve cached embedding if available.
    """

    text_hash = generate_text_hash(text)

    return embedding_cache.get(text_hash)


def store_embedding(text, embedding):
    """
    Store embedding in cache.
    """

    text_hash = generate_text_hash(text)

    embedding_cache[text_hash] = embedding