import json
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from schemas import ChatRequest, ChatResponse
from ollama import ollama_generate, ollama_generate_stream
import system_prompt

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    prompt = f"{system_prompt.get()}\n\nMessage: {request.message}"
    response = await ollama_generate(request.model, prompt)
    return ChatResponse(model=request.model, response=response)


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    prompt = f"{system_prompt.get()}\n\nMessage: {request.message}"

    async def event_stream():
        async for token in ollama_generate_stream(request.model, prompt):
            yield f"data: {json.dumps({'token': token})}\n\n"
        yield f"data: {json.dumps({'done': True, 'model': request.model})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
