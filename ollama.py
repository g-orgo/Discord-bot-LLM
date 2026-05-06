import httpx
import json
from config import (
    OLLAMA_URL,
    OLLAMA_CHAT_URL,
    OLLAMA_TIMEOUT,
    OLLAMA_KEEP_ALIVE,
    OLLAMA_LOW_VRAM,
    NUM_PREDICT,
    NUM_CTX,
)
from typing import AsyncGenerator

_OLLAMA_OPTIONS = {
    "num_predict": NUM_PREDICT, 
    "num_ctx": NUM_CTX,
    "temperature": 0.2,  # Lower temperature = less hallucination, more deterministic
    "top_p": 0.1,        # Lower top_p = more restrictive sampling
}
if OLLAMA_LOW_VRAM:
    _OLLAMA_OPTIONS["low_vram"] = True

# Persistent client — initialized once at startup, reused across all requests.
_client: httpx.AsyncClient | None = None


def init_client() -> None:
    global _client
    timeout = httpx.Timeout(connect=10.0, read=OLLAMA_TIMEOUT, write=30.0, pool=30.0)
    _client = httpx.AsyncClient(timeout=timeout)


async def close_client() -> None:
    global _client
    if _client is not None:
        await _client.aclose()
        _client = None


def _get_client() -> httpx.AsyncClient:
    if _client is None:
        raise RuntimeError("Ollama httpx client not initialized — call init_client() first")
    return _client


async def ollama_generate(model: str, prompt: str) -> str:
    payload = {"model": model, "prompt": prompt, "stream": False, "keep_alive": OLLAMA_KEEP_ALIVE, "options": _OLLAMA_OPTIONS}
    res = await _get_client().post(OLLAMA_URL, json=payload)
    res.raise_for_status()
    return res.json()["response"]


async def ollama_chat(model: str, system: str, user: str, few_shot: list[dict] | None = None) -> str:
    messages: list[dict] = [{"role": "system", "content": system}]
    if few_shot:
        messages.extend(few_shot)
    messages.append({"role": "user", "content": user})
    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
        "keep_alive": OLLAMA_KEEP_ALIVE,
        "options": _OLLAMA_OPTIONS,
    }
    res = await _get_client().post(OLLAMA_CHAT_URL, json=payload)
    res.raise_for_status()
    return res.json()["message"]["content"]


async def ollama_chat_stream(model: str, system: str, user: str, few_shot: list[dict] | None = None) -> AsyncGenerator[str, None]:
    messages: list[dict] = [{"role": "system", "content": system}]
    if few_shot:
        messages.extend(few_shot)
    messages.append({"role": "user", "content": user})
    payload = {
        "model": model,
        "messages": messages,
        "stream": True,
        "keep_alive": OLLAMA_KEEP_ALIVE,
        "options": _OLLAMA_OPTIONS,
    }
    async with _get_client().stream("POST", OLLAMA_CHAT_URL, json=payload) as response:
        response.raise_for_status()
        async for line in response.aiter_lines():
            if line:
                data = json.loads(line)
                yield data.get("message", {}).get("content", "")
                if data.get("done"):
                    break


async def ollama_generate_stream(model: str, prompt: str) -> AsyncGenerator[str, None]:
    payload = {"model": model, "prompt": prompt, "stream": True, "keep_alive": OLLAMA_KEEP_ALIVE, "options": _OLLAMA_OPTIONS}
    async with _get_client().stream("POST", OLLAMA_URL, json=payload) as response:
        response.raise_for_status()
        async for line in response.aiter_lines():
            if line:
                data = json.loads(line)
                yield data.get("response", "")
                if data.get("done"):
                    break
