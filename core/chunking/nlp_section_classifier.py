from functools import lru_cache

from core.parsing.section_aliases import (
    CANONICAL_SECTIONS,
    is_known_section_heading,
)
from core.chunking.semantic_boundary import (
    semantic_section_hint,
    word_count,
)


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
# MiniLM cosine scores for short resume fragments are often modest. A compact
# phrase like "Python FastAPI PyTorch" can be semantically correct even when
# the absolute score is around 0.20-0.35. The margin between top sections is
# therefore as important as the raw score. Thresholds stay conservative because
# rule-based parsing remains primary and NLP only repairs ambiguous content.
MIN_CLASSIFICATION_CONFIDENCE = 0.20
MIN_CLASSIFICATION_MARGIN = 0.025
MIN_REPAIR_CONFIDENCE = 0.26
MIN_DISAGREEMENT_CONFIDENCE = 0.34
MAX_OTHER_WORD_RATIO = 0.12
_TEXT_EMBEDDING_CACHE = {}


# Prototype descriptions are intentionally short, human-readable, and resume-
# shaped. MiniLM performs better when prototypes include both section meaning
# and realistic keywords/tools that appear in compressed resume lines.
SECTION_PROTOTYPES = {
    "contact_info": (
        "Contact information email phone mobile address location LinkedIn "
        "GitHub portfolio website personal links candidate details"
    ),
    "professional_summary": (
        "Professional summary career objective profile overview motivated "
        "software engineer data analyst AI developer with experience in "
        "Python projects internships problem solving"
    ),
    "skills": (
        "Technical skills programming languages frameworks tools technologies "
        "Python Java JavaScript FastAPI Django React PyTorch TensorFlow SQL "
        "Docker Git APIs cloud AWS Azure databases machine learning"
    ),
    "projects": (
        "Projects applications built developed implemented deployed AI chatbot "
        "dashboard web app machine learning model resume parser API system "
        "GitHub repository capstone project outcomes"
    ),
    "experience": (
        "Work experience internship professional experience software developer "
        "engineer analyst company role responsibilities collaborated delivered "
        "improved managed production client team"
    ),
    "education": (
        "Education degree university college school BTech MTech Bachelor Master "
        "Computer Science coursework CGPA GPA academic qualifications "
        "graduation relevant courses"
    ),
    "certifications": (
        "Certifications certificates credentials licenses online courses "
        "Coursera Udemy NPTEL AWS Azure Google certified badge professional "
        "training completed course"
    ),
    "achievements": (
        "Achievements awards honors accomplishments winner ranked scholarship "
        "recognition finalist selected hackathon prize academic achievement "
        "professional achievement"
    ),
    "research": (
        "Research publications paper journal conference thesis dissertation "
        "patent academic research experiment study published work poster "
        "technical writing"
    ),
    "leadership": (
        "Leadership positions of responsibility led organized coordinated "
        "mentored volunteered club committee society event team management "
        "campus ambassador community work"
    ),
    "other": (
        "Additional information hobbies interests languages declaration "
        "miscellaneous personal details activities references availability"
    ),
}


def _empty_validation_report(reason: str, nlp_available: bool = False) -> dict:
    return {
        "activated": False,
        "nlp_available": nlp_available,
        "reason": reason,
        "quality": {},
        "repairs": [],
        "disagreements": [],
        "section_confidence": [],
        "summary": {},
    }


def _get_sentence_transformer_class():
    """
    Import Sentence Transformers lazily.

    Rule-based parsing is the primary parser and should stay usable even when
    the optional NLP dependency or model files are not available locally.
    """

    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        return None

    return SentenceTransformer


@lru_cache(maxsize=1)
def _load_model():
    sentence_transformer = _get_sentence_transformer_class()

    if sentence_transformer is None:
        return None

    return sentence_transformer(MODEL_NAME)


