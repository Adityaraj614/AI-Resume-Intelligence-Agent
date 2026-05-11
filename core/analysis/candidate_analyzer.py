from typing import Any, Dict, List, Optional

from core.analysis.analysis_schema import (
    normalize_analysis_schema,
    validate_analysis_output,
)
from core.analysis.reasoning_utils import (
    build_evidence_trace,
    extract_top_strengths,
    infer_missing_skills,
    recommend_from_scores,
)
from core.llm.llm_client import LLMClient
from core.llm.prompt_templates import MATCH_ANALYSIS_PROMPT
from core.llm.response_parser import validate_llm_response


def _resolve_candidate_id(candidate_metadata: Optional[Dict[str, Any]],
                          matches: List[Dict[str, Any]]) -> str:
    if candidate_metadata and candidate_metadata.get("candidate_id"):
        return str(candidate_metadata["candidate_id"])

    for match in matches:
        if match.get("candidate_id"):
            return str(match["candidate_id"])

    return "unknown_candidate"


def _extract_matches(candidate_metadata: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if not candidate_metadata:
        return []

    matches = candidate_metadata.get("matches", [])

    if not isinstance(matches, list):
        raise TypeError("candidate_metadata['matches'] must be a list when provided.")

    return matches


def _build_analysis_prompt(structured_evidence_context: str,
                           job_description_context: str = "") -> str:
    return MATCH_ANALYSIS_PROMPT.format(
        job_description=job_description_context or "Use the JD context inside the evidence block.",
        context=structured_evidence_context,
    )


def analyze_candidate_match(
    structured_evidence_context: str,
    candidate_metadata: Optional[Dict[str, Any]] = None,
    jd_chunks: Optional[List[Dict[str, Any]]] = None,
    llm_client: Optional[LLMClient] = None,
) -> Dict[str, Any]:
    """
    Generate recruiter-style candidate analysis from retrieved evidence only.
    """

    if not isinstance(structured_evidence_context, str):
        raise TypeError("structured_evidence_context must be a string.")

    if not structured_evidence_context.strip():
        raise ValueError("structured_evidence_context cannot be empty.")

    if jd_chunks is None:
        jd_chunks = []

    if not isinstance(jd_chunks, list):
        raise TypeError("jd_chunks must be a list.")

    matches = _extract_matches(candidate_metadata)
    candidate_id = _resolve_candidate_id(candidate_metadata, matches)
    client = llm_client or LLMClient()
    prompt = _build_analysis_prompt(structured_evidence_context)
    llm_response = client.generate(prompt)

    if not validate_llm_response(llm_response):
        raise ValueError("LLM response does not match the required base schema.")

    evidence_trace = build_evidence_trace(matches)
    fallback_strengths = extract_top_strengths(matches)
    fallback_missing_skills = infer_missing_skills(jd_chunks, matches)

    analysis = {
        **llm_response,
        "candidate_id": candidate_id,
        "evidence_used": llm_response.get("evidence_used") or evidence_trace,
    }

    if not analysis["strengths"] and fallback_strengths:
        analysis["strengths"] = fallback_strengths

    if not analysis["missing_skills"] and fallback_missing_skills:
        analysis["missing_skills"] = fallback_missing_skills

    if candidate_metadata and candidate_metadata.get("aggregate_score") is not None:
        analysis["recommendation"] = recommend_from_scores(candidate_metadata)

    normalized_analysis = normalize_analysis_schema(analysis)

    if not normalized_analysis["evidence_used"] and evidence_trace:
        normalized_analysis["evidence_used"] = evidence_trace

    if not validate_analysis_output(normalized_analysis):
        raise ValueError("Candidate analysis output failed schema validation.")

    return normalized_analysis
