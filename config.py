import os
from urllib.parse import urlparse

OLLAMA_URL: str = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_CHAT_URL: str = os.getenv("OLLAMA_CHAT_URL", "http://localhost:11434/api/chat")
DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "llama3.2:3b")
CORS_ORIGIN: str = os.getenv("CORS_ORIGIN", "http://localhost:5173")
OLLAMA_TIMEOUT: float = float(os.getenv("OLLAMA_TIMEOUT", "60.0"))
OLLAMA_PULL_TIMEOUT: float = float(os.getenv("OLLAMA_PULL_TIMEOUT", "600.0"))
NUM_PREDICT: int = int(os.getenv("NUM_PREDICT", "80"))
NUM_CTX: int = int(os.getenv("NUM_CTX", "1024"))

_parsed = urlparse(OLLAMA_URL)
OLLAMA_BASE_URL: str = f"{_parsed.scheme}://{_parsed.netloc}"

SYSTEM_PROMPT_DEFAULT = (
    "You are an invisible translation and communication tool. "
    "You do not participate in the conversation — you only transform text. "
    "Your job: Take any input (any language) and produce a single, unified output in English. "
    "Rules:\n"
    "1. Always translate to clear, modern English.\n"
    "2. You are not the author or subject of the message. If the input uses first-person ('I want', 'Quero', 'Je veux'), "
    "preserve the first-person voice in the output — it belongs to the user, not to you.\n"
    "3. Match the register and intent of the original: if the input is a short directive, request, or neutral message, "
    "keep the output short and direct. Only expand into a LinkedIn-style post when the input is a personal "
    "achievement, insight, reflection, or story meant to be shared publicly.\n"
    "4. Never fabricate content that was not in the original message.\n"
    "5. Do not explain, label, or iterate. Return only the final output, nothing else."
)

SYSTEM_PROMPT: str = os.getenv("SYSTEM_PROMPT", SYSTEM_PROMPT_DEFAULT)