def _cosine_similarity(vector_a, vector_b) -> float:
    """
    Compute cosine similarity without adding another dependency.
    """

    dot_product = sum(a * b for a, b in zip(vector_a, vector_b))
    norm_a = sum(a * a for a in vector_a) ** 0.5
    norm_b = sum(b * b for b in vector_b) ** 0.5

    if not norm_a or not norm_b:
        return 0.0

    return dot_product / (norm_a * norm_b)


@lru_cache(maxsize=1)
def _prototype_embeddings():
    model = _load_model()

    if model is None:
        return {}

    section_names = tuple(SECTION_PROTOTYPES.keys())
    prototype_texts = [SECTION_PROTOTYPES[name] for name in section_names]
    embeddings = model.encode(prototype_texts, normalize_embeddings=True)

    return {
        section_name: embedding
        for section_name, embedding in zip(section_names, embeddings)
    }


def _text_cache_key(text: str) -> str:
    return " ".join(text.split()).strip().lower()


def _encode_texts_batch(texts: list) -> dict:
    """
    Encode multiple text blocks in one model call.

    Sentence Transformer inference has fixed overhead. Batching repair blocks
    and disagreement candidates avoids repeated ``model.encode`` calls inside
    loops, which matters when processing many resumes or many small fallback
    lines before later FAISS indexing.
    """

    model = _load_model()

    if model is None:
        return {}

    unique_texts = []
    unique_keys = set()

    for text in texts:
        if word_count(text) < 2:
            continue

        cache_key = _text_cache_key(text)

        if not cache_key or cache_key in _TEXT_EMBEDDING_CACHE:
            continue

        if cache_key not in unique_keys:
            unique_keys.add(cache_key)
            unique_texts.append(text)

    if unique_texts:
        embeddings = model.encode(unique_texts, normalize_embeddings=True)

        for text, embedding in zip(unique_texts, embeddings):
            _TEXT_EMBEDDING_CACHE[_text_cache_key(text)] = embedding

    return {
        text: _TEXT_EMBEDDING_CACHE[_text_cache_key(text)]
        for text in texts
        if _text_cache_key(text) in _TEXT_EMBEDDING_CACHE
    }


def _split_repair_blocks(text: str) -> list:
    """
    Split ambiguous content into small semantic blocks.

    Blocks are line-based for explainability. This keeps repairs conservative:
    the NLP layer moves only the lines it can classify confidently.
    """

    return [
        line.strip()
        for line in text.splitlines()
        if line.strip() and word_count(line) >= 2
    ]


def _section_word_count(sections: dict, section_name: str) -> int:
    return word_count(sections.get(section_name, ""))


def _count_rule_semantic_disagreements(sections: dict) -> int:
    """
    Count obvious rule-level semantic drift before loading NLP.

    This uses the lightweight regex hints from ``semantic_boundary`` only as a
    quality signal. It deliberately ignores professional summaries because they
    often mention skills, projects, and internships in one short paragraph.
    """

    disagreement_count = 0

    for section_name, content in sections.items():
        if section_name in {"contact_info", "professional_summary", "other"}:
            continue

        checked_lines = [
            line.strip()
            for line in content.splitlines()
            if word_count(line) >= 4
        ]

        if not checked_lines:
            continue

        line_disagreements = 0

        for line in checked_lines:
            hinted_section = semantic_section_hint(line)

            if hinted_section and hinted_section != section_name:
                line_disagreements += 1

        if line_disagreements >= 2:
            disagreement_count += 1

    return disagreement_count


