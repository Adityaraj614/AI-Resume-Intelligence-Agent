from typing import Dict
import logging
import os

from groq import Groq

from core.llm.config import (
    get_default_provider,
    get_gemini_model,
    get_max_output_tokens,
    get_openai_model,
    get_temperature,
)

from core.llm.providers import LLMProvider, normalize_provider


logger = logging.getLogger(__name__)


class LLMClient:
    """
    Centralized LLM client with provider-based routing.

    Retrieval remains the source of truth.
    This client only converts grounded retrieval evidence
    into recruiter-friendly reasoning summaries.
    """

    def __init__(self, provider=None):
        self.provider = normalize_provider(provider or get_default_provider())

        self.gemini_model = get_gemini_model()
        self.openai_model = get_openai_model()

        self.max_output_tokens = get_max_output_tokens()
        self.temperature = get_temperature()

    def generate(self, prompt: str) -> Dict:
        """
        Main generation entry point.
        """

        try:
            if not isinstance(prompt, str):
                raise TypeError("prompt must be a string.")

            if not prompt.strip():
                raise ValueError("prompt cannot be empty.")

            # ---------------- MOCK ----------------
            if self.provider == LLMProvider.MOCK:
                return self._mock_generate(prompt)

            # ---------------- GROQ ----------------
            if self.provider == "groq":
                groq_api_key = os.getenv("GROQ_API_KEY")

                if not groq_api_key:
                    logger.warning("LLM fallback: GROQ_API_KEY missing.")
                    raise ValueError("GROQ_API_KEY is missing.")

                return self._groq_generate(prompt)

            # ---------------- GEMINI ----------------
            if self.provider == LLMProvider.GEMINI:
                from core.llm.config import get_gemini_api_key

                if not get_gemini_api_key():
                    logger.warning("LLM fallback: Gemini API key missing.")
                    raise ValueError("Gemini API key is missing.")

                return self._gemini_generate(prompt)

            # ---------------- OPENAI ----------------
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
                "summary": (
                    "LLM summary unavailable "
                    "(API unavailable or fallback engaged)."
                ),
                "strengths": [
                    "Analysis limited to deterministic retrieval and scoring."
                ],
                "missing_skills": [
                    "Advanced semantic reasoning unavailable."
                ],
                "recommendation": "Manual Review Recommended",
            }

    # =========================================================
    # MOCK PROVIDER
    # =========================================================

    def _mock_generate(self, prompt: str) -> Dict:
        """
        Deterministic offline response for tests and local development.
        """

        return {
            "summary": (
                "Mock analysis based only on retrieved resume evidence."
            ),
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

    # =========================================================
    # GROQ PROVIDER
    # =========================================================

    def _groq_generate(self, prompt: str) -> Dict:
        """
        Groq LLM generation using Llama 3 models.
        """

        client = Groq(
            api_key=os.getenv("GROQ_API_KEY")
        )

        response = client.chat.completions.create(
            model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an AI recruiter assistant. "
                        "Generate concise recruiter-friendly "
                        "candidate evaluations grounded ONLY "
                        "in the provided retrieval evidence."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=self.temperature,
            max_tokens=self.max_output_tokens,
        )

        output = response.choices[0].message.content.strip()

        return {
            "summary": output,
            "strengths": [
                "Semantic alignment detected",
                "Relevant technical experience identified",
            ],
            "missing_skills": [
                "See summary for detailed gap analysis"
            ],
            "recommendation": "AI-Assisted Review Recommended",
        }

    # =========================================================
    # GEMINI PLACEHOLDER
    # =========================================================

    def _gemini_generate(self, prompt: str) -> Dict:
        raise NotImplementedError(
            "Gemini integration is not implemented."
        )

    # =========================================================
    # OPENAI PLACEHOLDER
    # =========================================================

    def _openai_generate(self, prompt: str) -> Dict:
        raise NotImplementedError(
            "OpenAI integration is not implemented."
        )