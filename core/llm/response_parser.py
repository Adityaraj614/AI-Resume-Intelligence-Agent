REQUIRED_RESPONSE_KEYS = (
    "summary",
    "strengths",
    "missing_skills",
    "recommendation",
)


def validate_llm_response(response) -> bool:
    """
    Validate the minimal structured response expected from any LLM provider.
    """

    if not isinstance(response, dict):
        return False

    for key in REQUIRED_RESPONSE_KEYS:
        if key not in response:
            return False

    if not isinstance(response["summary"], str):
        return False

    if not isinstance(response["strengths"], list):
        return False

    if not isinstance(response["missing_skills"], list):
        return False

    if not isinstance(response["recommendation"], str):
        return False

    return True
