import json
import logging
import asyncio
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from schemas import (
    ChatRequest,
    ChatResponse,
    ContextGateRequest,
    TranslateRequest,
    TranslateResponse,
)
from ollama import ollama_chat, ollama_chat_stream
from translation import translate_to_english
from config import (
    CHAT_ENABLE_CONTEXT_GATE,
    CHAT_MIN_ALTERNATIVES,
    CHAT_RETRY_ATTEMPTS,
    CHAT_RETRY_BACKOFF_SECONDS,
)
import httpx
import system_prompt

logger = logging.getLogger(__name__)
_RETRYABLE_STATUS_CODES = {500, 502, 503, 504}

_CONTEXT_GATE_SYSTEM = (
    "You are a strict context gate for rewritten user messages. "
    "Your job is to keep only outputs that faithfully preserve the original user intent, key topic, and business reason. "
    "The user is always speaking to a third party, never to you.\n"
    "Rules:\n"
    "1. Remove any meta text, labels, headings, explanations, or commentary (e.g., 'Here's a possible response', 'Option 1', 'emphasizing').\n"
    "2. Keep only complete final messages that can be sent as-is.\n"
    "3. Preserve concrete key facts from the original message (subject, reason, constraints).\n"
    "4. Do not invent new facts or change the decision meaning.\n"
    "5. If multiple valid alternatives remain, output them separated only by a standalone line containing 'Or'.\n"
    "6. If only one valid message remains, output that single message only.\n"
    "7. Output only the final cleaned message text with no preface or trailing notes."
)

_FORCE_ALTERNATIVES_SYSTEM = (
    "You rewrite a user's message for a third party.\n"
    "Return 2 to 3 distinct, context-faithful alternatives.\n"
    "Rules:\n"
    "1. Keep the same core meaning, topic, and reason from the original message.\n"
    "2. Keep the user's point of view (first-person when present).\n"
    "3. No meta text, no labels, no explanations, no headings.\n"
    "4. Output alternatives separated only by a standalone line containing 'Or'.\n"
    "5. Each alternative must be a complete final message ready to send."
)


def _count_or_alternatives(text: str) -> int:
    if not isinstance(text, str):
        return 0
    normalized = text.strip()
    if not normalized:
        return 0
    parts = [part.strip() for part in normalized.replace("\r", "").split("\n")]
    alternatives = []
    current: list[str] = []

    for line in parts:
        if line.lower() == "or":
            candidate = " ".join(current).strip()
            if candidate:
                alternatives.append(candidate)
            current = []
            continue
        if line:
            current.append(line)

    tail = " ".join(current).strip()
    if tail:
        alternatives.append(tail)

    return len([alt for alt in alternatives if alt])


def _split_or_alternatives(text: str) -> list[str]:
    if not isinstance(text, str):
        return []

    alternatives = []
    current: list[str] = []
    for line in text.replace("\r", "").split("\n"):
        normalized = line.strip()
        if not normalized:
            continue
        if normalized.lower() == "or":
            candidate = " ".join(current).strip()
            if candidate:
                alternatives.append(candidate)
            current = []
            continue
        current.append(normalized)

    candidate = " ".join(current).strip()
    if candidate:
        alternatives.append(candidate)

    unique: list[str] = []
    seen: set[str] = set()
    for alternative in alternatives:
        key = alternative.lower()
        if key in seen:
            continue
        seen.add(key)
        unique.append(alternative)
    return unique


async def _ollama_chat_with_retry(model: str, system: str, user: str, few_shot: list[dict] | None = None) -> str:
    for attempt in range(1, CHAT_RETRY_ATTEMPTS + 1):
        try:
            return await ollama_chat(model, system, user, few_shot=few_shot)
        except httpx.HTTPStatusError as exc:
            status_code = exc.response.status_code if exc.response else None
            retryable = status_code in _RETRYABLE_STATUS_CODES
            has_next_attempt = attempt < CHAT_RETRY_ATTEMPTS

            if retryable and has_next_attempt:
                delay = CHAT_RETRY_BACKOFF_SECONDS * attempt
                logger.warning(
                    "ollama_chat failed with HTTP %s (attempt %s/%s). Retrying in %.2fs.",
                    status_code,
                    attempt,
                    CHAT_RETRY_ATTEMPTS,
                    delay,
                )
                await asyncio.sleep(delay)
                continue
            raise
        except httpx.RequestError as exc:
            has_next_attempt = attempt < CHAT_RETRY_ATTEMPTS

            if has_next_attempt:
                delay = CHAT_RETRY_BACKOFF_SECONDS * attempt
                logger.warning(
                    "ollama_chat request failed (attempt %s/%s): %s. Retrying in %.2fs.",
                    attempt,
                    CHAT_RETRY_ATTEMPTS,
                    exc,
                    delay,
                )
                await asyncio.sleep(delay)
                continue
            raise


