from pydantic import BaseModel, Field
from config import DEFAULT_MODEL


class PromptRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=10000)
    model: str = DEFAULT_MODEL


class PromptResponse(BaseModel):
    model: str
    response: str


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=10000)
    model: str = DEFAULT_MODEL


class ChatResponse(BaseModel):
    model: str
    response: str


class ContextGateRequest(BaseModel):
    original_message: str = Field(..., min_length=1, max_length=10000)
    candidate_message: str = Field(..., min_length=1, max_length=10000)
    model: str = DEFAULT_MODEL


class SystemPromptUpdate(BaseModel):
    prompt: str


class TranslateRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=10000)
    model: str = DEFAULT_MODEL


class TranslateResponse(BaseModel):
    model: str
    response: str
