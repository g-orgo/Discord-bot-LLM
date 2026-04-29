# Raptor LLM — Operations Guide

**Last Updated:** 2026-04-27

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Start Ollama (required)
ollama serve

# In another terminal: Pull the default model
ollama pull qwen2.5:7b

# Start the API server
uvicorn main:app --reload
```

Server runs on `http://localhost:8000` with interactive docs at `/docs`.

---

## Dual-Mode Feature: Translation + LinkedIn Formatting

### What It Does

The `/chat` endpoint automatically:
1. **Translates input to English** (from any language)
2. **Reformats to professional LinkedIn tone** (in a single LLM operation)

This happens in **ONE PASS** for speed (~2.5s latency).

### Example

**Input (Portuguese, casual):**
```
"Isto deveria estar em inglês e legal"
```

**Output (English, professional):**
```
"This should be presented in English with a professional and appropriate tone."
```

### Controlling This Feature

The behavior is controlled by the **system prompt** (stored in `config.py`).

**View current prompt:**
```bash
curl http://localhost:8000/system-prompt
```

**Update at runtime (temporary - lost on restart):**
```bash
curl -X PUT http://localhost:8000/system-prompt \
  -H "Content-Type: application/json" \
  -d '{ "prompt": "Your new prompt here..." }'
```

**Make permanent changes:** Edit `config.py`, line 12-19 (SYSTEM_PROMPT_DEFAULT).

### Why It Works

- Single unified instruction to the LLM (not two separate operations)
- Prompt explicitly says "Do this in ONE PASS"
- Dramatically reduces processing time
- Maintains both translation accuracy and tone consistency

### Performance Benchmarks

| Operation | Latency | Tokens |
|-----------|---------|--------|
| Translation only | ~1.5s | 80-120 |
| LinkedIn formatting only | ~1.5s | 60-100 |
| **Both (one-pass)** | **~2.5s** | **140-180** |
| Sequential (two passes) | ~4-5s | 260-320 |

---

## Key Conventions

### `/chat` vs `/generate`

- **`/chat`** — Uses system prompt (translation + formatting)
  - Body: `{ "message": "...", "model": "qwen2.5:7b" }`
  - Returns: `{ "model": "...", "response": "..." }`

- **`/generate`** — Raw prompt, no system prompt
  - Body: `{ "prompt": "...", "model": "qwen2.5:7b" }`
  - Returns: `{ "model": "...", "response": "..." }`

### Streaming

For real-time token output (useful for web UI):

```bash
curl -X POST http://localhost:8000/chat/stream \
  -H "Content-Type: application/json" \
  -d '{ "message": "Hello", "model": "qwen2.5:7b" }'
```

Returns Server-Sent Events (SSE) stream:
```
data: {"token":"This"}
data: {"token":" is"}
data: {"token":" a"}
...
data: {"done":true,"model":"qwen2.5:7b"}
```

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_URL` | `http://localhost:11434/api/generate` | Ollama endpoint |
| `DEFAULT_MODEL` | `qwen2.5:7b` | Default model for requests |
| `OLLAMA_TIMEOUT` | `120.0` | Generation timeout (seconds) |
| `OLLAMA_PULL_TIMEOUT` | `600.0` | Model pull timeout (seconds) |
| `CORS_ORIGIN` | `http://localhost:5173` | Allowed CORS origin (Vite dev server) |
| `SYSTEM_PROMPT` | `(default dual-mode)` | Override system prompt at startup |

### Example `.env` for Production

```
OLLAMA_URL=http://ollama-service:11434/api/generate
DEFAULT_MODEL=qwen2.5:7b
OLLAMA_TIMEOUT=180.0
CORS_ORIGIN=https://your-domain.com
```

---

## Troubleshooting

### Model Not Found on Startup

The server auto-pulls the default model if missing. If it fails:

```bash
ollama pull qwen2.5:7b
```

### Slow Responses

1. Check Ollama is running: `curl http://localhost:11434/api/tags`
2. Check available RAM (model needs ~5GB)
3. Verify model is loaded: `ollama list`

### Translation Quality Issues

If output isn't in English or professional tone:
1. Verify system prompt is set correctly: `curl http://localhost:8000/system-prompt`
2. Test with `/generate` to isolate LLM behavior from prompt
3. Check Ollama model version: `ollama show qwen2.5:7b`

---

## Endpoints Reference

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/` | Health check |
| `GET` | `/system-prompt` | View current system prompt |
| `PUT` | `/system-prompt` | Update system prompt (runtime, in-memory) |
| `POST` | `/generate` | Raw LLM generation (no system prompt) |
| `POST` | `/chat` | Chat with translation + formatting (system prompt injected) |
| `POST` | `/chat/stream` | Streaming chat (SSE, same system prompt) |

Interactive Swagger UI: `http://localhost:8000/docs`

---

## Important Notes

⚠️ **System prompt is in-memory** — Changes via `PUT /system-prompt` are lost on restart. Permanent changes require editing `config.py`.

⚠️ **No authentication** — `GET /system-prompt` is publicly readable. Safe for local dev; secure if behind reverse proxy with auth.

⚠️ **One-pass optimization** — Prompt explicitly instructs "DO THIS IN ONE PASS". If you need sequential operations, you must rewrite the system prompt and accept 2x latency.

---

## Monitoring & Logging

The server logs model startup and generation requests:

```
[startup] Model 'qwen2.5:7b' is already installed.
[2026-04-27 10:15:22] POST /chat - 2.543s - "Isto deveria estar em inglês e legal"
```

For debugging, run with `--log-level debug`:

```bash
uvicorn main:app --reload --log-level debug
```
