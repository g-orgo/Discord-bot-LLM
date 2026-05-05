from contextlib import asynccontextmanager
import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from config import CORS_ORIGIN, OLLAMA_BASE_URL, DEFAULT_MODEL, OLLAMA_PULL_TIMEOUT
from routes.generate import router as generate_router
from routes.chat import router as chat_router
from routes.system_prompt import router as system_prompt_router
from routes.translate import router as translate_router
from routes.benchmark import router as benchmark_router
import ollama as ollama_client


async def _ensure_model() -> None:
    max_attempts = 3
    for attempt in range(1, max_attempts + 1):
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                tags_res = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
                tags_res.raise_for_status()
                installed = [m["name"] for m in tags_res.json().get("models", [])]
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


async def _warmup_model() -> None:
    try:
        print(f"[startup] Warming up model '{DEFAULT_MODEL}' into memory...")
        await ollama_client.ollama_chat(DEFAULT_MODEL, "You are a helpful assistant.", "hi")
        print(f"[startup] Model '{DEFAULT_MODEL}' is warm and ready.")
    except Exception as exc:
        print(f"[startup] WARNING: Warm-up failed (first user request may be slow): {exc}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    ollama_client.init_client()
    await _ensure_model()
    await _warmup_model()
    yield
    await ollama_client.close_client()


app = FastAPI(title="Raptor LLM", description="A translation layer and Brand communication tool for Discord channels with a web application interface.", lifespan=lifespan)


@app.exception_handler(httpx.TimeoutException)
async def ollama_timeout_exception_handler(request, exc):
    return JSONResponse(
        status_code=504,
        content={
            "detail": "Ollama timed out while loading or responding. Increase OLLAMA_TIMEOUT or reduce request complexity.",
        },
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=[CORS_ORIGIN],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(generate_router)
app.include_router(chat_router)
app.include_router(system_prompt_router)
app.include_router(translate_router)
app.include_router(benchmark_router)


@app.get("/")
def root():
    return {"message": "Raptor LLM API is running"}


@app.get("/health")
def health():
    return {"status": "ok"}

