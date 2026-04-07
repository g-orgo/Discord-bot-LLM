from pydantic import BaseModel
from config import DEFAULT_MODEL


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
