from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List


@dataclass(frozen=True)
class LinkedInExperience:
    title: str = ""
    company: str = ""
    start_date: str = ""
    end_date: str = ""
    location: str = ""
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class LinkedInEducation:
    school: str = ""
    degree: str = ""
    field_of_study: str = ""
    start_date: str = ""
    end_date: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class LinkedInCertification:
    name: str = ""
    issuer: str = ""
    issue_date: str = ""
    credential_id: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class LinkedInSkill:
    name: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class LinkedInProfile:
    name: str = ""
    headline: str = ""
    summary: str = ""
    skills: List[LinkedInSkill] = field(default_factory=list)
    experience: List[LinkedInExperience] = field(default_factory=list)
    education: List[LinkedInEducation] = field(default_factory=list)
    certifications: List[LinkedInCertification] = field(default_factory=list)
    projects: List[str] = field(default_factory=list)
    location: str = ""
    linkedin_url: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "headline": self.headline,
            "summary": self.summary,
            "skills": [skill.to_dict() for skill in self.skills],
            "experience": [item.to_dict() for item in self.experience],
            "education": [item.to_dict() for item in self.education],
            "certifications": [item.to_dict() for item in self.certifications],
            "projects": list(self.projects),
            "location": self.location,
            "linkedin_url": self.linkedin_url,
        }
