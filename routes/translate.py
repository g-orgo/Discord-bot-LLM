from fastapi import APIRouter
from schemas import TranslateRequest, TranslateResponse
from translation import translate_with_context_validation

router = APIRouter()


@router.post("/translate", response_model=TranslateResponse)
async def translate(request: TranslateRequest):
    response = await translate_with_context_validation(request.message, request.model)
    return TranslateResponse(model=request.model, response=response)
