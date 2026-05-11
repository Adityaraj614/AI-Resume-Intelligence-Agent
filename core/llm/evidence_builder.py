from typing import Any, Dict, List, Optional

from core.llm.context_formatter import (
    SEPARATOR,
    format_candidate_metadata,
    format_job_description_context,
    format_retrieved_evidence,
)
from core.llm.retrieval_summarizer import summarize_retrieval_context


def _extract_candidate_matches(candidate_result: Dict[str, Any]) -> List[Dict[str, Any]]:
    matches = candidate_result.get("matches", [])

    if not isinstance(matches, list):
        raise TypeError("candidate_result['matches'] must be a list when provided.")

    return matches


def build_evidence_context(jd_chunks: List[Dict[str, Any]],
                           retrieved_chunks: Optional[List[Dict[str, Any]]] = None,
                           candidate_result: Optional[Dict[str, Any]] = None,
                           max_chunks: int = 8,
                           max_characters_per_chunk: int = 500) -> str:
    """
    Build one hallucination-safe LLM context block from retrieval evidence.

    The returned context is structured and evidence-only. It does not create new
    claims; it only formats, deduplicates, and truncates retrieved text.
    """

    if candidate_result is not None:
        retrieved_chunks = _extract_candidate_matches(candidate_result)

    if retrieved_chunks is None:
        retrieved_chunks = []

    summarized_chunks = summarize_retrieval_context(
        retrieved_chunks=retrieved_chunks,
        max_chunks=max_chunks,
        max_characters_per_chunk=max_characters_per_chunk,
    )

    context_blocks = [
        format_job_description_context(jd_chunks),
        SEPARATOR,
    ]

    if candidate_result is not None:
        context_blocks.extend([
            format_candidate_metadata(candidate_result),
            SEPARATOR,
        ])

    context_blocks.append(format_retrieved_evidence(summarized_chunks))

    return "\n\n".join(context_blocks)
