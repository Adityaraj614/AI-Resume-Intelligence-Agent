from typing import Any, Dict, List


def interpret_similarity_score(score: float) -> str:
    """
    Convert a retrieval score into a conservative human-readable label.
    """

    score = float(score)

    if score >= 0.85:
        return "strong semantic match"

    if score >= 0.65:
        return "moderate semantic match"

    if score >= 0.45:
        return "weak semantic match"

    return "low-confidence match"


def build_evidence_trace(matches: List[Dict[str, Any]],
                         max_items: int = 5) -> List[str]:
    """
    Build explainable evidence statements from retrieval metadata.
    """

    if not isinstance(matches, list):
        raise TypeError("matches must be a list.")

    evidence_trace = []

    for match in matches[:max_items]:
        if not isinstance(match, dict):
            raise TypeError("Each match must be a dictionary.")

        resume_section = match.get("section", "unknown section")
        jd_section = match.get("jd_section", "unknown JD section")
        score = float(match.get("score", 0.0))
        score_label = interpret_similarity_score(score)

        evidence_trace.append(
            f"{resume_section} section matched {jd_section} "
            f"({score_label}, score {score:.2f})"
        )

    return evidence_trace


def extract_top_strengths(matches: List[Dict[str, Any]],
                          max_items: int = 3) -> List[str]:
    """
    Extract conservative strengths from top retrieved resume sections.
    """

    strengths = []
    seen_sections = set()

    for match in matches:
        section = str(match.get("section", "")).strip()
        chunk_text = str(match.get("chunk_text", "")).strip()

        if not section or not chunk_text:
            continue

        normalized_section = section.lower()

        if normalized_section in seen_sections:
            continue

        seen_sections.add(normalized_section)
        strengths.append(
            f"Evidence from {section} section: {chunk_text}"
        )

        if len(strengths) >= max_items:
            break

    return strengths


def infer_missing_skills(jd_chunks: List[Dict[str, Any]],
                         matches: List[Dict[str, Any]]) -> List[str]:
    """
    Conservatively identify JD chunks with no retrieved evidence.

    This does not infer actual missing skills beyond unmatched JD text.
    """

    matched_jd_texts = {
        str(match.get("jd_chunk_text", "")).strip().lower()
        for match in matches
        if match.get("jd_chunk_text")
    }
    missing_items = []

    for jd_chunk in jd_chunks:
        jd_text = str(jd_chunk.get("chunk_text", "")).strip()

        if jd_text and jd_text.lower() not in matched_jd_texts:
            missing_items.append(f"No retrieved evidence for JD item: {jd_text}")

    return missing_items


def recommend_from_scores(candidate_metadata: Dict[str, Any]) -> str:
    """
    Produce a simple recommendation label from retrieval metrics.
    """

    aggregate_score = float(candidate_metadata.get("aggregate_score", 0.0))
    jd_coverage = float(candidate_metadata.get("jd_match_coverage", 0.0))

    if aggregate_score >= 0.85 and jd_coverage >= 0.70:
        return "Strong Match"

    if aggregate_score >= 0.65 and jd_coverage >= 0.40:
        return "Moderate Match"

    return "Needs Review"
