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


class SystemPromptUpdate(BaseModel):
    prompt: str