async def _context_gate_response(
    model: str,
    original_message: str,
    candidate_response: str,
) -> str:
    prompt = (
        "Original user message:\n"
        f"{original_message}\n\n"
        "Candidate rewrite output:\n"
        f"{candidate_response}\n\n"
        "Return the cleaned, context-faithful final output now."
    )

    cleaned = await _ollama_chat_with_retry(model, _CONTEXT_GATE_SYSTEM, prompt)
    cleaned = cleaned.strip()
    return cleaned or candidate_response


async def _linkedinfy_message(model: str, message: str) -> str:
    prefixed_message = f"Rewrite: {message}"
    response = await _ollama_chat_with_retry(model, system_prompt.get(), prefixed_message, few_shot=system_prompt.get_few_shot())
    return response.strip() or message


async def _translate_message(model: str, message: str) -> str:
    translated = await translate_to_english(message, model)
    translated = translated.strip()
    return translated or message


async def _generate_alternative_messages(model: str, original_message: str, primary_message: str) -> list[str]:
    prompt = (
        "MESSAGE TO TRANSFORM:\n"
        f"{original_message}\n\n"
        "PRIMARY LINKEDINFY VERSION (context only):\n"
        f"{primary_message}\n\n"
        "Return 2 to 3 distinct transformations of the original message above, separated by a standalone 'Or' line."
    )
    raw = await _ollama_chat_with_retry(model, _FORCE_ALTERNATIVES_SYSTEM, prompt)
    alternatives = _split_or_alternatives(raw)
    if alternatives:
        return alternatives
    return [primary_message]


async def _finalize_alternative_messages(model: str, original_message: str, suggestions: list[str]) -> list[str]:
    finalized: list[str] = []
    seen: set[str] = set()

    for suggestion in suggestions:
        gated = await _context_gate_response(model, original_message, suggestion)
        key = gated.lower()
        if key in seen:
            continue
        seen.add(key)
        finalized.append(gated)

    return finalized


def _map_pipeline_error(exc: Exception) -> HTTPException:
    if isinstance(exc, httpx.HTTPStatusError):
        logger.error("ollama_chat failed with HTTP %s: %s", exc.response.status_code, exc)
        return HTTPException(status_code=503, detail="LLM generation unavailable — Ollama returned an error. Please retry.")
    logger.error("ollama_chat failed — cannot reach Ollama: %s", exc)
    return HTTPException(status_code=503, detail="LLM generation unavailable — cannot reach Ollama. Please retry.")

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        linked = await _linkedinfy_message(request.model, request.message)
        response = await _context_gate_response(request.model, request.message, linked)

        if CHAT_ENABLE_CONTEXT_GATE and CHAT_MIN_ALTERNATIVES > 1 and _count_or_alternatives(response) < CHAT_MIN_ALTERNATIVES:
            alternatives = await _generate_alternative_messages(request.model, request.message, response)
            finalized = await _finalize_alternative_messages(request.model, request.message, alternatives)
            if finalized:
                response = "\nOr\n".join(finalized[:CHAT_MIN_ALTERNATIVES])
    except (httpx.HTTPStatusError, httpx.RequestError) as exc:
        raise _map_pipeline_error(exc)
    
    return ChatResponse(model=request.model, response=response)


@router.post("/chat/pipeline/linkedinfy", response_model=ChatResponse)
async def chat_pipeline_linkedinfy(request: ChatRequest):
    try:
        response = await _linkedinfy_message(request.model, request.message)
    except (httpx.HTTPStatusError, httpx.RequestError) as exc:
        raise _map_pipeline_error(exc)
    return ChatResponse(model=request.model, response=response)


@router.post("/chat/pipeline/context-gate", response_model=ChatResponse)
async def chat_pipeline_context_gate(request: ContextGateRequest):
    try:
        response = await _context_gate_response(request.model, request.original_message, request.candidate_message)
    except (httpx.HTTPStatusError, httpx.RequestError) as exc:
        raise _map_pipeline_error(exc)
    return ChatResponse(model=request.model, response=response)


@router.post("/chat/pipeline/translate", response_model=TranslateResponse)
async def chat_pipeline_translate(request: TranslateRequest):
    try:
        response = await _translate_message(request.model, request.message)
    except (httpx.HTTPStatusError, httpx.RequestError) as exc:
        raise _map_pipeline_error(exc)
    return TranslateResponse(model=request.model, response=response)


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    try:
        async def event_stream():
            async for token in ollama_chat_stream(request.model, system_prompt.get(), request.message):
                yield f"data: {json.dumps({'token': token})}\n\n"
            yield f"data: {json.dumps({'done': True, 'model': request.model})}\n\n"

        return StreamingResponse(event_stream(), media_type="text/event-stream")
    except (httpx.HTTPStatusError, httpx.RequestError) as exc:
        raise _map_pipeline_error(exc)
