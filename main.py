from fastapi import FastAPI
from pydantic import BaseModel
import httpx
import os

app = FastAPI(title="Raptor LLM", description="LLM API server for raptor-chatbot — powered by Ollama")

OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "llama3.2"

SYSTEM_PROMPT = os.getenv(
    "SYSTEM_PROMPT",
    (
        "Você é um assistente de comunicação empático e acolhedor. "
        "Sua função é reescrever mensagens tornando-as mais gentis, calorosas e receptivas, "
        "mantendo o sentido original. "
        "Responda apenas com a mensagem reescrita, sem explicações adicionais."
    ),
)


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
    prompt = f"{SYSTEM_PROMPT}\n\nMensagem: {request.message}"
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
