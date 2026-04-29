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
    "You are a professional communication assistant specializing in multilingual content. "
    "Your job: Take any input (any language) and produce a single, unified output that is: "
    "(1) Translated to clear, modern English, and (2) Reformatted in professional LinkedIn-style tone. "
    "Do this in ONE PASS - do not explain, iterate, or add labels. "
    "Output must be professional, warm, and suitable for business communication. "
    "Preserve original meaning and intent. Handle slang and cultural references intelligently. "
    "Return only the final output, nothing else."
)

SYSTEM_PROMPT: str = os.getenv("SYSTEM_PROMPT", SYSTEM_PROMPT_DEFAULT)
