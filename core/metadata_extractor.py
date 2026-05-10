import re
from urllib.parse import urlparse

from core.section_aliases import (
    is_known_section_heading,
    is_noisy_extraction_artifact,
    is_potential_section_heading,
)


METADATA_FIELDS = (
    "candidate_name",
    "email",
    "phone",
    "linkedin",
    "github",
    "portfolio",
    "location",
)


EMAIL_PATTERN = re.compile(
    r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",
    re.I,
)

PHONE_PATTERN = re.compile(
    r"""
    (?<!\w)
    (?:\+?\d{1,3}[\s().-]*)?
    (?:\d[\s().-]*){10,12}
    (?!\w)
    """,
    re.X,
)

URL_PATTERN = re.compile(
    r"""
    (?:
        https?://
        | www\.
    )?
    (?:
        linkedin\.com/[^\s<>()\[\]{}]+
        | github\.com/[^\s<>()\[\]{}]+
        | [a-z0-9][a-z0-9.-]*\.[a-z]{2,}/[^\s<>()\[\]{}]+
        | (?<!@)\b[a-z0-9][a-z0-9.-]*\.[a-z]{2,}\b
    )
    """,
    re.I | re.X,
)

LOCATION_LABEL_PATTERN = re.compile(
    r"\b(?:location|address|based in|current location)\s*[:|-]\s*(.+)",
    re.I,
)

COMMON_LOCATION_HINTS = {
    "bangalore",
    "bengaluru",
    "mumbai",
    "delhi",
    "new delhi",
    "pune",
    "hyderabad",
    "chennai",
    "kolkata",
    "ahmedabad",
    "noida",
    "gurugram",
    "gurgaon",
    "jaipur",
    "lucknow",
    "india",
    "usa",
    "united states",
    "canada",
    "london",
    "singapore",
    "remote",
}

PORTFOLIO_LABELS = (
    "portfolio",
    "website",
    "personal website",
    "site",
    "homepage",
)

NON_PORTFOLIO_DOMAINS = (
    "linkedin.com",
    "github.com",
    "mailto:",
    "gmail.com",
    "outlook.com",
    "yahoo.com",
    "hotmail.com",
)


def _empty_metadata() -> dict:
    """
    Return stable metadata keys for downstream JSON, ranking, and UI layers.
    """

    return {
        field: ""
        for field in METADATA_FIELDS
    }


def _contact_zone_lines(text: str, max_lines: int = 18) -> list:
    """
    Keep metadata heuristics focused on the top contact area of the resume.

    Contact details almost always appear before the first real section heading.
    Restricting name/location heuristics to this zone reduces false positives
    from project descriptions, school names, and company addresses.
    """

    lines = []

    for raw_line in text.splitlines():
        line = raw_line.strip()

        if is_noisy_extraction_artifact(line):
            continue

        if lines and (
            is_known_section_heading(line)
            or is_potential_section_heading(line)
        ):
            break

        lines.append(line)

        if len(lines) >= max_lines:
            break

    return lines


def _clean_boundary_punctuation(value: str) -> str:
    """
    Remove punctuation commonly attached to regex matches by PDF extraction.
    """

    return value.strip().strip(".,;:|()[]{}<>")


def _split_contact_segments(line: str) -> list:
    """
    Split dense contact lines without losing meaningful comma-separated places.

    Resumes often compress metadata into one row:
    "Bengaluru, India | +91 ... | email@example.com".
    Splitting on strong separators lets each extractor inspect the right piece.
    """

    return [
        segment.strip()
        for segment in re.split(r"\s+(?:[|•·])\s+|\s{2,}", line)
        if segment.strip()
    ]


def normalize_email(email: str) -> str:
    """
    Lowercase and trim an email after regex validation.
    """

    candidate = _clean_boundary_punctuation(email).lower()

    if EMAIL_PATTERN.fullmatch(candidate):
        return candidate

    return ""


def extract_email(text: str) -> str:
    """
    Extract the first valid email address.

    Email is high-precision with regex, so scanning the full resume is safe.
    """

    for match in EMAIL_PATTERN.finditer(text):
        email = normalize_email(match.group(0))

        if email:
            return email

    return ""


