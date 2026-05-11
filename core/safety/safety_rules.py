FORBIDDEN_CLAIM_PATTERNS = (
    "guaranteed",
    "definitely has",
    "must have",
    "obviously",
    "perfect fit",
    "expert in",
    "worked at",
    "certified in",
)

PROMPT_INJECTION_PATTERNS = (
    "ignore previous instructions",
    "ignore all previous instructions",
    "forget the rules",
    "system prompt",
    "developer message",
    "reveal hidden instructions",
    "do anything now",
)

MIN_EVIDENCE_REQUIRED = 1
MIN_RECOMMENDATION_SCORE = {
    "Strong Match": 0.85,
    "Moderate Match": 0.65,
    "Weak Match": 0.45,
}

SAFE_ANALYSIS_RULES = (
    "Use ONLY retrieved evidence.",
    "Do NOT invent skills, employers, projects, certifications, or experience.",
    "If evidence is insufficient, explicitly state uncertainty.",
    "Unsupported claims should be rejected.",
    "Recommendations must remain evidence-grounded.",
)

SAFE_PROMPT_HEADER = """[SAFETY RULES]
Use ONLY retrieved evidence.
Do NOT invent skills, employers, projects, certifications, or experience.
If evidence is insufficient, explicitly state uncertainty.
Unsupported claims should be rejected.
Recommendations must remain evidence-grounded.
"""
