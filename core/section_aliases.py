import re


MAX_HEADING_WORDS = 8
MIN_DECORATED_HEADING_CONFIDENCE = 2
MIN_UNKNOWN_HEADING_CONFIDENCE = 3


CANONICAL_SECTIONS = (
    "contact_info",
    "professional_summary",
    "skills",
    "projects",
    "experience",
    "education",
    "certifications",
    "achievements",
    "research",
    "leadership",
    "other",
)


# Section naming is resume-author dependent, so the taxonomy lives outside the
# parser. The parser should only ask "what canonical section is this heading?"
# while this module owns the language variants and normalization rules.
SECTION_ALIASES = {
    "contact_info": (
        "contact",
        "contact info",
        "contact information",
        "personal information",
        "personal details",
        "personal profile",
        "candidate profile",
        "candidate details",
        "basic information",
        "basic details",
        "profile details",
        "address",
        "email",
        "phone",
        "mobile",
        "links",
        "social links",
        "online profiles",
        "portfolio",
        "portfolio links",
        "linkedin",
        "github",
    ),
    "professional_summary": (
        "summary",
        "professional summary",
        "career summary",
        "career profile",
        "profile",
        "professional profile",
        "executive summary",
        "candidate summary",
        "personal summary",
        "about",
        "about me",
        "objective",
        "career objective",
        "professional objective",
        "resume objective",
        "statement of purpose",
        "introduction",
        "overview",
        "professional overview",
        "career highlights",
        "summary of qualifications",
        "qualifications summary",
    ),
    "skills": (
        "skills",
        "technical skills",
        "tech skills",
        "technology skills",
        "technical expertise",
        "expertise",
        "areas of expertise",
        "core competencies",
        "competencies",
        "key competencies",
        "professional competencies",
        "technical competencies",
        "proficiencies",
        "technical proficiencies",
        "skills summary",
        "skill set",
        "technical skill set",
        "tech stack",
        "technology stack",
        "tools",
        "tools and technologies",
        "tools & technologies",
        "technologies",
        "frameworks",
        "libraries",
        "platforms",
        "software",
        "software skills",
        "programming skills",
        "programming languages",
        "languages",
        "developer tools",
        "data skills",
        "analytical skills",
        "machine learning skills",
        "ai skills",
        "cloud skills",
        "databases",
        "database skills",
        "operating systems",
        "methodologies",
    ),
    "projects": (
        "projects",
        "project experience",
        "academic projects",
        "personal projects",
        "professional projects",
        "technical projects",
        "key projects",
        "selected projects",
        "major projects",
        "featured projects",
        "relevant projects",
        "course projects",
        "capstone project",
        "capstone projects",
        "portfolio projects",
        "project portfolio",
        "project work",
        "academic work",
        "academic & applied projects",
        "academic and applied projects",
        "case studies",
        "applications built",
        "open source projects",
        "github projects",
    ),
    "experience": (
        "experience",
        "work experience",
        "professional experience",
        "employment history",
        "work history",
        "career history",
        "professional history",
        "industry experience",
        "relevant experience",
        "internship",
        "internships",
        "internship experience",
        "industrial training",
        "training experience",
        "apprenticeship",
        "apprenticeships",
        "roles",
        "positions held",
        "previous roles",
        "employment",
        "work",
        "professional background",
        "career experience",
        "volunteer experience",
        "freelance experience",
        "consulting experience",
    ),
    "education": (
        "education",
        "educational background",
        "academic background",
        "academic history",
        "academics",
        "academic profile",
        "education background",
        "education details",
        "educational details",
        "qualifications",
        "academic qualifications",
        "educational qualifications",
        "degrees",
        "degree",
        "college",
        "university",
        "schooling",
        "training",
        "coursework",
        "relevant coursework",
        "courses",
        "related coursework",
        "academic coursework",
        "scholastic record",
    ),
    "certifications": (
        "certifications",
        "certification",
        "certificates",
        "certificates and licenses",
        "certifications and licenses",
        "licenses",
        "licences",
        "licenses and certifications",
        "professional certifications",
        "technical certifications",
        "online certifications",
        "courses and certifications",
        "certified courses",
        "credentials",
        "professional credentials",
        "badges",
        "digital badges",
        "training certificates",
        "completed courses",
        "workshops",
        "workshops and certifications",
    ),
    "achievements": (
        "achievements",
        "achievement",
        "accomplishments",
        "awards",
        "honors",
        "honours",
        "awards and honors",
        "awards & honors",
        "awards and achievements",
        "recognition",
        "recognitions",
        "key achievements",
        "notable achievements",
        "professional achievements",
        "academic achievements",
        "highlights",
        "career achievements",
        "distinctions",
        "scholarships",
        "scholarship",
        "merits",
        "rankings",
        "publications and awards",
    ),
    "research": (
        "research",
        "research experience",
        "research work",
        "research projects",
        "research papers",
        "publications",
        "publication",
        "papers",
        "published work",
        "journal publications",
        "conference publications",
        "conference papers",
        "patents",
        "patent",
        "thesis",
        "dissertation",
        "academic research",
        "research interests",
        "areas of research",
        "presentations",
        "poster presentations",
        "technical writing",
        "white papers",
    ),
    "leadership": (
        "leadership",
        "leadership experience",
        "leadership roles",
        "positions of responsibility",
        "position of responsibility",
        "responsibilities",
        "roles and responsibilities",
        "team leadership",
        "community leadership",
        "student leadership",
        "campus involvement",
        "extracurricular activities",
        "extra curricular activities",
        "extracurriculars",
        "volunteering",
        "volunteer work",
        "volunteer leadership",
        "clubs",
        "societies",
        "committees",
        "event management",
        "mentoring",
        "mentorship",
    ),
    "other": (
        "other",
        "additional information",
        "additional details",
        "additional",
        "miscellaneous",
        "misc",
        "interests",
        "hobbies",
        "personal interests",
        "activities",
        "languages known",
        "language proficiency",
        "references",
        "declaration",
        "availability",
        "personal statement",
        "appendix",
        "notes",
    ),
}


