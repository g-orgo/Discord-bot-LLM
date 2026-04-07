from fastapi import APIRouter
from schemas import PromptRequest, PromptResponse
from ollama import ollama_generate

router = APIRouter()


@router.post("/generate", response_model=PromptResponse)
async def generate(request: PromptRequest):
    response = await ollama_generate(request.model, request.prompt)
    return PromptResponse(model=request.model, response=response)
