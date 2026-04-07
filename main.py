from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import CORS_ORIGIN
from routes.generate import router as generate_router
from routes.chat import router as chat_router
from routes.system_prompt import router as system_prompt_router

app = FastAPI(title="Raptor LLM")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[CORS_ORIGIN],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(generate_router)
app.include_router(chat_router)
app.include_router(system_prompt_router)


@app.get("/")
def root():
    return {"message": "Raptor LLM API is running"}

