"""
Shared translation utility.

Translates an arbitrary message to English using Ollama.
Used by /translate (endpoint) and /chat (preprocessing layer).
"""
import logging
from ollama import ollama_generate
from training import load_translate_examples
from config import DEFAULT_MODEL, TRANSLATE_EXAMPLES_LIMIT

logger = logging.getLogger(__name__)

_TRANSLATE_SYSTEM = (
    "Treat this request as fully isolated. Use only the current message. Do not continue or reuse any previous task or text.\n"
    "Task: detect language and translate to English when needed.\n"
    "Rules:\n"
    "1) If fully English, output exactly: ENGLISH\n"
    "2) Otherwise translate the full message to natural English\n"
    "3) Preserve subject, product names, and business reasons\n"
    "4) Output only final text (no labels or explanations)."
    + load_translate_examples(TRANSLATE_EXAMPLES_LIMIT)
)

_VALIDATE_TRANSLATION_SYSTEM = (
    "Treat this request as fully isolated. Use only the current original message and candidate translation. "
    "You validate whether an English translation preserves the original message intent, emotional tone, and key facts. "
    "Return only the corrected English translation, with no explanations or labels. "
    "If the candidate translation is already faithful, return it unchanged."
)


async def translate_to_english(message: str, model: str = DEFAULT_MODEL) -> str:
    """Return the English translation of *message*.

    If the message is already in English the original string is returned as-is.
    The translation preserves tone, sentiment, and intent so that downstream
    LLM processing receives the full emotional context of the original message.
    Falls back to the original message on Ollama errors so the chat pipeline
    can still produce a response.
    """
    prompt = f"{_TRANSLATE_SYSTEM}\n\nMessage: {message}"
    try:
        result = await ollama_generate(model, prompt)
    except Exception as exc:
        logger.error("translate_to_english failed — falling back to original message: %s", exc)
        return message
    result = result.strip()
    if result == "ENGLISH":
        return message
    return result


async def validate_translation_context(
    original_message: str,
    translated_message: str,
    model: str = DEFAULT_MODEL,
) -> str:
    """Validate semantic fidelity between original and translation.

    Returns a corrected English translation when context/tone drift is detected.
    Falls back to the candidate translation on Ollama errors.
    """
    prompt = (
        f"{_VALIDATE_TRANSLATION_SYSTEM}\n\n"
        f"Original message (source language): {original_message}\n"
        f"Candidate English translation: {translated_message}\n\n"
        "Return only the final faithful English translation."
    )
    try:
        corrected = await ollama_generate(model, prompt)
    except Exception as exc:
        logger.error("validate_translation_context failed — using candidate translation: %s", exc)
        return translated_message
    corrected = corrected.strip()
    return corrected or translated_message


async def translate_with_context_validation(message: str, model: str = DEFAULT_MODEL) -> str:
    """Translate and validate context preservation for downstream chat processing."""
    translated = await translate_to_english(message, model)
    if translated.strip() == message.strip():
        return translated
    return await validate_translation_context(message, translated, model)


async def translate_for_chat(message: str, model: str = DEFAULT_MODEL, validate_context: bool = False) -> str:
    """Translate for chat flow with optional context validation.

    The chat route defaults to a single translation pass for lower latency.
    """
    translated = await translate_to_english(message, model)
    if translated.strip() == message.strip() or not validate_context:
        return translated
    return await validate_translation_context(message, translated, model)
