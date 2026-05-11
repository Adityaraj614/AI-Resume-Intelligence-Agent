import json
from typing import Any, Dict

from core.linkedin.linkedin_normalizer import (
    normalize_date_fields,
    normalize_profile_dict,
    normalize_skills,
    normalize_text_list,
)
from core.linkedin.linkedin_schema import (
    LinkedInCertification,
    LinkedInEducation,
    LinkedInExperience,
    LinkedInProfile,
    LinkedInSkill,
)
from core.linkedin.linkedin_utils import as_list, clean_text, safe_get
from core.linkedin.linkedin_validator import validate_linkedin_profile


def parse_linkedin_json(raw_profile: Any, strict: bool = False) -> LinkedInProfile:
    """
    Parse mock/exported LinkedIn JSON into a deterministic LinkedInProfile.
    """

    data = _load_json_payload(raw_profile)
    normalized = normalize_profile_dict(data)
    profile = LinkedInProfile(
        name=normalized["name"],
        headline=normalized["headline"],
        summary=normalized["summary"],
        skills=[
            LinkedInSkill(name=skill)
            for skill in normalize_skills(_extract_skill_values(data.get("skills", [])))
        ],
        experience=[
            _parse_experience(item)
            for item in as_list(data.get("experience", []))
            if isinstance(item, dict)
        ],
        education=[
            _parse_education(item)
            for item in as_list(data.get("education", []))
            if isinstance(item, dict)
        ],
        certifications=[
            _parse_certification(item)
            for item in as_list(data.get("certifications", []))
            if isinstance(item, dict)
        ],
        projects=normalize_text_list(data.get("projects", [])),
        location=normalized["location"],
        linkedin_url=normalized["linkedin_url"],
    )
    profile = _order_profile_sections(profile)

    validation = validate_linkedin_profile(profile)

    if strict and not validation["is_valid"]:
        raise ValueError("; ".join(validation["errors"]))

    return profile


def _load_json_payload(raw_profile: Any) -> Dict[str, Any]:
    if isinstance(raw_profile, dict):
        return raw_profile

    if isinstance(raw_profile, str):
        try:
            data = json.loads(raw_profile)
        except json.JSONDecodeError as exc:
            raise ValueError("LinkedIn JSON payload is malformed.") from exc

        if not isinstance(data, dict):
            raise ValueError("LinkedIn JSON payload must be an object.")

        return data

    raise TypeError("raw_profile must be a dictionary or JSON string.")


def _extract_skill_values(skills: Any) -> list:
    values = []

    for skill in as_list(skills):
        if isinstance(skill, dict):
            values.append(skill.get("name", ""))
        else:
            values.append(skill)

    return values


def _parse_experience(item: Dict[str, Any]) -> LinkedInExperience:
    normalized_dates = normalize_date_fields(item)

    return LinkedInExperience(
        title=clean_text(safe_get(item, "title")),
        company=clean_text(safe_get(item, "company")),
        start_date=normalized_dates["start_date"],
        end_date=normalized_dates["end_date"],
        location=clean_text(safe_get(item, "location")),
        description=clean_text(safe_get(item, "description")),
    )


def _parse_education(item: Dict[str, Any]) -> LinkedInEducation:
    normalized_dates = normalize_date_fields(item)

    return LinkedInEducation(
        school=clean_text(safe_get(item, "school")),
        degree=clean_text(safe_get(item, "degree")),
        field_of_study=clean_text(safe_get(item, "field_of_study")),
        start_date=normalized_dates["start_date"],
        end_date=normalized_dates["end_date"],
    )


def _parse_certification(item: Dict[str, Any]) -> LinkedInCertification:
    return LinkedInCertification(
        name=clean_text(safe_get(item, "name")),
        issuer=clean_text(safe_get(item, "issuer")),
        issue_date=clean_text(safe_get(item, "issue_date")),
        credential_id=clean_text(safe_get(item, "credential_id")),
    )


def _order_profile_sections(profile: LinkedInProfile) -> LinkedInProfile:
    """
    Apply stable ordering to LinkedIn-origin lists before downstream mapping.
    """

    return LinkedInProfile(
        name=profile.name,
        headline=profile.headline,
        summary=profile.summary,
        skills=sorted(profile.skills, key=lambda skill: skill.name.lower()),
        experience=sorted(
            profile.experience,
            key=lambda item: (
                item.start_date,
                item.end_date,
                item.company.lower(),
                item.title.lower(),
            ),
            reverse=True,
        ),
        education=sorted(
            profile.education,
            key=lambda item: (
                item.start_date,
                item.end_date,
                item.school.lower(),
                item.degree.lower(),
            ),
            reverse=True,
        ),
        certifications=sorted(
            profile.certifications,
            key=lambda item: (
                item.issue_date,
                item.issuer.lower(),
                item.name.lower(),
            ),
            reverse=True,
        ),
        projects=sorted(profile.projects, key=lambda project: project.lower()),
        location=profile.location,
        linkedin_url=profile.linkedin_url,
    )
