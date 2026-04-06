from fastapi import FastAPI
from pydantic import BaseModel
import httpx
import os

SYSTEM_PROMPT = os.getenv(
    "SYSTEM_PROMPT",
    (
        "You are an empathetic and welcoming communication assistant. "
        "Your job is to rewrite the user's message in a warmer, kinder, and more receptive way, keeping the original meaning intact. "
        "Always respond in modern English, regardless of the language the message was written in. "
        "Use a casual, friendly tone — think LinkedIn thought-leader energy, but genuine. "
        "Add a few modern expressions or mild slang if it fits naturally, but don't overdo it. "
        "Reply with the rewritten message only — no explanations, no labels, no extra commentary."
    ),
)

app = FastAPI(title="Raptor LLM", description=SYSTEM_PROMPT)

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
DEFAULT_MODEL = "llama3.2"


class PromptRequest(BaseModel):
    prompt: str
    model: str = DEFAULT_MODEL


class PromptResponse(BaseModel):
    model: str
    response: str


class ChatRequest(BaseModel):
    message: str
    model: str = DEFAULT_MODEL


class ChatResponse(BaseModel):
    model: str
    response: str


class SystemPromptUpdate(BaseModel):
    prompt: str


@app.get("/")
def root():
    return {"message": "Raptor LLM API is running"}


@app.get("/system-prompt")
def get_system_prompt():
    return {"prompt": SYSTEM_PROMPT}


@app.put("/system-prompt")
def update_system_prompt(body: SystemPromptUpdate):
    global SYSTEM_PROMPT
    SYSTEM_PROMPT = body.prompt
    return {"prompt": SYSTEM_PROMPT}


@app.post("/generate", response_model=PromptResponse)
async def generate(request: PromptRequest):
    payload = {
        "model": request.model,
        "prompt": request.prompt,
        "stream": False,
    }

    async with httpx.AsyncClient(timeout=120.0) as client:
        res = await client.post(OLLAMA_URL, json=payload)
        res.raise_for_status()
        data = res.json()

    return PromptResponse(model=request.model, response=data["response"])


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    prompt = f"{SYSTEM_PROMPT}\n\nMessage: {request.message}"
    payload = {
        "model": request.model,
        "prompt": prompt,
        "stream": False,
    }

    async with httpx.AsyncClient(timeout=120.0) as client:
        res = await client.post(OLLAMA_URL, json=payload)
        res.raise_for_status()
        data = res.json()

    return ChatResponse(model=request.model, response=data["response"])
