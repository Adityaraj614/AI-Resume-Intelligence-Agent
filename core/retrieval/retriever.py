from difflib import SequenceMatcher
from typing import Any, Dict, List, Optional

import numpy as np

from core.retrieval.faiss_index import search_index


DEFAULT_SECTION_WEIGHTS = {
    "projects": 1.5,
    "experience": 1.5,
    "skills": 1.2,
    "certifications": 1.0,
    "education": 0.8,
    "summary": 0.7,
    "hobbies": 0.2,
}

SUPPORTED_AGGREGATION_METHODS = (
    "average",
    "max",
    "weighted",
    "weighted_average",
    "top_k_average",
    "hybrid_max_average",
)


def _validate_resume_index_bundle(resume_index_bundle: Dict[str, Any]) -> None:
    if not isinstance(resume_index_bundle, dict):
        raise TypeError("resume_index_bundle must be a dictionary.")

    if "index" not in resume_index_bundle:
        raise ValueError("resume_index_bundle is missing index.")

    if "metadata_store" not in resume_index_bundle:
        raise ValueError("resume_index_bundle is missing metadata_store.")

    metadata_store = resume_index_bundle["metadata_store"]

    if not isinstance(metadata_store, list):
        raise TypeError("metadata_store must be a list.")

    faiss_index = resume_index_bundle["index"]

    if faiss_index.ntotal != len(metadata_store):
        raise ValueError(
            "FAISS vector count and metadata count must match before retrieval."
        )


def _prepare_jd_embedding_record(record: Dict[str, Any],
                                 record_index: int,
                                 expected_dim: int) -> Dict[str, Any]:
    if not isinstance(record, dict):
        raise TypeError(
            f"JD embedding record at index {record_index} must be a dictionary."
        )

    if "embedding" not in record:
        raise ValueError(
            f"JD embedding record at index {record_index} is missing embedding."
        )

    embedding = np.asarray(record["embedding"], dtype=np.float32)

    if embedding.ndim != 1:
        raise ValueError(
            f"JD embedding at index {record_index} must be a 1D vector."
        )

    if embedding.shape[0] != expected_dim:
        raise ValueError(
            f"JD embedding at index {record_index} has dimension "
            f"{embedding.shape[0]}, expected {expected_dim}."
        )

    return {
        **record,
        "embedding": embedding.astype(np.float32, copy=False),
    }


def _normalize_section(section: Any) -> str:
    if not isinstance(section, str):
        return ""

    return " ".join(section.strip().lower().split()).replace(" ", "_")


def _get_section_weight(section: Any,
                        section_weights: Optional[Dict[str, float]]) -> float:
    weights = section_weights or DEFAULT_SECTION_WEIGHTS
    normalized_section = _normalize_section(section)

    return float(weights.get(normalized_section, 1.0))


def _build_retrieval_result(jd_record: Dict[str, Any],
                            resume_match: Dict[str, Any],
                            total_jd_chunks: int,
                            section_weights: Optional[Dict[str, float]]) -> Dict[str, Any]:
    score = float(resume_match["score"])
    section_weight = _get_section_weight(
        section=resume_match.get("section", ""),
        section_weights=section_weights,
    )

    return {
        "jd_section": jd_record.get("section", ""),
        "jd_chunk_index": jd_record.get("chunk_index"),
        "jd_chunk_text": jd_record.get("chunk_text", ""),
        "jd_total_chunks": total_jd_chunks,
        "section_weight": section_weight,
        "weighted_score": float(score * section_weight),
        **resume_match,
    }


def retrieve_resume_matches(jd_embedding_records: List[Dict[str, Any]],
                            resume_index_bundle: Dict[str, Any],
                            top_k: int = 5,
                            minimum_similarity_score: float = 0.0,
                            section_weights: Optional[Dict[str, float]] = None) -> List[Dict[str, Any]]:
    """
    Query the resume FAISS database for every embedded JD chunk.

    Each returned result keeps both sides of the match: the JD chunk that asked
    the question and the resume chunk that FAISS found semantically similar.
    """

    if jd_embedding_records is None:
        raise ValueError("jd_embedding_records cannot be None.")

    if not isinstance(jd_embedding_records, list):
        raise TypeError("jd_embedding_records must be a list of dictionaries.")

    if not isinstance(top_k, int) or top_k <= 0:
        raise ValueError("top_k must be a positive integer.")

    if minimum_similarity_score < 0:
        raise ValueError("minimum_similarity_score cannot be negative.")

    _validate_resume_index_bundle(resume_index_bundle)

    faiss_index = resume_index_bundle["index"]
    metadata_store = resume_index_bundle["metadata_store"]
    retrieval_results = []
    total_jd_chunks = len(jd_embedding_records)

    for record_index, jd_record in enumerate(jd_embedding_records):
        prepared_jd_record = _prepare_jd_embedding_record(
            record=jd_record,
            record_index=record_index,
            expected_dim=faiss_index.d,
        )

        resume_matches = search_index(
            faiss_index=faiss_index,
            query_embedding=prepared_jd_record["embedding"],
            metadata_store=metadata_store,
            top_k=top_k,
        )

        retrieval_results.extend(
            _build_retrieval_result(
                jd_record=prepared_jd_record,
                resume_match=resume_match,
                total_jd_chunks=total_jd_chunks,
                section_weights=section_weights,
            )
            for resume_match in resume_matches
            if float(resume_match["score"]) >= minimum_similarity_score
        )

    return retrieval_results


