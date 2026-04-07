import httpx
import json
from config import OLLAMA_URL, OLLAMA_TIMEOUT, OLLAMA_PULL_TIMEOUT
from typing import AsyncGenerator


async def ollama_generate(model: str, prompt: str) -> str:
    payload = {"model": model, "prompt": prompt, "stream": False}
    async with httpx.AsyncClient(timeout=OLLAMA_TIMEOUT) as client:
        res = await client.post(OLLAMA_URL, json=payload)
        res.raise_for_status()
        return res.json()["response"]


async def ollama_generate_stream(model: str, prompt: str) -> AsyncGenerator[str, None]:
    payload = {"model": model, "prompt": prompt, "stream": True}
    async with httpx.AsyncClient(timeout=OLLAMA_TIMEOUT) as client:
        async with client.stream("POST", OLLAMA_URL, json=payload) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line:
                    data = json.loads(line)
                    yield data.get("response", "")
                    if data.get("done"):
                        break
