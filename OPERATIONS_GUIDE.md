# Raptor LLM - Operations Guide

Last updated: 2026-05-05

## Quick start

```bash
# Install dependencies
pip install -r requirements.txt

# Start Ollama
ollama serve

# Pull default model
ollama pull qwen2.5:1.5b

# Start API
uvicorn main:app --reload
```

Server: http://localhost:8000
Swagger: http://localhost:8000/docs

## Runtime model and pipeline

Current operational defaults:

- DEFAULT_MODEL: qwen2.5:1.5b
- OLLAMA_TIMEOUT: 300.0s
- OLLAMA_PULL_TIMEOUT: 600.0s
- Chat retry: enabled via CHAT_RETRY_ATTEMPTS and CHAT_RETRY_BACKOFF_SECONDS

Primary `/chat` flow:

1. linkedinfy rewrite
2. context gate cleanup
3. translation to final English output

Optional extra alternatives are controlled by config flags and can trigger additional stages when enabled.

## Endpoints

### Health and prompt management

- GET /
- GET /system-prompt
- PUT /system-prompt

### Generic generation

- POST /generate
  - Raw generation, no system prompt injection

### Chat endpoints

- POST /chat
  - Compatibility endpoint returning the primary final response

- POST /chat/stream
  - SSE token streaming for web clients

### Staged chat pipeline endpoints

- POST /chat/pipeline/linkedinfy
- POST /chat/pipeline/context-gate
- POST /chat/pipeline/translate
- POST /chat/pipeline/suggestions
- POST /chat/pipeline/suggestions/finalize

These endpoints exist so the Discord bot can keep one visible message updated and stop early when optional suggestion generation is not needed.

### Benchmark

- GET /benchmark
  - Query params: model, runs, warmup_runs, message

## Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| OLLAMA_URL | http://localhost:11434/api/generate | Ollama generate endpoint |
| OLLAMA_CHAT_URL | http://localhost:11434/api/chat | Ollama chat endpoint |
| DEFAULT_MODEL | qwen2.5:1.5b | Default model alias |
| CORS_ORIGIN | http://localhost:5173 | Allowed CORS origin |
| OLLAMA_TIMEOUT | 300.0 | HTTP read timeout in seconds |
| OLLAMA_PULL_TIMEOUT | 600.0 | Model pull timeout in seconds |
| OLLAMA_KEEP_ALIVE | 5m | Model keep-alive hint to Ollama |
| OLLAMA_LOW_VRAM | true | Enables low VRAM options |
| NUM_PREDICT | 80 | Max prediction tokens |
| NUM_CTX | 1024 | Context window |
| TRANSLATE_EXAMPLES_LIMIT | 2 | Few-shot examples in translation stage |
| CHAT_ENABLE_CONTEXT_GATE | false | Enables optional extra gated alternatives logic |
| CHAT_MIN_ALTERNATIVES | 1 | Minimum alternatives threshold |
| CHAT_RETRY_ATTEMPTS | 2 | Retry attempts for transient failures |
| CHAT_RETRY_BACKOFF_SECONDS | 1.5 | Backoff multiplier in seconds |
| SYSTEM_PROMPT | built-in default | Override initial system prompt at startup |

## Operational notes

- System prompt updates are in-memory and reset on process restart.
- `/chat` and `/chat/stream` are stable client contracts.
- `/chat/pipeline/*` is intended for staged UX orchestration (currently used by the Discord bot).

## Troubleshooting

### Ollama unavailable

Symptoms:

- `/chat` returns HTTP 503
- Logs indicate request or upstream HTTP errors

Checks:

```bash
curl http://localhost:11434/api/tags
ollama list
```

### Slow responses

1. Confirm model is pulled and available locally.
2. Validate hardware constraints (RAM/CPU).
3. If needed, tune `NUM_PREDICT`, `NUM_CTX`, and timeout values.

### Prompt behavior drift

1. Inspect current prompt: `GET /system-prompt`
2. Re-apply expected prompt via `PUT /system-prompt`
3. Validate with both `/chat` and staged pipeline endpoints
