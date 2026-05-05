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
ollama pull qwen2.5:1.5b

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
| `OLLAMA_TIMEOUT` | `300.0` | Request timeout in seconds |
| `OLLAMA_PULL_TIMEOUT` | `600.0` | Model pull timeout in seconds |
| `OLLAMA_KEEP_ALIVE` | `5m` | How long Ollama keeps the model loaded between requests |
| `OLLAMA_LOW_VRAM` | `true` | Enables Ollama low-VRAM mode in request options |
| `DEFAULT_MODEL` | `qwen2.5:1.5b` | Default Ollama model |
| `NUM_PREDICT` | `80` | Max generated tokens per request |
| `NUM_CTX` | `1024` | Context window used in Ollama options |
| `TRANSLATE_EXAMPLES_LIMIT` | `2` | Max few-shot examples injected in translation prompt |
| `CHAT_ENABLE_CONTEXT_GATE` | `false` | Enables extra context-gate pass in `/chat` (higher latency) |
| `CHAT_MIN_ALTERNATIVES` | `1` | Minimum alternatives before forced regeneration in `/chat` |

## Endpoints

### `GET /`
Health check.

---

### `POST /generate`
Generic LLM generation — sends a raw prompt directly to Ollama.

**Body:**
```json
{
  "prompt": "Hello! Who are you?",
  "model": "qwen2.5:7b"
}
```

**Response:**
```json
{
  "model": "qwen2.5:7b",
  "response": "Hello! I am an AI assistant..."
}
```

---

### `POST /chat`
Chat endpoint used by the Discord bot and the web frontend. It now runs the primary pipeline in this order: linkedinfy rewrite -> context gate -> translation.

**Body:**
```json
{
  "message": "How do I stay motivated?",
  "model": "qwen2.5:7b"
}
```

**Response:**
```json
{
  "model": "qwen2.5:7b",
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
data: {"done": true, "model": "qwen2.5:7b"}
```

---

### `GET /benchmark`
Runs a latency/token benchmark directly against Ollama chat.

**Query params:**
- `model` (optional): model alias (default: `DEFAULT_MODEL`)
- `runs` (optional): measured runs (default: `3`)
- `warmup_runs` (optional): non-measured warmups (default: `1`)
- `message` (optional): benchmark prompt

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

---

### `POST /chat/pipeline/linkedinfy`
Runs only the primary linkedinfy rewrite stage.

### `POST /chat/pipeline/context-gate`
Runs the context gate against the original message and a candidate rewrite.

### `POST /chat/pipeline/translate`
Translates the primary rewrite when needed.

These staged endpoints exist so the Discord bot can keep a single visible message updated through the pipeline and stop early after the primary translation when the user does not need extra suggestions.

**Response:**
```json
{ "prompt": "You are a pirate assistant. Respond only in pirate speak." }
```

## Related services

- [`raptor-chatbot`](https://github.com/g-orgo/Discord-bot-studies) — Discord bot that calls `/chat`
- [`raptor-chatbot-web`](https://github.com/g-orgo/Discord-bot-web) — Web frontend that calls `/chat/stream` and `/system-prompt`