def normalize_phone(phone: str) -> str:
    """
    Normalize phone numbers while keeping an optional country code.

    The returned value is digit-focused for consistency. A leading plus is kept
    only when the original candidate clearly included an international prefix.
    """

    candidate = _clean_boundary_punctuation(phone)
    has_plus_prefix = candidate.lstrip().startswith("+")
    digits = re.sub(r"\D", "", candidate)

    # Reject short IDs, years, zip codes, and very long accidental captures.
    if not 10 <= len(digits) <= 15:
        return ""

    if len(set(digits)) <= 2:
        return ""

    if has_plus_prefix:
        return f"+{digits}"

    return digits


def extract_phone(text: str) -> str:
    """
    Extract a plausible phone number from the contact zone first.

    Contact-zone priority prevents project metrics and dates from becoming
    phone numbers. Full-text fallback still helps resumes with unusual layouts.
    """

    search_spaces = [
        "\n".join(_contact_zone_lines(text)),
        text,
    ]

    for search_space in search_spaces:
        for match in PHONE_PATTERN.finditer(search_space):
            phone = normalize_phone(match.group(0))

            if phone:
                return phone

    return ""


def normalize_url(url: str) -> str:
    """
    Normalize web links into explicit HTTPS URLs.
    """

    candidate = _clean_boundary_punctuation(url).lower()
    candidate = re.sub(r"^(?:url|link|website|portfolio)\s*[:|-]\s*", "", candidate)
    candidate = candidate.rstrip("/")

    if not candidate:
        return ""

    if not candidate.startswith(("http://", "https://")):
        candidate = f"https://{candidate}"

    candidate = re.sub(r"^https?://www\.", "https://", candidate)
    parsed_url = urlparse(candidate)

    if not parsed_url.netloc or "." not in parsed_url.netloc:
        return ""

    return candidate


def _iter_normalized_urls(text: str):
    """
    Yield unique normalized URLs while preserving resume order.
    """

    seen_urls = set()

    for match in URL_PATTERN.finditer(text):
        url = normalize_url(match.group(0))

        if not url or url in seen_urls:
            continue

        seen_urls.add(url)
        yield url


def _domain_contains(url: str, domain: str) -> bool:
    parsed_url = urlparse(url)

    return parsed_url.netloc.lower().removeprefix("www.").endswith(domain)


def extract_linkedin(text: str) -> str:
    """
    Extract LinkedIn profile URLs, preferring /in/ profile links.
    """

    for url in _iter_normalized_urls(text):
        parsed_url = urlparse(url)
        path = parsed_url.path.strip("/")

        if (
            _domain_contains(url, "linkedin.com")
            and path.startswith("in/")
            and len(path.split("/")) >= 2
        ):
            return url

    return ""


def extract_github(text: str) -> str:
    """
    Extract GitHub profile URLs while avoiding repository-only deep links.
    """

    for url in _iter_normalized_urls(text):
        parsed_url = urlparse(url)
        path_parts = [
            part for part in parsed_url.path.strip("/").split("/")
            if part
        ]

        if not _domain_contains(url, "github.com"):
            continue

        if len(path_parts) == 1 and re.fullmatch(r"[a-z0-9-]+", path_parts[0], re.I):
            return url

    return ""


def _is_portfolio_url(url: str) -> bool:
    parsed_url = urlparse(url)
    domain = parsed_url.netloc.lower().removeprefix("www.")

    if any(domain.endswith(blocked_domain) for blocked_domain in NON_PORTFOLIO_DOMAINS):
        return False

    return bool(parsed_url.path.strip("/") or domain.endswith("github.io"))


def _is_labeled_portfolio_url(url: str) -> bool:
    parsed_url = urlparse(url)
    domain = parsed_url.netloc.lower().removeprefix("www.")

    return not any(
        domain.endswith(blocked_domain)
        for blocked_domain in NON_PORTFOLIO_DOMAINS
    )


def extract_portfolio(text: str) -> str:
    """
    Extract portfolio/personal website links.

    Labeled portfolio lines are preferred. Otherwise, use the first non-social
    URL that looks like a personal site and not a common email/social domain.
    """

    for line in text.splitlines():
        normalized_line = line.strip().lower()

        if not any(label in normalized_line for label in PORTFOLIO_LABELS):
            continue

        for url in _iter_normalized_urls(line):
            if _is_labeled_portfolio_url(url):
                return url

    for url in _iter_normalized_urls(text):
        if _is_portfolio_url(url):
            return url

    return ""


