import re

from core.parsing.section_aliases import CANONICAL_SECTIONS


MIN_TINY_SECTION_CHARS = 18

NARRATIVE_SECTIONS = {
    "projects",
    "experience",
    "research",
    "leadership",
    "achievements",
}


# These patterns are intentionally lightweight. They are not a replacement for
# NLP classification; they are a practical guardrail that repairs obvious
# section bleed before embeddings, FAISS retrieval, and ranking consume chunks.
SEMANTIC_BOUNDARY_PATTERNS = {
    "skills": (
        r"\b(?:python|java|javascript|typescript|sql|fastapi|flask|django)\b",
        r"\b(?:react|node|streamlit|pandas|numpy|pytorch|tensorflow|sklearn)\b",
        r"\b(?:aws|azure|gcp|docker|kubernetes|git|github|linux|faiss)\b",
        r"\b(?:tools?|technologies|frameworks?|libraries|databases?)\b",
    ),
    "projects": (
        r"\b(?:built|developed|created|implemented|designed|deployed)\b",
        r"\b(?:project|application|app|system|platform|chatbot|dashboard|model)\b",
        r"\b(?:github|repository|demo|prototype|capstone)\b",
    ),
    "experience": (
        r"\b(?:intern|internship|engineer|developer|analyst|consultant)\b",
        r"\b(?:worked|collaborated|managed|owned|delivered|improved)\b",
        r"\b(?:company|organization|client|team|role|responsibilities)\b",
    ),
    "education": (
        r"\b(?:b\.?tech|m\.?tech|bachelor|master|degree|university|college)\b",
        r"\b(?:cgpa|gpa|coursework|semester|graduation|school)\b",
    ),
    "certifications": (
        r"\b(?:certified|certification|certificate|coursera|udemy|nptel)\b",
        r"\b(?:credential|license|licence|badge)\b",
    ),
    "achievements": (
        r"\b(?:award|won|winner|ranked|scholarship|honou?r|recognition)\b",
        r"\b(?:achievement|accomplishment|finalist|selected)\b",
    ),
    "research": (
        r"\b(?:research|paper|publication|published|journal|conference)\b",
        r"\b(?:thesis|dissertation|patent|experiment|study)\b",
    ),
    "leadership": (
        r"\b(?:led|lead|organized|coordinated|mentored|volunteer)\b",
        r"\b(?:club|committee|society|event|leadership|responsibility)\b",
    ),
}


def word_count(text: str) -> int:
    return len(re.findall(r"[A-Za-z0-9]+", text))


def looks_like_sentence(line: str) -> bool:
    """
    Detect prose-like lines that can bleed into terse sections such as skills.
    """

    words = word_count(line)

    if words >= 8:
        return True

    return bool(re.search(
        r"\b(?:built|developed|implemented|worked|managed|led|deployed|created)\b",
        line,
        re.I
    ))


def semantic_section_hint(line: str) -> str:
    """
    Infer a weak semantic section for a content line.

    The parser still trusts explicit headings first. These hints only repair
    common boundary issues, such as skills sections swallowing project prose or
    malformed transitions sending education/certification lines to "other".
    """

    normalized_line = line.lower()
    scores = {}

    for section_name, patterns in SEMANTIC_BOUNDARY_PATTERNS.items():
        score = sum(
            1
            for pattern in patterns
            if re.search(pattern, normalized_line, re.I)
        )

        if score:
            scores[section_name] = score

    if not scores:
        return ""

    return max(scores, key=scores.get)


def looks_like_skill_list(line: str) -> bool:
    """
    Detect dense technology lists from compressed PDF layouts.
    """

    if re.search(r"[,|/]", line) and word_count(line) <= 16:
        return True

    return semantic_section_hint(line) == "skills"


def resolve_content_section(current_section: str,
                            previous_content_section: str,
                            line: str) -> str:
    """
    Decide where a content line belongs after heading-based parsing.

    Heading detection gives the primary boundary. This function is a defensive
    semantic guardrail for broken PDFs and compressed layouts. It prevents
    obvious semantic drift from corrupting a high-value section before NLP
    fallback, embeddings, FAISS retrieval, or explainable scoring consume it.
    """

    semantic_hint = semantic_section_hint(line)

    if current_section == "skills":
        if looks_like_skill_list(line):
            return current_section

        if (
            previous_content_section in NARRATIVE_SECTIONS
            and looks_like_sentence(line)
        ):
            return previous_content_section

    if current_section == "other" and semantic_hint in CANONICAL_SECTIONS:
        return semantic_hint

    if (
        semantic_hint
        and semantic_hint != current_section
        and current_section in {"contact_info", "other"}
    ):
        return semantic_hint

    return current_section


def merge_tiny_low_signal_sections(sections: dict) -> dict:
    """
    Avoid isolated tiny chunks created by noisy or malformed transitions.

    Tiny content can be harmful for retrieval: a one-token section creates a
    low-context embedding that may rank for the wrong reason. We keep meaningful
    tiny sections such as short skill lists, but route low-signal fragments to
    "other" where NLP fallback can inspect them later.
    """

    cleaned_sections = {
        section_name: list(lines)
        for section_name, lines in sections.items()
    }

    for section_name in CANONICAL_SECTIONS:
        if section_name in {"contact_info", "skills", "other"}:
            continue

        content = "\n".join(cleaned_sections.get(section_name, [])).strip()

        if not content:
            continue

        if len(content) >= MIN_TINY_SECTION_CHARS or word_count(content) >= 3:
            continue

        cleaned_sections["other"].extend(cleaned_sections[section_name])
        cleaned_sections[section_name] = []

    return cleaned_sections
