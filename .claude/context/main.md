# Context: raptor-llm/main.py

**Date:** 2026-04-06

## Summary
FastAPI app that proxies prompts to Ollama. Exposes `/generate` (generic) and `/chat` (used by raptor-chatbot). Supports a configurable system prompt that instructs the LLM to act as a welcoming communication assistant that always responds in English.

## Architecture
- Single file: `main.py`
- Ollama: configurable via `OLLAMA_URL` env var, default `http://localhost:11434/api/generate`; model default `llama3.2:3b`
- `SYSTEM_PROMPT` global: configurable via `SYSTEM_PROMPT` env var or `PUT /system-prompt` at runtime
- FastAPI `description` is set to `SYSTEM_PROMPT` — visible in Swagger UI at `/docs`

## Endpoints

| Method | Path | Body | Response | Description |
|--------|------|------|----------|-------------|
| `GET` | `/` | — | `{ message }` | Health check |
| `GET` | `/system-prompt` | — | `{ prompt }` | Returns current system prompt |
| `PUT` | `/system-prompt` | `{ prompt }` | `{ prompt }` | Updates system prompt at runtime |
| `POST` | `/generate` | `{ prompt, model? }` | `{ model, response }` | Generic generation (no system prompt) |
| `POST` | `/chat` | `{ message, model? }` | `{ model, response }` | Chat with system prompt injected |

## Models / Schemas
- `PromptRequest` / `PromptResponse` — for `/generate`
- `ChatRequest` / `ChatResponse` — for `/chat`
- `SystemPromptUpdate` — for `PUT /system-prompt`

## Decisions
- `SYSTEM_PROMPT` is a mutable global — allows runtime update via `PUT /system-prompt` without restart
- Default prompt instructs the LLM to rewrite messages warmly, always in modern English
- `/chat` injects the system prompt before the user message: `{SYSTEM_PROMPT}\n\nMessage: {message}`
- `/generate` does not inject system prompt — raw proxy behavior
- `OLLAMA_URL` is now configurable via env var (added in audit run 3)

## Known issues / Next steps
- `SYSTEM_PROMPT` is in-memory — resets on restart
- `GET /system-prompt` has no auth — acceptable for local/dev use only
