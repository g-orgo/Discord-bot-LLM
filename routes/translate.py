from fastapi import APIRouter
from schemas import TranslateRequest, TranslateResponse
from ollama import ollama_generate
from training import load_translate_examples
from config import DEFAULT_MODEL

router = APIRouter()

_TRANSLATE_SYSTEM = (
    "You are a translation tool. Follow these rules exactly:\n"
    "1. If the message is written entirely in English, respond with the single word: ENGLISH\n"
    "2. If the message contains any non-English text, translate the entire message to English. "
    "Output only the translated text — no language names, no explanations, no labels."
    + load_translate_examples()
)


@router.post("/translate", response_model=TranslateResponse)
async def translate(request: TranslateRequest):
    prompt = f"{_TRANSLATE_SYSTEM}\n\nMessage: {request.message}"
    response = await ollama_generate(request.model, prompt)
    return TranslateResponse(model=request.model, response=response.strip())
