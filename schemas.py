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


class SuggestionsRequest(BaseModel):
    original_message: str = Field(..., min_length=1, max_length=10000)
    primary_message: str = Field(..., min_length=1, max_length=10000)
    model: str = DEFAULT_MODEL


class SuggestionsFinalizeRequest(BaseModel):
    original_message: str = Field(..., min_length=1, max_length=10000)
    suggestions: list[str] = Field(..., min_length=1, max_length=10)
    model: str = DEFAULT_MODEL


class SuggestionsResponse(BaseModel):
    model: str
    suggestions: list[str]


class SystemPromptUpdate(BaseModel):
    prompt: str


class TranslateRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=10000)
    model: str = DEFAULT_MODEL


class TranslateResponse(BaseModel):
    model: str
    response: str
