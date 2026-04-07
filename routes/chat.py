from fastapi import APIRouter
from schemas import ChatRequest, ChatResponse
from ollama import ollama_generate
import system_prompt

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    prompt = f"{system_prompt.get()}\n\nMessage: {request.message}"
    response = await ollama_generate(request.model, prompt)
    return ChatResponse(model=request.model, response=response)
