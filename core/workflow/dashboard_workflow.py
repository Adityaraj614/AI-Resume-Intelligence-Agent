import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple

from core.analysis.analysis_schema import normalize_analysis_schema, validate_analysis_output
from core.analysis.candidate_analyzer import analyze_candidate_match
from core.analysis.reasoning_utils import (
    build_evidence_trace,
    extract_top_strengths,
    infer_missing_skills,
    recommend_from_scores,
)
from core.embeddings.jd_embedder import build_jd_chunk_records, embed_jd_chunks
from core.embeddings.resume_embedder import (
    build_chunk_records_from_resume_data,
    embed_resume_chunks,
)
from core.linkedin.linkedin_mapper import map_linkedin_to_candidate_profile
from core.linkedin.linkedin_parser import parse_linkedin_json
from core.linkedin.linkedin_validator import validate_linkedin_profile
from core.llm.context_formatter import (
    format_candidate_metadata,
    format_job_description_context,
    format_retrieved_evidence,
)
from core.parsing.parser import build_resume_data, extract_text_from_pdf
from core.ranking.ranking_engine import rank_candidates
from core.retrieval.resume_indexer import index_resume_embeddings
from core.retrieval.retriever import aggregate_candidate_scores, retrieve_resume_matches
from core.scoring.scoring_engine import score_candidate
from core.workflow.workflow_manager import run_recruiter_workflow


logger = logging.getLogger(__name__)


class DashboardWorkflowError(RuntimeError):
    """
    Recruiter-safe wrapper for integration failures surfaced to the UI.
    """


