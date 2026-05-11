from typing import Any, Dict, List


def _normalize_text(text: Any) -> str:
    if not isinstance(text, str):
        return ""

    return " ".join(text.strip().lower().split())


def deduplicate_chunks(retrieved_chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Remove repeated resume chunk text while preserving first-seen order.

    This is conservative: it only removes exact normalized text duplicates and
    never rewrites evidence.
    """

    if not isinstance(retrieved_chunks, list):
        raise TypeError("retrieved_chunks must be a list.")

    deduplicated_chunks = []
    seen_chunk_texts = set()

    for chunk in retrieved_chunks:
        if not isinstance(chunk, dict):
            raise TypeError("Each retrieved chunk must be a dictionary.")

        normalized_text = _normalize_text(chunk.get("chunk_text", ""))

        if normalized_text in seen_chunk_texts:
            continue

        seen_chunk_texts.add(normalized_text)
        deduplicated_chunks.append(chunk)

    return deduplicated_chunks


def compress_long_chunk(chunk_text: str,
                        max_characters: int = 500) -> str:
    """
    Truncate long evidence without changing its meaning.
    """

    if not isinstance(chunk_text, str):
        raise TypeError("chunk_text must be a string.")

    if max_characters <= 0:
        raise ValueError("max_characters must be greater than 0.")

    compact_text = " ".join(chunk_text.strip().split())

    if len(compact_text) <= max_characters:
        return compact_text

    return compact_text[:max_characters].rstrip() + "..."


def summarize_retrieval_context(retrieved_chunks: List[Dict[str, Any]],
                                max_chunks: int = 8,
                                max_characters_per_chunk: int = 500) -> List[Dict[str, Any]]:
    """
    Build a compact retrieval evidence list without inventing new facts.
    """

    if not isinstance(max_chunks, int) or max_chunks <= 0:
        raise ValueError("max_chunks must be a positive integer.")

    deduplicated_chunks = deduplicate_chunks(retrieved_chunks)
    summarized_chunks = []

    for chunk in deduplicated_chunks[:max_chunks]:
        summarized_chunks.append({
            **chunk,
            "chunk_text": compress_long_chunk(
                chunk_text=chunk.get("chunk_text", ""),
                max_characters=max_characters_per_chunk,
            ),
        })

    return summarized_chunks
