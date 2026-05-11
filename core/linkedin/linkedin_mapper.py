import hashlib
import json
from typing import Any, Dict, List

from core.linkedin.linkedin_parser import parse_linkedin_json
from core.linkedin.linkedin_schema import LinkedInProfile
from core.linkedin.linkedin_utils import clean_text


def map_linkedin_to_candidate_profile(profile: Any) -> Dict[str, Any]:
    """
    Map LinkedInProfile into the unified internal candidate profile shape.

    Compatibility assumptions:
    - retrieval can consume ``profile_text`` or section-level text derived from it.
    - recruiter analytics read ``skills`` or ``extracted_skills``.
    - ranking/scoring attach scores later, so this adapter does not create scores.
    """

    linkedin_profile = profile if isinstance(profile, LinkedInProfile) else parse_linkedin_json(profile)
    profile_data = linkedin_profile.to_dict()
    skills = [skill["name"] for skill in profile_data["skills"]]
    experience = profile_data["experience"]
    education = profile_data["education"]
    projects = profile_data["projects"]
    certifications = profile_data["certifications"]
    candidate_id = _build_candidate_id(profile_data)
    section_chunks = _build_section_chunks(profile_data)
    profile_text = _build_profile_text(section_chunks)

    return {
        "candidate_id": candidate_id,
        "candidate_name": profile_data["name"] or candidate_id,
        "headline": profile_data["headline"],
        "summary": profile_data["summary"],
        "skills": skills,
        "extracted_skills": skills,
        "experience": experience,
        "education": education,
        "certifications": certifications,
        "projects": projects,
        "location": profile_data["location"],
        "linkedin_url": profile_data["linkedin_url"],
        "source": "linkedin",
        "source_metadata": {
            "source": "linkedin",
            "ingestion_type": "structured_json",
            "linkedin_url": profile_data["linkedin_url"],
        },
        "profile_text": profile_text,
        "section_chunks": section_chunks,
        "text": profile_text,
        "raw_profile": profile_data,
    }


def _build_candidate_id(profile_data: Dict[str, Any]) -> str:
    stable_identity = {
        "linkedin_url": profile_data.get("linkedin_url", ""),
        "name": profile_data.get("name", ""),
        "headline": profile_data.get("headline", ""),
    }
    serialized = json.dumps(stable_identity, sort_keys=True, ensure_ascii=True)
    digest = hashlib.sha256(serialized.encode("utf-8")).hexdigest()[:12]

    return f"linkedin_{digest}"


def _build_section_chunks(profile_data: Dict[str, Any]) -> Dict[str, List[str]]:
    sections = {
        "headline": _non_empty_lines([profile_data.get("headline", "")]),
        "summary": _non_empty_lines([profile_data.get("summary", "")]),
        "skills": _non_empty_lines([
            skill.get("name", "")
            for skill in profile_data.get("skills", [])
        ]),
        "experience": [],
        "projects": _non_empty_lines(profile_data.get("projects", [])),
        "education": [],
        "certifications": [],
    }

    for item in profile_data.get("experience", []):
        sections["experience"].append(
            _join_parts([
                item.get("title", ""),
                item.get("company", ""),
                _format_date_range(item.get("start_date", ""), item.get("end_date", "")),
                item.get("description", ""),
            ])
        )

    for item in profile_data.get("education", []):
        sections["education"].append(
            _join_parts([
                item.get("school", ""),
                item.get("degree", ""),
                item.get("field_of_study", ""),
                _format_date_range(item.get("start_date", ""), item.get("end_date", "")),
            ])
        )

    for item in profile_data.get("certifications", []):
        sections["certifications"].append(
            _join_parts([
                item.get("name", ""),
                item.get("issuer", ""),
                item.get("issue_date", ""),
            ])
        )

    return {
        section: _dedupe_lines(lines)
        for section, lines in sections.items()
        if _dedupe_lines(lines)
    }


def _build_profile_text(section_chunks: Dict[str, List[str]]) -> str:
    ordered_sections = (
        ("headline", "Headline"),
        ("summary", "Summary"),
        ("skills", "Skills"),
        ("experience", "Experience"),
        ("projects", "Projects"),
        ("education", "Education"),
        ("certifications", "Certifications"),
    )
    blocks = []

    for section_key, section_label in ordered_sections:
        lines = section_chunks.get(section_key, [])

        if not lines:
            continue

        blocks.append(f"{section_label}:\n" + "\n".join(lines))

    return "\n\n".join(blocks)


def _non_empty_lines(values: List[Any]) -> List[str]:
    return [
        clean_text(value)
        for value in values
        if clean_text(value)
    ]


def _join_parts(values: List[Any]) -> str:
    return " | ".join(_non_empty_lines(values))


def _format_date_range(start_date: str, end_date: str) -> str:
    start = clean_text(start_date)
    end = clean_text(end_date)

    if start and end:
        return f"{start} - {end}"

    return start or end


def _dedupe_lines(lines: List[str]) -> List[str]:
    seen = set()
    deduped = []

    for line in _non_empty_lines(lines):
        key = line.lower()

        if key in seen:
            continue

        seen.add(key)
        deduped.append(line)

    return deduped
