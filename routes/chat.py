import json
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from schemas import ChatRequest, ChatResponse
from ollama import ollama_chat, ollama_chat_stream
import system_prompt

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    response = await ollama_chat(request.model, system_prompt.get(), request.message)
    return ChatResponse(model=request.model, response=response)


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    async def event_stream():
        async for token in ollama_chat_stream(request.model, system_prompt.get(), request.message):
            yield f"data: {json.dumps({'token': token})}\n\n"
        yield f"data: {json.dumps({'done': True, 'model': request.model})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
