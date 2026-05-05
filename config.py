import os
from urllib.parse import urlparse

OLLAMA_URL: str = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_CHAT_URL: str = os.getenv("OLLAMA_CHAT_URL", "http://localhost:11434/api/chat")
DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "qwen2.5:1.5b")
CORS_ORIGIN: str = os.getenv("CORS_ORIGIN", "http://localhost:5173")
OLLAMA_TIMEOUT: float = float(os.getenv("OLLAMA_TIMEOUT", "300.0"))
OLLAMA_PULL_TIMEOUT: float = float(os.getenv("OLLAMA_PULL_TIMEOUT", "600.0"))
OLLAMA_KEEP_ALIVE: str = os.getenv("OLLAMA_KEEP_ALIVE", "5m")
OLLAMA_LOW_VRAM: bool = os.getenv("OLLAMA_LOW_VRAM", "true").strip().lower() in {
    "1", "true", "yes", "on"
}
NUM_PREDICT: int = int(os.getenv("NUM_PREDICT", "80"))
NUM_CTX: int = int(os.getenv("NUM_CTX", "1024"))
TRANSLATE_EXAMPLES_LIMIT: int = max(0, int(os.getenv("TRANSLATE_EXAMPLES_LIMIT", "2")))
CHAT_ENABLE_CONTEXT_GATE: bool = os.getenv("CHAT_ENABLE_CONTEXT_GATE", "false").strip().lower() in {
    "1", "true", "yes", "on"
}
CHAT_MIN_ALTERNATIVES: int = max(1, int(os.getenv("CHAT_MIN_ALTERNATIVES", "1")))
CHAT_RETRY_ATTEMPTS: int = max(1, int(os.getenv("CHAT_RETRY_ATTEMPTS", "2")))
CHAT_RETRY_BACKOFF_SECONDS: float = max(0.0, float(os.getenv("CHAT_RETRY_BACKOFF_SECONDS", "1.5")))

_parsed = urlparse(OLLAMA_URL)
OLLAMA_BASE_URL: str = f"{_parsed.scheme}://{_parsed.netloc}"

SYSTEM_PROMPT_DEFAULT = (
    "TASK: Rewrite messages. Only rewrite. Do not add, do not respond, do not explain.\n"
    "INPUT_LANGUAGE = OUTPUT_LANGUAGE (Portuguese stays Portuguese, English stays English).\n\n"
    "EXAMPLES:\n"
    "Input: 'I'm giving a presentation to my dad'\n"
    "Output: 'I'll be presenting to my father.'\n\n"
    "Input: 'Need to talk to you about a business opportunity'\n"
    "Output: 'I'd like to discuss a potential business opportunity.'\n\n"
    "Input: 'Wanna talk to the boss about a raise'\n"
    "Output: 'I'd like to schedule a conversation about my salary.'\n\n"
    "RULES (MANDATORY):\n"
    "1. Rewrite the message. Preserve the input language.\n"
    "2. DO NOT add new ideas, suggestions, or context.\n"
    "3. DO NOT respond as if speaking TO YOU. The message is for someone else.\n"
    "4. DO NOT change the language.\n"
    "5. DO NOT be overly polite or conversational.\n"
    "6. OUTPUT: Only the rewritten message. Nothing else.\n"
    "7. If the message is already clear, make minimal changes or keep as-is."
)

SYSTEM_PROMPT: str = os.getenv("SYSTEM_PROMPT", SYSTEM_PROMPT_DEFAULT)
