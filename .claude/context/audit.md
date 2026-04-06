# Audit Summary — Raptor LLM
**Latest run:** April 6, 2026 (run 3)

---

## Run 3 — Language consistency pass

### Fixed

- **Portuguese prompt label in `/chat`** — `"Mensagem: {message}"` changed to `"Message: {message}"`
- **Stale `main.md` context file** — rewritten in English with updated architecture (env vars, system prompt format, FastAPI description)

---

## Health check

| Area | Status | Notes |
|------|--------|-------|
| Endpoint structure | ✅ Good | All 5 endpoints properly defined with typed models |
| System prompt | ✅ Good | Correctly injected in `/chat`, absent in `/generate` |
| Ollama integration | ✅ Good | Async, correct timeout (120s), stream disabled |
| Input validation | ✅ Good | All request bodies use Pydantic models |
| OLLAMA_URL configurable | ✅ Good | Reads from env var with local default |
| English-only output | ✅ Good | System prompt explicitly instructs LLM to reply in English |

---

## Still open (low priority)

- **System prompt resets on restart** — changes via `PUT /system-prompt` are in-memory only
- **`GET /system-prompt` has no auth** — acceptable for local dev use

---

## History
- **Run 1** — No issues found
- **Run 2** — `OLLAMA_URL` env var added; FastAPI description updated
- **Run 3** — Portuguese prompt label fixed; `main.md` context updated

---

## 💡 Things to keep in mind

### 🔓 System prompt is visible to anyone
The `GET /system-prompt` endpoint returns the current system prompt with no password or key. This is fine for internal/dev use, but if the server is ever exposed publicly, the prompt (your "secret instructions" to the AI) would be readable by anyone.

**When to act:** Only if the server leaves localhost.

### 🔄 System prompt resets on restart
Changes made via `PUT /system-prompt` are in-memory — they vanish when the server restarts. The default prompt (the welcoming, empathetic one) is restored from the environment variable or hardcoded default.

**When to act:** Only if you need prompt changes to survive restarts.

---

## 📌 Current system prompt (default)
> "Você é um assistente de comunicação empático e acolhedor. Sua função é reescrever mensagens tornando-as mais gentis, calorosas e receptivas, mantendo o sentido original. Responda apenas com a mensagem reescrita, sem explicações adicionais."