def _normalize_alias(value: str) -> str:
    """
    Normalize headings and aliases into the same comparison format.

    This intentionally removes punctuation and connector differences so
    "Tools & Technologies", "Tools and Technologies:", and "tools/technologies"
    can resolve to the same canonical section.
    """

    value = value.casefold().strip()
    value = value.replace("&", " and ")
    value = re.sub(r"[/|+_-]", " ", value)
    value = re.sub(r"[^a-z0-9\s]", " ", value)
    value = re.sub(r"\s+", " ", value)

    return value.strip()


NORMALIZED_SECTION_ALIASES = {
    canonical_section: tuple(
        sorted({_normalize_alias(alias) for alias in aliases})
    )
    for canonical_section, aliases in SECTION_ALIASES.items()
}


ALIAS_TO_CANONICAL_SECTION = {
    alias: canonical_section
    for canonical_section, aliases in NORMALIZED_SECTION_ALIASES.items()
    for alias in aliases
}


def strip_heading_decoration(line: str) -> str:
    """
    Remove visual heading markers while preserving the candidate title text.

    Resumes often use PDF/layout artifacts around headings:
    "=== SKILLS ===", "# EDUCATION", "[PROJECTS]", or "TECH STACK |".
    This helper strips only boundary decoration. It does not remove words from
    the middle of a line, which helps prevent content sentences from being
    rewritten into accidental headings.
    """

    candidate = line.strip()

    # Markdown-style prefixes and quote markers sometimes survive PDF extract.
    candidate = re.sub(r"^(?:[#>]+\s*)+", "", candidate)

    # Repeated visual rulers around headings.
    candidate = re.sub(r"^[\s=*_~|:-]+", "", candidate)
    candidate = re.sub(r"[\s=*_~|:-]+$", "", candidate)
    candidate = candidate.strip()

    # Whole-heading wrappers. Apply repeatedly for cases like "[# SKILLS:]".
    previous_candidate = None
    while candidate and candidate != previous_candidate:
        previous_candidate = candidate
        candidate = re.sub(
            r"^[\[\(\{<]\s*(.*?)\s*[\]\)\}>]$",
            r"\1",
            candidate
        ).strip()
        candidate = re.sub(r"[\s:|.-]+$", "", candidate).strip()

    return candidate


def get_heading_candidate(line: str) -> str:
    """
    Return the normalized alias candidate extracted from a raw resume line.

    The regex/decorator pass handles formatting. The alias normalizer then
    handles casing, punctuation, connector variants, and spacing.
    """

    return _normalize_alias(strip_heading_decoration(line))


def capitalization_ratio(value: str) -> float:
    """
    Measure how heading-like the capitalization is.

    Uppercase headings are common in resumes, but this is a supporting signal
    rather than a standalone rule because many valid headings are title case.
    """

    letters = [character for character in value if character.isalpha()]

    if not letters:
        return 0.0

    uppercase_letters = [
        character for character in letters
        if character == character.upper()
    ]

    return len(uppercase_letters) / len(letters)


def formatting_density(value: str) -> float:
    """
    Estimate how much of a line is heading decoration.

    A dense ratio of punctuation/separators is a strong hint for lines like
    "=== PROJECTS ===", but only after the cleaned candidate maps to an alias.
    """

    stripped_value = value.strip()

    if not stripped_value:
        return 0.0

    formatting_characters = re.findall(r"[^A-Za-z0-9\s]", stripped_value)

    return len(formatting_characters) / len(stripped_value)


