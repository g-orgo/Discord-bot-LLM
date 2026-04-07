from fastapi import APIRouter
from schemas import SystemPromptUpdate
import system_prompt

router = APIRouter()


@router.get("/system-prompt")
def get_system_prompt():
    return {"prompt": system_prompt.get()}


@router.put("/system-prompt")
def update_system_prompt(body: SystemPromptUpdate):
    system_prompt.set(body.prompt)
    return {"prompt": system_prompt.get()}
