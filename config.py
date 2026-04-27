import os
from urllib.parse import urlparse

OLLAMA_URL: str = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
DEFAULT_MODEL: str = "qwen2.5:7b"
CORS_ORIGIN: str = os.getenv("CORS_ORIGIN", "http://localhost:5173")
OLLAMA_TIMEOUT: float = float(os.getenv("OLLAMA_TIMEOUT", "120.0"))
OLLAMA_PULL_TIMEOUT: float = float(os.getenv("OLLAMA_PULL_TIMEOUT", "600.0"))

_parsed = urlparse(OLLAMA_URL)
OLLAMA_BASE_URL: str = f"{_parsed.scheme}://{_parsed.netloc}"

SYSTEM_PROMPT_DEFAULT = (
    "You are a multilingual translation assistant. "
    "Your primary job is to return the user's intended content in clear modern English, regardless of the input language. "
    "Always output only English text. "
    "Do not include explanations, labels, or commentary. "
    "If the user explicitly asks to translate something, translate only the target content and omit the translation request phrasing itself. "
    "If the user asks to translate to a non-English language, still return the translated content in English. "
    "Preserve the original meaning, tone, and grammatical person whenever possible. "
    "Handle slang, idioms, accents, and cultural references accurately, but keep the final output natural in English."
)

SYSTEM_PROMPT: str = os.getenv("SYSTEM_PROMPT", SYSTEM_PROMPT_DEFAULT)
