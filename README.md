# Raptor LLM

LLM API server that acts as a translation layer between the Raptor services and a local [Ollama](https://ollama.com) instance. Handles AI chat, streaming responses, and a configurable system prompt.

## Stack

Python · FastAPI · Ollama · httpx · uvicorn

## Prerequisites

- Python 3.11+
- [Ollama](https://ollama.com) installed and running locally

## Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Pull the default model
ollama pull llama3.2:3b

# Start Ollama (if not running as a service)
ollama serve
```

## Running the server

```bash
# Development (auto-reload)
uvicorn main:app --reload

# Production
uvicorn main:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`.  
Interactive docs (Swagger UI): `http://localhost:8000/docs`

## Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_URL` | `http://localhost:11434/api/generate` | Ollama generate endpoint |
| `CORS_ORIGIN` | `http://localhost:5173` | Allowed CORS origin |
| `OLLAMA_TIMEOUT` | `120.0` | Request timeout in seconds |
| `OLLAMA_PULL_TIMEOUT` | `600.0` | Model pull timeout in seconds |
| `DEFAULT_MODEL` | `llama3.2:3b` | Default Ollama model (hardcoded in `config.py`) |

## Endpoints

### `GET /`
Health check.

---

### `POST /generate`
Generic LLM generation — sends a raw prompt directly to Ollama.

**Body:**
```json
{
  "prompt": "Olá! Quem é você?",
  "model": "llama3.2:3b"
}
```

**Response:**
```json
{
  "model": "llama3.2:3b",
  "response": "Olá! Sou um assistente de IA..."
}
```

---

### `POST /chat`
Chat endpoint used by the Discord bot's `/ask` command and the web frontend. Prepends the active system prompt to the message before calling Ollama.

**Body:**
```json
{
  "message": "How do I stay motivated?",
  "model": "llama3.2:3b"
}
```

**Response:**
```json
{
  "model": "llama3.2:3b",
  "response": "Staying motivated is all about..."
}
```

---

### `POST /chat/stream`
Streaming version of `/chat`. Returns a `text/event-stream` response where each event delivers one token:

```
data: {"token": "Staying"}
data: {"token": " motivated"}
...
data: {"done": true, "model": "llama3.2:3b"}
```

---

### `GET /system-prompt`
Returns the current system prompt.

**Response:**
```json
{ "prompt": "You are an empathetic and welcoming communication assistant..." }
```

---

### `PUT /system-prompt`
Updates the active system prompt (in-memory, resets on server restart).

**Body:**
```json
{ "prompt": "You are a pirate assistant. Respond only in pirate speak." }
```

**Response:**
```json
{ "prompt": "You are a pirate assistant. Respond only in pirate speak." }
```

## Related services

- [`raptor-chatbot`](https://github.com/g-orgo/Discord-bot-studies) — Discord bot that calls `/chat`
- [`raptor-chatbot-web`](https://github.com/g-orgo/Discord-bot-web) — Web frontend that calls `/chat/stream` and `/system-prompt`
