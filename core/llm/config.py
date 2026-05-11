import os


DEFAULT_PROVIDER = "mock"
GEMINI_MODEL = "gemini-1.5-flash"
OPENAI_MODEL = "gpt-4o-mini"
MAX_OUTPUT_TOKENS = 800
TEMPERATURE = 0.2


def get_default_provider() -> str:
    """
    Read the configured LLM provider.

    Defaults to the deterministic mock provider so local development and tests
    never require external API credentials.
    """

    return os.getenv("LLM_PROVIDER", DEFAULT_PROVIDER).strip().lower()


def get_gemini_model() -> str:
    return os.getenv("GEMINI_MODEL", GEMINI_MODEL)


def get_openai_model() -> str:
    return os.getenv("OPENAI_MODEL", OPENAI_MODEL)


def get_max_output_tokens() -> int:
    return int(os.getenv("MAX_OUTPUT_TOKENS", MAX_OUTPUT_TOKENS))


def get_temperature() -> float:
    return float(os.getenv("TEMPERATURE", TEMPERATURE))


def get_gemini_api_key() -> str:
    return os.getenv("GEMINI_API_KEY", "")


def get_openai_api_key() -> str:
    return os.getenv("OPENAI_API_KEY", "")
