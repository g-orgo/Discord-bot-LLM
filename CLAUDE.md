# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the API server (development)
uvicorn main:app --reload

# Run the API server (production)
uvicorn main:app --host 0.0.0.0 --port 8000
```

No test suite is configured.

## Local development setup

Requires [Ollama](https://ollama.com) installed and running locally.

```bash
# Pull a model
ollama pull qwen2.5:7b

# Start Ollama (if not running as a service)
ollama serve
```

Ollama listens on `http://localhost:11434` by default.

## Architecture

Single-file FastAPI application (`main.py`) that proxies prompts to a local Ollama instance.

**Request flow:**
1. Client sends `POST /generate` with `{ prompt, model }`
2. `main.py` forwards the request to Ollama's `/api/generate` endpoint with `stream: false`
3. Ollama response is unwrapped and returned as `{ model, response }`

**Key constants in `main.py`:**
- `OLLAMA_URL` — Ollama endpoint (`http://localhost:11434/api/generate`)
- `DEFAULT_MODEL` — default model used when `model` is not specified (`qwen2.5:7b`)

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Health check |
| `POST` | `/generate` | Generate a response from the LLM (generic) |
| `POST` | `/chat` | Chat endpoint used by raptor-chatbot `/ask` command |

Interactive docs available at `http://localhost:8000/docs` (Swagger UI).