def _looks_like_location(value: str) -> bool:
    """
    Basic location validation.

    This avoids treating sentences, links, phone numbers, and degree names as
    locations. The heuristic intentionally favors clear city/state/country
    strings over clever but noisy inference.
    """

    candidate = _clean_boundary_punctuation(value)
    lowered_candidate = candidate.lower()

    if not candidate or len(candidate) > 80:
        return False

    if any(marker in lowered_candidate for marker in ("@", "http", "linkedin", "github")):
        return False

    if re.search(r"\d{4,}", candidate):
        return False

    words = re.findall(r"[A-Za-z]+", candidate)

    if not 1 <= len(words) <= 6:
        return False

    if "," in candidate:
        return True

    return any(location_hint in lowered_candidate for location_hint in COMMON_LOCATION_HINTS)


def normalize_location(location: str) -> str:
    """
    Normalize whitespace and separators in a location candidate.
    """

    candidate = _clean_boundary_punctuation(location)
    candidate = re.sub(r"\s+", " ", candidate)
    candidate = re.sub(r"\s*,\s*", ", ", candidate)

    if _looks_like_location(candidate):
        return candidate

    return ""


def extract_location(text: str) -> str:
    """
    Extract a conservative location from labeled lines or contact-zone hints.
    """

    contact_lines = _contact_zone_lines(text)

    for line in contact_lines:
        match = LOCATION_LABEL_PATTERN.search(line)

        if not match:
            continue

        location = normalize_location(match.group(1))

        if location:
            return location

    for line in contact_lines:
        location = normalize_location(line)

        if location:
            return location

        for segment in _split_contact_segments(line):
            location = normalize_location(segment)

            if location:
                return location

    return ""


def _normalize_name_candidate(name: str) -> str:
    """
    Clean and title-case simple candidate names.
    """

    candidate = _clean_boundary_punctuation(name)
    candidate = re.sub(r"\s+", " ", candidate).strip()

    if not candidate:
        return ""

    words = candidate.split()

    if not 2 <= len(words) <= 4:
        return ""

    if any(re.search(r"[^A-Za-z.'-]", word) for word in words):
        return ""

    return " ".join(
        word[:1].upper() + word[1:].lower()
        for word in words
    )


def _is_probable_name(line: str) -> bool:
    """
    Validate candidate names aggressively to avoid contact fields and headings.
    """

    candidate = line.strip()
    lowered_candidate = candidate.lower()

    if not candidate or len(candidate) > 60:
        return False

    if any(marker in lowered_candidate for marker in ("@", "http", "linkedin", "github")):
        return False

    if re.search(r"\d", candidate):
        return False

    if candidate == candidate.lower():
        return False

    if is_known_section_heading(candidate) or is_potential_section_heading(candidate):
        return False

    return bool(_normalize_name_candidate(candidate))


def _name_from_filename(file_name: str) -> str:
    """
    Last-resort name fallback from uploaded filename.
    """

    base_name = re.sub(r"\.[A-Za-z0-9]+$", "", file_name or "")
    base_name = re.sub(r"[_\-]+", " ", base_name)
    base_name = re.sub(r"\b(?:resume|cv|profile)\b", "", base_name, flags=re.I)
    base_name = re.sub(r"\s+", " ", base_name).strip()

    return _normalize_name_candidate(base_name)


def extract_candidate_name(text: str, fallback_name: str = "") -> str:
    """
    Extract a candidate name from the resume header.

    Most resumes place the candidate name in the first few non-noisy lines.
    We scan only the contact zone and reject headings, links, emails, phones,
    and digit-heavy lines to keep precision high.
    """

    for line in _contact_zone_lines(text, max_lines=8):
        if _is_probable_name(line):
            return _normalize_name_candidate(line)

    return _name_from_filename(fallback_name)


def extract_candidate_metadata(text: str, fallback_name: str = "") -> dict:
    """
    Build a structured metadata object from resume text.

    Regex handles high-confidence entities such as email, phone, and URLs.
    Heuristics handle ambiguous fields like name and location with conservative
    contact-zone rules to reduce false positives before embeddings/retrieval.
    """

    metadata = _empty_metadata()

    metadata["candidate_name"] = extract_candidate_name(text, fallback_name)
    metadata["email"] = extract_email(text)
    metadata["phone"] = extract_phone(text)
    metadata["linkedin"] = extract_linkedin(text)
    metadata["github"] = extract_github(text)
    metadata["portfolio"] = extract_portfolio(text)
    metadata["location"] = extract_location(text)

    return metadata
