from typing import Any, Dict, List

from core.linkedin.linkedin_schema import LinkedInProfile
from core.linkedin.linkedin_utils import clean_text, is_valid_date_range


def _profile_to_dict(profile: Any) -> Dict[str, Any]:
    if isinstance(profile, LinkedInProfile):
        return profile.to_dict()

    if isinstance(profile, dict):
        return profile

    return {}


def validate_linkedin_profile(profile: Any) -> Dict[str, Any]:
    """
    Validate LinkedIn-style profile data with deterministic recruiter-safe output.
    """

    data = _profile_to_dict(profile)
    errors: List[str] = []
    warnings: List[str] = []

    if not data:
        errors.append("Profile must be a dictionary or LinkedInProfile.")

    if not clean_text(data.get("name", "")):
        errors.append("Missing required field: name.")

    skills = data.get("skills", [])

    if not isinstance(skills, list):
        errors.append("Skills must be a list.")
        skills = []

    skill_names = [
        clean_text(skill.get("name", skill) if isinstance(skill, dict) else skill)
        for skill in skills
    ]
    empty_skill_count = len([skill for skill in skill_names if not skill])

    if empty_skill_count:
        warnings.append(f"{empty_skill_count} empty skills were ignored.")

    non_empty_skill_names = [
        skill
        for skill in skill_names
        if skill
    ]
    duplicate_skill_count = len(non_empty_skill_names) - len({
        skill.lower()
        for skill in non_empty_skill_names
    })

    if duplicate_skill_count:
        warnings.append(f"{duplicate_skill_count} duplicate skills detected.")

    experience = data.get("experience", [])

    if not isinstance(experience, list):
        errors.append("Experience must be a list.")
        experience = []

    for index, item in enumerate(experience):
        if not isinstance(item, dict):
            errors.append(f"Experience entry {index} is malformed.")
            continue

        if not clean_text(item.get("title", "")) and not clean_text(item.get("company", "")):
            warnings.append(f"Experience entry {index} is missing title and company.")

        if not is_valid_date_range(item.get("start_date", ""), item.get("end_date", "")):
            errors.append(f"Experience entry {index} has an invalid date range.")

    education = data.get("education", [])

    if not isinstance(education, list):
        errors.append("Education must be a list.")

    duplicate_sections = _detect_duplicate_sections(data)
    warnings.extend(duplicate_sections)

    status = "valid" if not errors else "invalid"

    return {
        "is_valid": not errors,
        "status": status,
        "errors": errors,
        "warnings": warnings,
        "error_count": len(errors),
        "warning_count": len(warnings),
    }


def _detect_duplicate_sections(data: Dict[str, Any]) -> List[str]:
    warnings = []

    for section in ("experience", "education", "certifications", "projects"):
        items = data.get(section, [])

        if not isinstance(items, list):
            continue

        normalized_items = [
            str(item).strip().lower()
            for item in items
            if str(item).strip()
        ]

        duplicate_count = len(normalized_items) - len(set(normalized_items))

        if duplicate_count:
            warnings.append(f"{duplicate_count} duplicate {section} entries detected.")

    return warnings
