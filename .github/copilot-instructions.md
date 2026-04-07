# Raptor LLM — Workspace Guidelines

FastAPI application that proxies prompts to a local Ollama instance. Used as the dedicated LLM backend for the `raptor-chatbot` Discord bot.

## Build & Run

```bash
# Install dependencies
pip install -r requirements.txt

# Run (development, with auto-reload)
uvicorn main:app --reload

# Run (production)
uvicorn main:app --host 0.0.0.0 --port 8000
```

No test suite is configured.

**Local dev:** Requires [Ollama](https://ollama.com) running locally on `http://localhost:11434`.

```bash
ollama pull llama3.2:3b   # pull the default model
ollama serve           # start Ollama if not running as a service
```

## Architecture

Single-file FastAPI application (`main.py`).

**Request flow (`/chat`):**
1. raptor-chatbot sends `POST /chat` with `{ message }`
2. `main.py` prepends `SYSTEM_PROMPT` and forwards to Ollama's `/api/generate` with `stream: false`
3. Ollama response is unwrapped and returned as `{ model, response }`

**Key constants in `main.py`:**
- `OLLAMA_URL` — `http://localhost:11434/api/generate`
- `DEFAULT_MODEL` — `llama3.2:3b`
- `SYSTEM_PROMPT` — configurable via `SYSTEM_PROMPT` env var or `PUT /system-prompt` at runtime
- `OLLAMA_TIMEOUT` — httpx timeout for generation requests (default `120.0`s, configurable via env var)
- `OLLAMA_PULL_TIMEOUT` — timeout for model pull at startup (default `600.0`s, configurable via env var)

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Health check |
| `GET` | `/system-prompt` | Returns the current system prompt |
| `PUT` | `/system-prompt` | Updates the system prompt in runtime (body: `{ prompt }`) |
| `POST` | `/generate` | Generic LLM generation — no system prompt injected |
| `POST` | `/chat` | Chat endpoint for raptor-chatbot — system prompt injected, returns full response |
| `POST` | `/chat/stream` | Streaming chat — returns SSE tokens as they are generated |

Interactive docs: `http://localhost:8000/docs`

## Key Conventions

**Single-file app.** Keep all logic in `main.py` unless explicitly asked to split.

**Pydantic models for all I/O.** Every request and response must use a typed Pydantic model.

**Async routes.** All endpoints that call Ollama must be `async def` with `httpx.AsyncClient`.

**System prompt is in-memory.** `SYSTEM_PROMPT` resets on restart — no persistence without discussion.

**`/chat` vs `/generate`:** `/chat` always injects the system prompt. `/generate` is a raw proxy — do not add system prompt to it.

**Required `.env` variables:** `SYSTEM_PROMPT` (optional, has default).

## Dev Skill (always apply)

Before any code change in this workspace, load and follow the dev skill:
`e:/raptor/.claude/skills/dev/SKILL.md`
