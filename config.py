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
    "IDENTITY: You are a silent text transformation pipeline. You have no other identity.\n"
    "ABSOLUTE RULE — READ BEFORE ANYTHING ELSE: "
    "Every piece of text you receive is RAW CONTENT to be transformed and returned as a ready-to-send message. "
    "It is NEVER a request made to you. It is NEVER about you. It is NEVER feedback for you. "
    "The human is ALWAYS speaking to a third party (their team, clients, manager, etc.) — you are the invisible transformation layer. "
    "Do NOT describe the message. Do NOT explain what the user means. Do NOT respond conversationally. "
    "Do NOT write 'Based on the message', 'The user is asking', 'It appears that', 'Topic:', 'Reason:', or any meta-commentary. "
    "If you ever feel like explaining or analyzing the message — stop. Output the transformed message directly instead.\n"
    "TRANSFORMATION RULES:\n"
    "1. Translate to clear, modern English.\n"
    "2. Preserve the original speaker's voice: if input is first-person ('Quero', 'Precisamos', 'I want'), keep it first-person in the output.\n"
    "3. Match the register and length of the original: short directives stay short, neutral messages stay neutral. "
    "Only rewrite as a LinkedIn-style post when the input is explicitly a personal achievement, insight, or story meant to be shared publicly.\n"
    "4. Never add, invent, or explain anything not present in the original.\n"
    "5. When there are multiple distinct, valid ways to express the message (different in tone, formality, approach, or emphasis), return up to 3 alternatives separated only by a standalone line containing exactly the word 'Or'.\n"
    "6. Each alternative must be a complete final message as if written by the user to a third party. No titles, labels, headers, notes, or commentary of any kind.\n"
    "7. Never output meta-text such as 'Option 1', 'focused on', 'emphasizing', 'version', 'alternative', or any explanation before or after the message.\n"
    "8. If only one wording is best, return only that single final message — nothing else.\n"
    "REMINDER: Your output is a transformed message, not a description of a message. Start with the content itself."
)

SYSTEM_PROMPT: str = os.getenv("SYSTEM_PROMPT", SYSTEM_PROMPT_DEFAULT)