def is_repeated_separator_line(line: str) -> bool:
    """
    Detect visual separators that PDF extraction often emits as standalone text.

    These lines are layout noise, not resume content. Skipping them prevents
    separator bars from polluting semantic chunks and future embeddings.
    """

    return bool(re.fullmatch(r"[\s=*_~|:.\-]{3,}", line.strip()))


def is_noisy_extraction_artifact(line: str) -> bool:
    """
    Detect low-value PDF extraction artifacts.

    This intentionally stays conservative. It skips obvious standalone rulers
    and page markers, while keeping normal resume text untouched.
    """

    stripped_line = line.strip()

    if not stripped_line:
        return True

    if is_repeated_separator_line(stripped_line):
        return True

    if re.fullmatch(r"page\s+\d+(?:\s+of\s+\d+)?", stripped_line, re.I):
        return True

    return False


def heading_confidence(line: str) -> int:
    """
    Score whether a raw line behaves like a resume heading.

    The score is intentionally simple and explainable:
    - short lines are more likely to be headings
    - high capitalization ratio is a useful formatting cue
    - punctuation density catches decorative separators
    - boundary punctuation catches colon/pipe/dash heading styles

    Exact alias matching is still required by ``is_known_section_heading``.
    This score only decides whether the matched alias came from a plausible
    heading line or from noisy resume body text.
    """

    stripped_line = line.strip()
    candidate = strip_heading_decoration(stripped_line)
    normalized_candidate = _normalize_alias(candidate)

    if not normalized_candidate:
        return 0

    words = normalized_candidate.split()
    score = 0

    if len(words) <= MAX_HEADING_WORDS:
        score += 1

    if capitalization_ratio(candidate) >= 0.65:
        score += 1

    if formatting_density(stripped_line) >= 0.15:
        score += 1

    if re.search(r"[:|.-]\s*$", stripped_line):
        score += 1

    if re.search(r"^(?:[#>]+|[=\-_*~|]{2,}|\s*[\[\(\{<])", stripped_line):
        score += 1

    # Plain aliases such as "Education" and "Career Summary" should still be
    # accepted even when they are not uppercase or decorated.
    if normalized_candidate in ALIAS_TO_CANONICAL_SECTION:
        score += 1

    return score


def is_potential_section_heading(line: str) -> bool:
    """
    Identify unknown but heading-like lines for fallback routing.

    Known headings are handled by exact alias matching. This helper is stricter
    and only catches lines that look strongly like section boundaries but are
    not in the alias dictionary yet, such as "PUBLIC SPEAKING:" or
    "=== COMMUNITY WORK ===". Routing those blocks to "other" is safer than
    appending them to the previous canonical section.
    """

    if is_noisy_extraction_artifact(line):
        return False

    candidate = strip_heading_decoration(line)
    normalized_candidate = _normalize_alias(candidate)

    if not normalized_candidate:
        return False

    words = normalized_candidate.split()

    if len(words) > MAX_HEADING_WORDS:
        return False

    if normalized_candidate in ALIAS_TO_CANONICAL_SECTION:
        return True

    has_heading_boundary = bool(
        re.search(r"[:|.-]\s*$", line.strip())
        or re.search(r"^(?:[#>]+|[=\-_*~|]{2,}|\s*[\[\(\{<])", line.strip())
    )
    has_strong_caps = capitalization_ratio(candidate) >= 0.75

    return (
        heading_confidence(line) >= MIN_UNKNOWN_HEADING_CONFIDENCE
        and (has_heading_boundary or has_strong_caps)
    )


def normalize_section_name(section_name: str, default: str = "other") -> str:
    """
    Return the canonical section name for a raw resume heading.

    Unknown headings fall back to ``default`` so callers can decide whether an
    unmatched heading should become "other" or simply be ignored.
    """

    normalized_name = get_heading_candidate(section_name)

    if normalized_name in CANONICAL_SECTIONS:
        return normalized_name

    return ALIAS_TO_CANONICAL_SECTION.get(normalized_name, default)


def is_known_section_heading(line: str) -> bool:
    """
    Check if a line looks like a known resume section heading.

    Keeping this small heuristic near the alias map makes section extraction
    easier to tune as the project grows toward embeddings and ranking.
    """

    if is_noisy_extraction_artifact(line):
        return False

    normalized_line = get_heading_candidate(line)

    if not normalized_line:
        return False

    # Resume headings are usually short. This guard aggressively rejects body
    # text like "Built projects using Python" even though it contains a known
    # section word.
    if len(normalized_line.split()) > MAX_HEADING_WORDS:
        return False

    if normalized_line not in ALIAS_TO_CANONICAL_SECTION:
        return False

    return heading_confidence(line) >= MIN_DECORATED_HEADING_CONFIDENCE