def evaluate_parsing_quality(sections: dict, raw_text: str = "") -> dict:
    """
    Score whether the deterministic parser output needs NLP validation.

    This check is intentionally rule-based. We avoid loading the NLP model when
    explicit headings, low fallback content, and stable section structure already
    indicate high chunk purity.
    """

    total_words = sum(word_count(content) for content in sections.values())
    other_words = _section_word_count(sections, "other")
    other_ratio = other_words / total_words if total_words else 0.0
    populated_sections = [
        section_name
        for section_name, content in sections.items()
        if section_name not in {"contact_info", "other"} and word_count(content) >= 3
    ]
    tiny_sections = [
        section_name
        for section_name, content in sections.items()
        if section_name not in {"contact_info", "other"} and 0 < word_count(content) < 3
    ]
    known_heading_count = sum(
        1
        for line in raw_text.splitlines()
        if is_known_section_heading(line.strip())
    )
    possible_semantic_disagreements = _count_rule_semantic_disagreements(sections)

    needs_validation = (
        other_ratio > MAX_OTHER_WORD_RATIO
        or known_heading_count < 2
        or len(populated_sections) < 2
        or len(tiny_sections) >= 2
        or possible_semantic_disagreements > 0
    )

    return {
        "total_words": total_words,
        "other_words": other_words,
        "other_ratio": round(other_ratio, 3),
        "known_heading_count": known_heading_count,
        "populated_sections": populated_sections,
        "tiny_sections": tiny_sections,
        "possible_semantic_disagreements": possible_semantic_disagreements,
        "needs_nlp_validation": needs_validation,
    }


def should_run_nlp_validation(sections: dict, raw_text: str = "") -> bool:
    """
    Return True only when rule-based parsing looks uncertain.
    """

    return evaluate_parsing_quality(
        sections=sections,
        raw_text=raw_text
    )["needs_nlp_validation"]


def compute_section_similarities(texts: list) -> dict:
    """
    Compare many texts with every section prototype using batched embeddings.
    """

    prototypes = _prototype_embeddings()

    if not prototypes:
        return {}

    text_embeddings = _encode_texts_batch(texts)
    similarity_results = {}

    for text, text_embedding in text_embeddings.items():
        similarity_results[text] = {
            section_name: round(
                _cosine_similarity(text_embedding, prototype_embedding),
                4
            )
            for section_name, prototype_embedding in prototypes.items()
        }

    return similarity_results


def compute_section_similarity(text: str) -> dict:
    """
    Compare one text block with every section prototype.

    Kept as a public convenience wrapper; internally it uses the same batched
    path as larger validation workflows.
    """

    return compute_section_similarities([text]).get(text, {})


def _classification_from_scores(scores: dict,
                                min_confidence: float,
                                min_margin: float) -> dict:
    if not scores:
        return {
            "section": "other",
            "confidence": 0.0,
            "margin": 0.0,
            "scores": {},
            "reason": "nlp_unavailable_or_too_short",
        }

    ranked_scores = sorted(
        scores.items(),
        key=lambda item: item[1],
        reverse=True
    )
    best_section, best_score = ranked_scores[0]
    second_score = ranked_scores[1][1] if len(ranked_scores) > 1 else 0.0
    margin = best_score - second_score
    top_scores = [
        {
            "section": section_name,
            "score": score,
        }
        for section_name, score in ranked_scores[:5]
    ]

    if best_score < min_confidence or margin < min_margin:
        return {
            "section": "other",
            "confidence": best_score,
            "margin": round(margin, 4),
            "scores": scores,
            "top_scores": top_scores,
            "reason": "low_confidence_or_margin",
        }

    return {
        "section": best_section,
        "confidence": best_score,
        "margin": round(margin, 4),
        "scores": scores,
        "top_scores": top_scores,
        "reason": "classified",
    }


def explain_similarity_distribution(text: str, top_k: int = 5) -> dict:
    """
    Return raw similarity scores for calibration/debugging.

    MiniLM cosine values for short, keyword-heavy resume text are usually much
    lower than people expect from normalized scores. This helper makes the
    distribution visible so calibration can focus on ranking and margin, not
    only an absolute threshold.
    """

    scores = compute_section_similarity(text)
    ranked_scores = sorted(
        scores.items(),
        key=lambda item: item[1],
        reverse=True
    )
    classification = _classification_from_scores(
        scores,
        min_confidence=MIN_CLASSIFICATION_CONFIDENCE,
        min_margin=MIN_CLASSIFICATION_MARGIN
    )

    return {
        "text": text,
        "predicted_section": classification["section"],
        "confidence": classification["confidence"],
        "margin": classification["margin"],
        "reason": classification["reason"],
        "top_scores": [
            {
                "section": section_name,
                "score": score,
            }
            for section_name, score in ranked_scores[:top_k]
        ],
        "all_scores": scores,
    }


