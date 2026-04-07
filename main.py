from contextlib import asynccontextmanager
import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import CORS_ORIGIN, OLLAMA_BASE_URL, DEFAULT_MODEL, OLLAMA_PULL_TIMEOUT
from routes.generate import router as generate_router
from routes.chat import router as chat_router
from routes.system_prompt import router as system_prompt_router


async def _ensure_model() -> None:
    max_attempts = 3
    for attempt in range(1, max_attempts + 1):
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                tags_res = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
                tags_res.raise_for_status()
                installed = [m["name"].split(":")[0] for m in tags_res.json().get("models", [])]
                if DEFAULT_MODEL in installed:
                    print(f"[startup] Model '{DEFAULT_MODEL}' is already installed.")
                    return
                print(f"[startup] Model '{DEFAULT_MODEL}' not found. Pulling (attempt {attempt}/{max_attempts})...")
                pull_res = await client.post(
                    f"{OLLAMA_BASE_URL}/api/pull",
                    json={"name": DEFAULT_MODEL, "stream": False},
                    timeout=OLLAMA_PULL_TIMEOUT,
                )
                pull_res.raise_for_status()
                print(f"[startup] Model '{DEFAULT_MODEL}' pulled successfully.")
                return
        except Exception as exc:
            print(f"[startup] Attempt {attempt}/{max_attempts} failed: {exc}")
    print(f"[startup] WARNING: Could not ensure model '{DEFAULT_MODEL}' after {max_attempts} attempts.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await _ensure_model()
    yield


app = FastAPI(title="Raptor LLM", description="A translation layer and Brand communication tool for Discord channels with a web application interface.", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[CORS_ORIGIN],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(generate_router)
app.include_router(chat_router)
app.include_router(system_prompt_router)


@app.get("/")
def root():
    return {"message": "Raptor LLM API is running"}