def retrieve_top_chunks(retrieval_results: List[Dict[str, Any]],
                        top_k: int = 10) -> List[Dict[str, Any]]:
    """
    Return the highest-scoring JD-to-resume chunk matches globally.
    """

    if not isinstance(retrieval_results, list):
        raise TypeError("retrieval_results must be a list.")

    if not isinstance(top_k, int) or top_k <= 0:
        raise ValueError("top_k must be a positive integer.")

    sorted_results = sorted(
        retrieval_results,
        key=lambda result: result.get("score", float("-inf")),
        reverse=True,
    )

    return sorted_results[:top_k]


def group_results_by_candidate(
    retrieval_results: List[Dict[str, Any]]
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Group chunk-level retrieval results under each candidate id.
    """

    if not isinstance(retrieval_results, list):
        raise TypeError("retrieval_results must be a list.")

    grouped_results = {}

    for result in retrieval_results:
        if not isinstance(result, dict):
            raise TypeError("Each retrieval result must be a dictionary.")

        candidate_id = result.get("candidate_id")

        if not candidate_id:
            raise ValueError("Each retrieval result must include candidate_id.")

        grouped_results.setdefault(candidate_id, []).append(result)

    return grouped_results


def _aggregate_scores(scores: List[float], method: str) -> float:
    if method == "max":
        return max(scores)

    if method in ("average", "weighted_average", "top_k_average"):
        return sum(scores) / len(scores)

    if method == "weighted":
        weights = [
            1.0 / (rank + 1)
            for rank in range(len(scores))
        ]
        weighted_total = sum(
            score * weight
            for score, weight in zip(scores, weights)
        )

        return weighted_total / sum(weights)

    if method == "hybrid_max_average":
        average_score = sum(scores) / len(scores)
        max_score = max(scores)

        return (max_score * 0.6) + (average_score * 0.4)

    raise ValueError(
        "aggregation_method must be one of: "
        f"{', '.join(SUPPORTED_AGGREGATION_METHODS)}."
    )


def _normalize_text(text: Any) -> str:
    if not isinstance(text, str):
        return ""

    return " ".join(text.strip().lower().split())


def _is_near_duplicate(text: str,
                       seen_texts: List[str],
                       similarity_threshold: float) -> bool:
    for seen_text in seen_texts:
        similarity = SequenceMatcher(None, text, seen_text).ratio()

        if similarity >= similarity_threshold:
            return True

    return False


def _suppress_duplicate_matches(
    matches: List[Dict[str, Any]],
    suppress_exact_duplicates: bool,
    suppress_near_duplicates: bool,
    near_duplicate_threshold: float,
) -> List[Dict[str, Any]]:
    if not suppress_exact_duplicates and not suppress_near_duplicates:
        return matches

    deduped_matches = []
    seen_exact_texts = set()
    seen_texts = []

    for match in matches:
        normalized_text = _normalize_text(match.get("chunk_text", ""))

        if suppress_exact_duplicates and normalized_text in seen_exact_texts:
            continue

        if (
            suppress_near_duplicates
            and _is_near_duplicate(normalized_text, seen_texts, near_duplicate_threshold)
        ):
            continue

        deduped_matches.append(match)
        seen_exact_texts.add(normalized_text)
        seen_texts.append(normalized_text)

    return deduped_matches


def _get_match_score(match: Dict[str, Any],
                     use_section_weights: bool) -> float:
    if use_section_weights:
        return float(match.get("weighted_score", match["score"]))

    return float(match["score"])


def _infer_total_jd_chunks(retrieval_results: List[Dict[str, Any]]) -> int:
    explicit_counts = [
        int(result["jd_total_chunks"])
        for result in retrieval_results
        if result.get("jd_total_chunks") is not None
    ]

    if explicit_counts:
        return max(explicit_counts)

    unique_jd_keys = {
        (
            result.get("jd_section", ""),
            result.get("jd_chunk_index"),
            result.get("jd_chunk_text", ""),
        )
        for result in retrieval_results
    }

    return len(unique_jd_keys)


def _calculate_jd_match_coverage(matches: List[Dict[str, Any]],
                                 total_jd_chunks: int,
                                 coverage_similarity_threshold: float) -> float:
    if total_jd_chunks <= 0:
        return 0.0

    matched_jd_chunks = {
        (
            match.get("jd_section", ""),
            match.get("jd_chunk_index"),
            match.get("jd_chunk_text", ""),
        )
        for match in matches
        if float(match.get("score", 0.0)) >= coverage_similarity_threshold
    }

    return len(matched_jd_chunks) / total_jd_chunks


def _candidate_matches_required_sections(
    matches: List[Dict[str, Any]],
    required_jd_sections: Optional[List[str]],
) -> bool:
    if not required_jd_sections:
        return True

    normalized_required_sections = {
        _normalize_section(section)
        for section in required_jd_sections
    }

    return any(
        _normalize_section(match.get("jd_section", "")) in normalized_required_sections
        for match in matches
    )


def aggregate_candidate_scores(
    retrieval_results: List[Dict[str, Any]],
    aggregation_method: str = "average",
    top_n: int = 3,
    minimum_candidate_score: float = 0.0,
    minimum_jd_coverage: float = 0.0,
    coverage_similarity_threshold: float = 0.45,
    required_jd_sections: Optional[List[str]] = None,
    use_section_weights: bool = True,
    suppress_exact_duplicates: bool = False,
    suppress_near_duplicates: bool = False,
    near_duplicate_threshold: float = 0.92,
    include_eliminated: bool = False,
    total_jd_chunks: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """
    Convert explainable chunk matches into candidate-level relevance scores.

    By default, each candidate score is the average of that candidate's top
    matching chunks. This avoids one weak chunk dragging down an otherwise
    relevant candidate while still rewarding repeated semantic matches.
    """

    if aggregation_method not in SUPPORTED_AGGREGATION_METHODS:
        raise ValueError(
            "aggregation_method must be one of: "
            f"{', '.join(SUPPORTED_AGGREGATION_METHODS)}."
        )

    if not isinstance(top_n, int) or top_n <= 0:
        raise ValueError("top_n must be a positive integer.")

    if minimum_candidate_score < 0:
        raise ValueError("minimum_candidate_score cannot be negative.")

    if not 0 <= minimum_jd_coverage <= 1:
        raise ValueError("minimum_jd_coverage must be between 0 and 1.")

    if coverage_similarity_threshold < 0:
        raise ValueError("coverage_similarity_threshold cannot be negative.")

    if not 0 <= near_duplicate_threshold <= 1:
        raise ValueError("near_duplicate_threshold must be between 0 and 1.")

    grouped_results = group_results_by_candidate(retrieval_results)
    candidate_scores = []
    resolved_total_jd_chunks = (
        total_jd_chunks
        if total_jd_chunks is not None
        else _infer_total_jd_chunks(retrieval_results)
    )

    for candidate_id, candidate_matches in grouped_results.items():
        sorted_matches = retrieve_top_chunks(
            retrieval_results=candidate_matches,
            top_k=len(candidate_matches),
        )
        deduped_matches = _suppress_duplicate_matches(
            matches=sorted_matches,
            suppress_exact_duplicates=suppress_exact_duplicates,
            suppress_near_duplicates=suppress_near_duplicates,
            near_duplicate_threshold=near_duplicate_threshold,
        )

        if not deduped_matches:
            continue

        top_matches = deduped_matches[:top_n]
        scores = [
            _get_match_score(match, use_section_weights)
            for match in top_matches
        ]
        aggregate_score = float(
            _aggregate_scores(scores, aggregation_method)
        )
        jd_match_coverage = float(
            _calculate_jd_match_coverage(
                matches=deduped_matches,
                total_jd_chunks=resolved_total_jd_chunks,
                coverage_similarity_threshold=coverage_similarity_threshold,
            )
        )
        matched_sections = sorted({
            match.get("section", "")
            for match in deduped_matches
            if match.get("section")
        })

        candidate_result = {
            "candidate_id": candidate_id,
            "aggregate_score": aggregate_score,
            "jd_match_coverage": jd_match_coverage,
            "matched_sections": matched_sections,
            "match_count": len(deduped_matches),
            "top_match": top_matches[0],
            "matches": deduped_matches,
        }

        eliminated_reasons = []

        if aggregate_score < minimum_candidate_score:
            eliminated_reasons.append("below_minimum_candidate_score")

        if jd_match_coverage < minimum_jd_coverage:
            eliminated_reasons.append("below_minimum_jd_coverage")

        if not _candidate_matches_required_sections(
            matches=deduped_matches,
            required_jd_sections=required_jd_sections,
        ):
            eliminated_reasons.append("missing_required_jd_section")

        if eliminated_reasons:
            candidate_result["eliminated_reason"] = ", ".join(eliminated_reasons)

            if not include_eliminated:
                continue

        candidate_scores.append(candidate_result)

    return sorted(
        candidate_scores,
        key=lambda result: result["aggregate_score"],
        reverse=True,
    )
