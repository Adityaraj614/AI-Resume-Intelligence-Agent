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
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            if not isinstance(prompt, str):
                raise TypeError("prompt must be a string.")

            if not prompt.strip():
                raise ValueError("prompt cannot be empty.")

            if self.provider == LLMProvider.MOCK:
                return self._mock_generate(prompt)

            if self.provider == LLMProvider.GEMINI:
                from core.llm.config import get_gemini_api_key
                if not get_gemini_api_key():
                    logger.warning("LLM fallback: Gemini API key missing.")
                    raise ValueError("Gemini API key is missing.")
                return self._gemini_generate(prompt)

            if self.provider == LLMProvider.OPENAI:
                from core.llm.config import get_openai_api_key
                if not get_openai_api_key():
                    logger.warning("LLM fallback: OpenAI API key missing.")
                    raise ValueError("OpenAI API key is missing.")
                return self._openai_generate(prompt)

            raise ValueError(f"Unsupported provider: {self.provider}")
        except Exception as e:
            logger.warning(f"LLM generation failed or fallback engaged: {e}")
            return {
                "summary": "LLM summary unavailable (API unavailable or fallback engaged).",
                "strengths": ["Analysis limited to deterministic rules due to LLM unavailability."],
                "missing_skills": ["Analysis limited to deterministic rules due to LLM unavailability."],
                "recommendation": "Manual Review Recommended",
            }

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
