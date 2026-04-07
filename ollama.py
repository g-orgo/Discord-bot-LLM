import httpx
from config import OLLAMA_URL


async def ollama_generate(model: str, prompt: str) -> str:
    payload = {"model": model, "prompt": prompt, "stream": False}
    async with httpx.AsyncClient(timeout=120.0) as client:
        res = await client.post(OLLAMA_URL, json=payload)
        res.raise_for_status()
        return res.json()["response"]