def run_dashboard_workflow(inputs: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(inputs, dict):
        raise TypeError("inputs must be a dictionary.")

    try:
        job_description = _resolve_job_description(inputs)
    except Exception as exc:
        logger.exception("dashboard_workflow_jd_intake_failed")
        raise DashboardWorkflowError(
            "The job description could not be read. Use pasted text or upload a valid TXT, MD, or PDF file."
        ) from exc

    resume_files = list(inputs.get("resume_files", []) or [])
    linkedin_files = list(inputs.get("linkedin_files", []) or [])

    if not job_description.strip():
        raise DashboardWorkflowError("Add a job description before analyzing candidates.")

    if not resume_files and not linkedin_files:
        raise DashboardWorkflowError("Upload at least one resume PDF or LinkedIn JSON profile.")

    candidate_profiles, intake_warnings = _build_candidate_profiles(resume_files, linkedin_files)

    if not candidate_profiles:
        raise DashboardWorkflowError(
            "No valid candidate profiles could be prepared from the uploaded files."
        )

    try:
        ranked_candidates, pipeline_debug = _build_ranked_candidates(
            job_description,
            candidate_profiles,
        )
    except RuntimeError as exc:
        raise DashboardWorkflowError(_friendly_runtime_error(exc)) from exc
    except Exception as exc:
        raise DashboardWorkflowError(
            "Candidate analysis could not be completed. Review uploaded files and configuration, then try again."
        ) from exc

    if not ranked_candidates:
        raise DashboardWorkflowError(
            "The workflow completed intake, but no candidates had enough evidence for ranking."
        )

    workflow_result = run_recruiter_workflow(
        ranked_candidates=ranked_candidates,
        execution_timestamp=_current_timestamp(),
    )
    workflow_result["workflow_outputs"]["candidate_profiles"] = candidate_profiles
    workflow_result["workflow_outputs"]["pipeline_debug"] = pipeline_debug
    workflow_result["diagnostics"]["pipeline_warnings"].extend(intake_warnings)

    return workflow_result


def _resolve_job_description(inputs: Dict[str, Any]) -> str:
    pasted_text = str(inputs.get("job_description", "") or "").strip()
    jd_file = inputs.get("jd_file")

    if jd_file is None:
        return pasted_text

    file_name = str(getattr(jd_file, "name", "")).lower()

    if file_name.endswith(".pdf"):
        file_text = extract_text_from_pdf(_fresh_file(jd_file))
    else:
        file_text = _read_text_file(jd_file)

    return "\n\n".join(part for part in (pasted_text, file_text.strip()) if part)


def _build_candidate_profiles(
    resume_files: List[Any],
    linkedin_files: List[Any],
) -> Tuple[List[Dict[str, Any]], List[str]]:
    profiles = []
    warnings = []

    for index, resume_file in enumerate(resume_files, start=1):
        try:
            resume_data = build_resume_data(_fresh_file(resume_file))
            candidate_id = _stable_resume_candidate_id(resume_data, index)
            profile = _resume_data_to_candidate_profile(resume_data, candidate_id)
            profiles.append(profile)
        except Exception as exc:
            logger.warning(
                "dashboard_workflow_resume_intake_failed",
                extra={"file_name": getattr(resume_file, "name", str(index))},
                exc_info=True,
            )
            warnings.append(
                f"Resume {getattr(resume_file, 'name', index)} could not be processed: {exc}"
            )

    for index, linkedin_file in enumerate(linkedin_files, start=1):
        try:
            payload = json.loads(_read_text_file(linkedin_file))
            profile = parse_linkedin_json(payload, strict=True)
            validation = validate_linkedin_profile(profile)

            if not validation["is_valid"]:
                raise ValueError("; ".join(validation["errors"]))

            profiles.append(map_linkedin_to_candidate_profile(profile))
        except Exception as exc:
            logger.warning(
                "dashboard_workflow_linkedin_intake_failed",
                extra={"file_name": getattr(linkedin_file, "name", str(index))},
                exc_info=True,
            )
            warnings.append(
                f"LinkedIn profile {getattr(linkedin_file, 'name', index)} could not be processed: {exc}"
            )

    return profiles, warnings


def _build_ranked_candidates(
    job_description: str,
    candidate_profiles: List[Dict[str, Any]],
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    jd_chunks = build_jd_chunk_records(job_description)
    embedded_jd_chunks = embed_jd_chunks(jd_chunks)
    resume_chunk_records = []

    for profile in candidate_profiles:
        resume_chunk_records.extend(build_chunk_records_from_resume_data(profile))

    if not resume_chunk_records:
        raise DashboardWorkflowError("No candidate text chunks were available for retrieval.")

    embedded_resume_chunks = embed_resume_chunks(resume_chunk_records)
    resume_index = index_resume_embeddings(embedded_resume_chunks)
    retrieval_results = retrieve_resume_matches(
        jd_embedding_records=embedded_jd_chunks,
        resume_index_bundle=resume_index,
        top_k=5,
        minimum_similarity_score=0.0,
    )
    candidate_metadata = aggregate_candidate_scores(
        retrieval_results,
        aggregation_method="hybrid_max_average",
        top_n=5,
        minimum_candidate_score=0.0,
        minimum_jd_coverage=0.0,
        include_eliminated=True,
    )
    scoring_outputs = []
    safety_results = {}
    evidence_quality_signals = {}

    for metadata in candidate_metadata:
        analysis = _analyze_candidate(job_description, jd_chunks, metadata)
        safety = _safety_result(analysis, metadata)
        scoring = score_candidate(metadata, analysis)
        scoring_outputs.append(scoring)
        safety_results[metadata["candidate_id"]] = safety
        evidence_quality_signals[metadata["candidate_id"]] = {
            "evidence_coverage": metadata.get("jd_match_coverage", 0.0),
            "retrieval_quality": metadata.get("aggregate_score", 0.0),
            "jd_match_coverage": metadata.get("jd_match_coverage", 0.0),
        }

    ranked = rank_candidates(
        scoring_outputs,
        safety_results=safety_results,
        evidence_quality_signals=evidence_quality_signals,
    )
    enriched_ranked = _enrich_ranked_candidates(
        ranked,
        candidate_profiles,
        candidate_metadata,
        safety_results,
    )

    return enriched_ranked, {
        "jd_chunk_count": len(jd_chunks),
        "resume_chunk_count": len(resume_chunk_records),
        "retrieval_match_count": len(retrieval_results),
        "ranked_candidate_count": len(enriched_ranked),
    }


def _analyze_candidate(
    job_description: str,
    jd_chunks: List[Dict[str, Any]],
    metadata: Dict[str, Any],
) -> Dict[str, Any]:
    evidence_context = "\n\n".join([
        format_job_description_context(jd_chunks),
        format_candidate_metadata(metadata),
        format_retrieved_evidence(metadata.get("matches", [])),
    ])

    try:
        return analyze_candidate_match(
            evidence_context,
            candidate_metadata=metadata,
            jd_chunks=jd_chunks,
        )
    except Exception:
        logger.warning(
            "dashboard_workflow_llm_analysis_fallback",
            extra={"candidate_id": metadata.get("candidate_id", "unknown_candidate")},
            exc_info=True,
        )
        fallback = normalize_analysis_schema({
            "candidate_id": metadata.get("candidate_id", "unknown_candidate"),
            "summary": _fallback_summary(metadata),
            "strengths": extract_top_strengths(metadata.get("matches", [])),
            "missing_skills": infer_missing_skills(jd_chunks, metadata.get("matches", [])),
            "evidence_used": build_evidence_trace(metadata.get("matches", [])),
            "recommendation": recommend_from_scores(metadata),
        })

        if not validate_analysis_output(fallback):
            raise

        return fallback


def _safety_result(analysis: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
    from core.safety.evidence_validator import validate_analysis_evidence

    validation = validate_analysis_evidence(analysis, metadata)

    return {
        "is_safe": validation["is_valid"],
        "unsupported_claims": validation["unsupported_items"],
        "hallucination_risk": 0.0 if validation["is_valid"] else 0.50,
    }


def _enrich_ranked_candidates(
    ranked_candidates: List[Dict[str, Any]],
    candidate_profiles: List[Dict[str, Any]],
    candidate_metadata: List[Dict[str, Any]],
    safety_results: Dict[str, Dict[str, Any]],
) -> List[Dict[str, Any]]:
    profiles_by_id = {
        str(profile.get("candidate_id", "")): profile
        for profile in candidate_profiles
    }
    metadata_by_id = {
        str(metadata.get("candidate_id", "")): metadata
        for metadata in candidate_metadata
    }

    enriched = []

    for ranked in ranked_candidates:
        candidate_id = str(ranked.get("candidate_id", ""))
        profile = profiles_by_id.get(candidate_id, {})
        metadata = metadata_by_id.get(candidate_id, {})
        safety = safety_results.get(candidate_id, {})

        enriched.append({
            **profile,
            **metadata,
            **ranked,
            "ranking_position": ranked.get("rank"),
            "confidence_score": ranked.get("confidence", 0.0),
            "source": profile.get("source", "resume"),
            "safety_result": safety,
        })

    return enriched


def _resume_data_to_candidate_profile(
    resume_data: Dict[str, Any],
    candidate_id: str,
) -> Dict[str, Any]:
    metadata = resume_data.get("metadata", {}) if isinstance(resume_data.get("metadata"), dict) else {}
    sections = resume_data.get("sections", {}) if isinstance(resume_data.get("sections"), dict) else {}

    return {
        **resume_data,
        "candidate_id": candidate_id,
        "candidate_name": resume_data.get("candidate_name", candidate_id),
        "source": "resume",
        "text": resume_data.get("resume_text", ""),
        "profile_text": resume_data.get("resume_text", ""),
        "extracted_skills": metadata.get("skills", _section_lines(sections.get("skills", ""))),
        "skills": metadata.get("skills", _section_lines(sections.get("skills", ""))),
        "experience": _section_lines(sections.get("experience", "")),
        "education": _section_lines(sections.get("education", "")),
        "projects": _section_lines(sections.get("projects", "")),
        "certifications": _section_lines(sections.get("certifications", "")),
    }


def _section_lines(section_text: Any) -> List[str]:
    return [
        line.strip(" -*\t")
        for line in str(section_text or "").splitlines()
        if line.strip(" -*\t")
    ]


def _stable_resume_candidate_id(resume_data: Dict[str, Any], index: int) -> str:
    file_name = str(resume_data.get("file_name", "") or "").strip()

    if file_name:
        return file_name

    candidate_name = str(resume_data.get("candidate_name", "") or "").strip()
    return candidate_name or f"resume_{index:03d}"


def _fresh_file(uploaded_file: Any) -> Any:
    if hasattr(uploaded_file, "seek"):
        uploaded_file.seek(0)

    return uploaded_file


def _read_text_file(uploaded_file: Any) -> str:
    if hasattr(uploaded_file, "getvalue"):
        raw = uploaded_file.getvalue()
    else:
        _fresh_file(uploaded_file)
        raw = uploaded_file.read()

    if isinstance(raw, str):
        return raw

    return bytes(raw).decode("utf-8", errors="replace")


def _fallback_summary(metadata: Dict[str, Any]) -> str:
    evidence_trace = build_evidence_trace(metadata.get("matches", []), max_items=1)

    if evidence_trace:
        return evidence_trace[0]

    return "Candidate has limited retrieved evidence for this job description."


def _friendly_runtime_error(error: RuntimeError) -> str:
    message = str(error)

    if "Embedding model is unavailable" in message:
        return (
            "The embedding model is unavailable. Download/cache the configured "
            "SentenceTransformer model, or set DISABLE_TRANSFORMER_MODEL=1 for local offline testing."
        )

    return message


def _current_timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