def classify_text_sections(texts: list,
                           min_confidence: float = MIN_CLASSIFICATION_CONFIDENCE,
                           min_margin: float = MIN_CLASSIFICATION_MARGIN) -> dict:
    """
    Classify many text blocks with one batched embedding pass.
    """

    similarities = compute_section_similarities(texts)

    return {
        text: _classification_from_scores(
            similarities.get(text, {}),
            min_confidence=min_confidence,
            min_margin=min_margin
        )
        for text in texts
    }


def classify_text_section(text: str,
                          min_confidence: float = MIN_CLASSIFICATION_CONFIDENCE,
                          min_margin: float = MIN_CLASSIFICATION_MARGIN) -> dict:
    """
    Infer the most likely canonical section for a text block.

    Low confidence or low margin returns "other". This prevents the NLP layer
    from aggressively overriding deterministic parsing on fuzzy text.
    """

    return classify_text_sections(
        [text],
        min_confidence=min_confidence,
        min_margin=min_margin
    )[text]


def validate_section_assignment(rule_section: str, text: str) -> dict:
    """
    Compare deterministic section assignment against NLP inference.

    Agreement is informational for strong rule sections. Disagreement becomes a
    repair signal only when confidence is high and the section is ambiguous.
    """

    classification = classify_text_section(text)
    return _build_assignment_validation(rule_section, classification)


def _build_assignment_validation(rule_section: str, classification: dict) -> dict:
    nlp_section = classification["section"]
    confidence = classification["confidence"]
    agreement = (
        nlp_section == "other"
        or nlp_section == rule_section
        or confidence < MIN_DISAGREEMENT_CONFIDENCE
    )

    return {
        "rule_section": rule_section,
        "nlp_section": nlp_section,
        "agreement": agreement,
        "confidence": confidence,
        "margin": classification["margin"],
        "reason": classification["reason"],
    }


def validate_section_assignments(assignments: list) -> list:
    """
    Validate many rule assignments in one batched NLP pass.

    ``assignments`` should contain ``(rule_section, text)`` tuples. This is used
    for section-level disagreement checks and keeps validation scalable for
    multi-resume processing.
    """

    texts = [text for _, text in assignments]
    classifications = classify_text_sections(texts)

    return [
        _build_assignment_validation(
            rule_section,
            classifications.get(text, {})
        )
        for rule_section, text in assignments
    ]


def detect_semantic_disagreement(sections: dict) -> list:
    """
    Detect high-confidence NLP disagreements for existing sections.
    """

    assignments = []

    for section_name, content in sections.items():
        if section_name in {"contact_info", "other"} or word_count(content) < 4:
            continue

        assignments.append((section_name, content))

    validations = validate_section_assignments(assignments)

    return [
        validation
        for validation in validations
        if not validation["agreement"]
    ]


def repair_ambiguous_section(section_name: str, content: str) -> tuple:
    """
    Repair ambiguous or fallback section content conservatively.

    Only lines with high-confidence section matches are moved. Everything else
    remains in the original section, usually "other".
    """

    repaired_blocks = {}
    remaining_blocks = []

    blocks = _split_repair_blocks(content)
    classifications = classify_text_sections(
        blocks,
        min_confidence=MIN_REPAIR_CONFIDENCE,
        min_margin=MIN_CLASSIFICATION_MARGIN,
    )

    for block in blocks:
        classification = classifications.get(block, {})
        target_section = classification["section"]

        if (
            target_section in CANONICAL_SECTIONS
            and target_section not in {"contact_info", "other", section_name}
            and classification["confidence"] >= MIN_REPAIR_CONFIDENCE
        ):
            repaired_blocks.setdefault(target_section, []).append({
                "text": block,
                "confidence": classification["confidence"],
                "margin": classification["margin"],
            })
        else:
            remaining_blocks.append(block)

    return repaired_blocks, "\n".join(remaining_blocks).strip()


