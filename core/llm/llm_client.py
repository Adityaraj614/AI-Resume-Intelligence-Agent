from typing import Dict

from core.llm.config import (
    get_default_provider,
    get_gemini_model,
    get_max_output_tokens,
    get_openai_model,
    get_temperature,
)
from core.llm.providers import LLMProvider, normalize_provider


class LLMClient:
    """
    Centralized LLM client with provider-based routing.

    Retrieval remains the source of truth. This client is only responsible for
    turning grounded prompts into reasoning-style responses.
    """

    def __init__(self, provider=None):
        self.provider = normalize_provider(provider or get_default_provider())
        self.gemini_model = get_gemini_model()
        self.openai_model = get_openai_model()
        self.max_output_tokens = get_max_output_tokens()
        self.temperature = get_temperature()

    def generate(self, prompt: str) -> Dict:
        if not isinstance(prompt, str):
            raise TypeError("prompt must be a string.")

        if not prompt.strip():
            raise ValueError("prompt cannot be empty.")

        if self.provider == LLMProvider.MOCK:

            return self._mock_generate(prompt)

        if self.provider == LLMProvider.GEMINI:

            return self._gemini_generate(prompt)

        if self.provider == LLMProvider.OPENAI:

            return self._openai_generate(prompt)

        raise ValueError(
            f"Unsupported provider: {self.provider}"
        )

    def _mock_generate(self, prompt: str) -> Dict:
        """
        Deterministic offline response for tests and local development.
        """

        return {
            "summary": "Mock analysis based only on retrieved resume evidence.",
            "strengths": [
                "Evidence-backed Python experience",
                "Evidence-backed machine learning experience",
                "Evidence-backed project work",
            ],
            "missing_skills": [
                "No additional missing skills inferred by mock provider"
            ],
            "recommendation": "Review recommended",
        }

    def _gemini_generate(self, prompt: str) -> Dict:
        raise NotImplementedError(
            "Gemini integration is not implemented in Phase 4A."
        )

    def _openai_generate(self, prompt: str) -> Dict:
        raise NotImplementedError(
            "OpenAI integration is not implemented in Phase 4A."
        )
