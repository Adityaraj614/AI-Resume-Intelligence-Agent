import pytest

from core.llm.llm_client import LLMClient
from core.llm.prompt_templates import MATCH_ANALYSIS_PROMPT
from core.llm.providers import LLMProvider
from core.llm.response_parser import validate_llm_response


def test_mock_llm_generation():
    client = LLMClient()

    response = client.generate("Retrieved evidence: Python and ML projects.")

    assert validate_llm_response(response)
    assert "summary" in response
    assert "strengths" in response
    assert "missing_skills" in response
    assert "recommendation" in response


def test_mock_llm_generation_is_deterministic():
    client = LLMClient(provider=LLMProvider.MOCK)

    first_response = client.generate("same grounded prompt")
    second_response = client.generate("same grounded prompt")

    assert first_response == second_response


def test_provider_string_is_normalized():
    client = LLMClient(provider="mock")

    assert client.provider == LLMProvider.MOCK


def test_placeholder_providers_raise_not_implemented():
    gemini_client = LLMClient(provider=LLMProvider.GEMINI)
    openai_client = LLMClient(provider=LLMProvider.OPENAI)

    with pytest.raises(NotImplementedError):
        gemini_client.generate("grounded prompt")

    with pytest.raises(NotImplementedError):
        openai_client.generate("grounded prompt")


def test_invalid_response_validation_fails():
    invalid_response = {
        "summary": "Missing required list fields",
        "recommendation": "Review",
    }

    assert validate_llm_response(invalid_response) is False


def test_match_analysis_prompt_is_retrieval_grounded():
    assert "Retrieval results are the source of truth." in MATCH_ANALYSIS_PROMPT
    assert "Do NOT invent skills or experience." in MATCH_ANALYSIS_PROMPT
    assert "{context}" in MATCH_ANALYSIS_PROMPT
