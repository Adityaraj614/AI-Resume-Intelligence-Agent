from enum import Enum


class LLMProvider(Enum):
    MOCK = "mock"
    GEMINI = "gemini"
    OPENAI = "openai"


def normalize_provider(provider) -> LLMProvider:
    """
    Convert strings or enum values into a safe provider enum.
    """

    if isinstance(provider, LLMProvider):
        return provider

    if isinstance(provider, str):
        normalized_provider = provider.strip().lower()

        for llm_provider in LLMProvider:
            if llm_provider.value == normalized_provider:
                return llm_provider

    raise ValueError(f"Unsupported provider: {provider}")
