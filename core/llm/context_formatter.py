from typing import Any, Dict, List


SEPARATOR = "--------------------------------"


def _title_case_section(section: Any) -> str:
    if not isinstance(section, str) or not section.strip():
        return "Unknown"

    return section.strip().replace("_", " ").title()


def _format_score(score: Any) -> str:
    try:
        return f"{float(score):.2f}"
    except (TypeError, ValueError):
        return "N/A"


def format_job_description_context(jd_chunks: List[Dict[str, Any]]) -> str:
    """
    Format JD chunks into a compact prompt-ready block.
    """

    if not isinstance(jd_chunks, list):
        raise TypeError("jd_chunks must be a list.")

    lines = ["[JOB DESCRIPTION]"]

    for index, chunk in enumerate(jd_chunks, start=1):
        if not isinstance(chunk, dict):
            raise TypeError("Each JD chunk must be a dictionary.")

        lines.extend([
            "",
            f"Requirement {index}",
            f"Section: {_title_case_section(chunk.get('section', ''))}",
            "Content:",
            f"\"{chunk.get('chunk_text', '').strip()}\"",
        ])

    return "\n".join(lines)


def format_retrieved_evidence(retrieved_chunks: List[Dict[str, Any]]) -> str:
    """
    Format retrieved resume evidence while preserving retrieval metadata.
    """

    if not isinstance(retrieved_chunks, list):
        raise TypeError("retrieved_chunks must be a list.")

    lines = ["[RETRIEVED CANDIDATE EVIDENCE]"]

    for chunk in retrieved_chunks:
        if not isinstance(chunk, dict):
            raise TypeError("Each retrieved chunk must be a dictionary.")

        lines.extend([
            "",
            f"Candidate ID: {chunk.get('candidate_id', 'unknown_candidate')}",
            f"Section: {_title_case_section(chunk.get('section', ''))}",
            f"Similarity Score: {_format_score(chunk.get('score'))}",
            f"Matched JD Section: {_title_case_section(chunk.get('jd_section', ''))}",
            "Matched JD Chunk:",
            f"\"{chunk.get('jd_chunk_text', '').strip()}\"",
            "Content:",
            f"\"{chunk.get('chunk_text', '').strip()}\"",
            SEPARATOR,
        ])

    return "\n".join(lines)


def format_candidate_metadata(candidate_result: Dict[str, Any]) -> str:
    """
    Format candidate-level retrieval summary metadata when available.
    """

    if not isinstance(candidate_result, dict):
        raise TypeError("candidate_result must be a dictionary.")

    matched_sections = candidate_result.get("matched_sections", [])

    if isinstance(matched_sections, list):
        matched_sections_text = ", ".join(
            _title_case_section(section)
            for section in matched_sections
        )
    else:
        matched_sections_text = ""

    lines = [
        "[CANDIDATE RETRIEVAL SUMMARY]",
        f"Candidate ID: {candidate_result.get('candidate_id', 'unknown_candidate')}",
        f"Aggregate Score: {_format_score(candidate_result.get('aggregate_score'))}",
        f"JD Match Coverage: {_format_score(candidate_result.get('jd_match_coverage'))}",
        f"Match Count: {candidate_result.get('match_count', 0)}",
        f"Matched Sections: {matched_sections_text}",
    ]

    return "\n".join(lines)