def compute_rule_confidence(section_name: str,
                            content: str,
                            quality: dict) -> float:
    """
    Estimate deterministic-parser confidence for explainability.

    This is not a statistical model. It is a transparent score based on section
    signal strength, fallback ratio, and rule/heuristic consistency. Recruiters
    and developers can inspect it to understand why a section was trusted.
    """

    if not content:
        return 0.0

    if section_name == "other":
        return 0.25

    score = 0.72

    if section_name in quality.get("populated_sections", []):
        score += 0.12

    if quality.get("known_heading_count", 0) >= 2:
        score += 0.06

    if quality.get("other_ratio", 0.0) <= MAX_OTHER_WORD_RATIO:
        score += 0.05

    hinted_section = semantic_section_hint(content)

    if hinted_section == section_name:
        score += 0.05
    elif hinted_section and hinted_section != section_name:
        score -= 0.15

    if section_name in quality.get("tiny_sections", []):
        score -= 0.2

    return round(max(0.0, min(score, 0.98)), 2)


def _repair_targets_by_section(repairs: list) -> dict:
    repair_targets = {}

    for repair in repairs:
        for block in repair.get("blocks", []):
            repair_targets.setdefault(repair["to"], []).append(block)

    return repair_targets


def build_section_confidence_report(original_sections: dict,
                                    final_sections: dict,
                                    quality: dict,
                                    repairs: list,
                                    disagreements: list) -> list:
    """
    Build explainable section-level confidence metadata.

    This improves recruiter trust and debugging visibility: each section shows
    whether the deterministic parser and NLP agreed, whether repair happened,
    and what confidence the final assignment carries before ranking.
    """

    confidence_report = []
    repair_targets = _repair_targets_by_section(repairs)
    disagreement_by_rule_section = {
        disagreement["rule_section"]: disagreement
        for disagreement in disagreements
    }
    validation_assignments = [
        (section_name, content)
        for section_name, content in final_sections.items()
        if section_name not in {"contact_info", "other"} and word_count(content) >= 4
    ]
    validations = {
        validation["rule_section"]: validation
        for validation in validate_section_assignments(validation_assignments)
    }

    for section_name in CANONICAL_SECTIONS:
        content = final_sections.get(section_name, "")
        rule_confidence = compute_rule_confidence(
            section_name=section_name,
            content=content,
            quality=quality
        )
        validation = validations.get(section_name, {})
        disagreement = disagreement_by_rule_section.get(section_name)
        repaired_blocks = repair_targets.get(section_name, [])
        nlp_section = validation.get("nlp_section", "")
        nlp_confidence = validation.get("confidence", 0.0)
        repair_applied = bool(repaired_blocks)
        agreement = validation.get("agreement", True)

        if disagreement:
            agreement = False
            nlp_section = disagreement["nlp_section"]
            nlp_confidence = disagreement["confidence"]

        confidence_report.append({
            "final_section": section_name,
            "rule_section": section_name,
            "nlp_section": nlp_section,
            "rule_confidence": rule_confidence,
            "nlp_confidence": round(nlp_confidence, 2),
            "agreement": agreement,
            "repair_applied": repair_applied,
            "repaired_blocks": len(repaired_blocks),
            "word_count": word_count(content),
        })

    return confidence_report


def build_rule_only_section_confidence_report(sections: dict,
                                              quality: dict) -> list:
    """
    Build confidence metadata without loading NLP.

    Clean resumes should skip NLP, but still deserve an explainable report for
    debugging and future ranking features.
    """

    return [
        {
            "final_section": section_name,
            "rule_section": section_name,
            "nlp_section": "",
            "rule_confidence": compute_rule_confidence(
                section_name=section_name,
                content=sections.get(section_name, ""),
                quality=quality
            ),
            "nlp_confidence": 0.0,
            "agreement": True,
            "repair_applied": False,
            "repaired_blocks": 0,
            "word_count": word_count(sections.get(section_name, "")),
        }
        for section_name in CANONICAL_SECTIONS
    ]


