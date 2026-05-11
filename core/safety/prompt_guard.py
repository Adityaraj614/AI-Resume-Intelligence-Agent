import re

from core.safety.safety_rules import (
    PROMPT_INJECTION_PATTERNS,
    SAFE_PROMPT_HEADER,
)


def sanitize_prompt_context(context: str) -> str:
    """
    Remove common prompt-injection phrases from retrieved text.
    """

    if not isinstance(context, str):
        raise TypeError("context must be a string.")

    sanitized_context = context

    for pattern in PROMPT_INJECTION_PATTERNS:
        sanitized_context = re.sub(
            re.escape(pattern),
            "[removed unsafe instruction]",
            sanitized_context,
            flags=re.IGNORECASE,
        )

    return sanitized_context.strip()


def inject_safety_constraints(prompt: str) -> str:
    """
    Prefix prompt text with fixed evidence-grounding constraints.
    """

    if not isinstance(prompt, str):
        raise TypeError("prompt must be a string.")

    prompt = prompt.strip()

    if prompt.startswith("[SAFETY RULES]"):
        return prompt

    return f"{SAFE_PROMPT_HEADER}\n{prompt}"


def build_safe_prompt(prompt_template: str, **template_values) -> str:
    """
    Format a prompt template after sanitizing all string values.
    """

    if not isinstance(prompt_template, str):
        raise TypeError("prompt_template must be a string.")

    sanitized_values = {
        key: sanitize_prompt_context(value) if isinstance(value, str) else value
        for key, value in template_values.items()
    }
    formatted_prompt = prompt_template.format(**sanitized_values)

    return inject_safety_constraints(formatted_prompt)