def build_validation_summary(report: dict) -> dict:
    """
    Summarize validation outcomes for UI/debug consumption.
    """

    section_confidence = report.get("section_confidence", [])
    populated_confidence = [
        item
        for item in section_confidence
        if item.get("word_count", 0) > 0
    ]
    average_rule_confidence = (
        sum(item["rule_confidence"] for item in populated_confidence)
        / len(populated_confidence)
        if populated_confidence else 0.0
    )
    average_nlp_confidence = (
        sum(item["nlp_confidence"] for item in populated_confidence)
        / len(populated_confidence)
        if populated_confidence else 0.0
    )

    return {
        "activated": report.get("activated", False),
        "reason": report.get("reason", ""),
        "total_repairs": sum(
            len(repair.get("blocks", []))
            for repair in report.get("repairs", [])
        ),
        "disagreement_count": len(report.get("disagreements", [])),
        "average_rule_confidence": round(average_rule_confidence, 2),
        "average_nlp_confidence": round(average_nlp_confidence, 2),
    }


def classify_other_sections(sections: dict) -> tuple:
    """
    Classify fallback content from "other" into canonical sections when safe.
    """

    repaired_sections = {
        section_name: content
        for section_name, content in sections.items()
    }
    repairs = []
    other_content = repaired_sections.get("other", "")

    if not other_content:
        return repaired_sections, repairs

    repaired_blocks, remaining_other = repair_ambiguous_section(
        section_name="other",
        content=other_content
    )

    for target_section, blocks in repaired_blocks.items():
        moved_text = "\n".join(block["text"] for block in blocks)
        existing_content = repaired_sections.get(target_section, "")
        repaired_sections[target_section] = "\n".join(
            part for part in (existing_content, moved_text) if part
        ).strip()
        repairs.append({
            "from": "other",
            "to": target_section,
            "blocks": blocks,
        })

    repaired_sections["other"] = remaining_other

    return repaired_sections, repairs


def validate_and_repair_sections(sections: dict,
                                 raw_text: str = "",
                                 force: bool = False) -> tuple:
    """
    Run the hybrid NLP validation layer only when parsing quality needs it.

    Returns ``(sections, report)`` so the existing resume object can keep using
    the same ``sections`` key while optionally exposing validation diagnostics.
    """

    quality = evaluate_parsing_quality(sections, raw_text)

    if not force and not quality["needs_nlp_validation"]:
        report = _empty_validation_report(
            reason="rule_based_parsing_quality_is_strong",
            nlp_available=_get_sentence_transformer_class() is not None
        )
        report["quality"] = quality
        report["section_confidence"] = build_rule_only_section_confidence_report(
            sections,
            quality
        )
        report["summary"] = build_validation_summary(report)
        return sections, report

    if _get_sentence_transformer_class() is None:
        report = _empty_validation_report(
            reason="sentence_transformers_not_installed",
            nlp_available=False
        )
        report["quality"] = quality
        report["section_confidence"] = build_rule_only_section_confidence_report(
            sections,
            quality
        )
        report["summary"] = build_validation_summary(report)
        return sections, report

    # Loading the model happens here, after the quality gate. This keeps the
    # deterministic parser primary and avoids model startup cost for clean
    # resumes.
    model = _load_model()

    if model is None:
        report = _empty_validation_report(
            reason="sentence_transformer_model_unavailable",
            nlp_available=False
        )
        report["quality"] = quality
        report["section_confidence"] = build_rule_only_section_confidence_report(
            sections,
            quality
        )
        report["summary"] = build_validation_summary(report)
        return sections, report

    repaired_sections, repairs = classify_other_sections(sections)
    disagreements = detect_semantic_disagreement(repaired_sections)

    report = {
        "activated": True,
        "nlp_available": True,
        "reason": "quality_gate_requested_validation",
        "quality": quality,
        "repairs": repairs,
        "disagreements": disagreements,
    }
    report["section_confidence"] = build_section_confidence_report(
        original_sections=sections,
        final_sections=repaired_sections,
        quality=quality,
        repairs=repairs,
        disagreements=disagreements
    )
    report["summary"] = build_validation_summary(report)

    return repaired_sections, report
