# Context: raptor-llm/main.py

**Date:** 2026-04-06

## Summary
FastAPI app que faz proxy de prompts para Ollama. Expõe endpoints `/generate` (genérico) e `/chat` (usado pelo raptor-chatbot). Suporta system prompt configurável que instrui a LLM a atuar como assistente que torna mensagens mais acolhedoras.

## Architecture
- Arquivo único: `main.py`
- Ollama: `http://localhost:11434/api/generate`, modelo padrão `llama3.2`
- `SYSTEM_PROMPT` global: configurável via env var `SYSTEM_PROMPT` ou via `PUT /system-prompt` em runtime

## Files
- `main.py` — app completo

## Endpoints

| Method | Path | Body | Response | Descrição |
|--------|------|------|----------|-----------|
| `GET` | `/` | — | `{ message }` | Health check |
| `GET` | `/system-prompt` | — | `{ prompt }` | Retorna o system prompt atual |
| `PUT` | `/system-prompt` | `{ prompt }` | `{ prompt }` | Atualiza o system prompt em runtime |
| `POST` | `/generate` | `{ prompt, model? }` | `{ model, response }` | Geração genérica (sem system prompt) |
| `POST` | `/chat` | `{ message, model? }` | `{ model, response }` | Chat com system prompt injetado |

## Models / Schemas
- `PromptRequest` / `PromptResponse` — para `/generate`
- `ChatRequest` / `ChatResponse` — para `/chat`
- `SystemPromptUpdate` — para `PUT /system-prompt`

## Decisions
- `SYSTEM_PROMPT` é uma variável global mutável — permite atualização via `PUT /system-prompt` sem reiniciar o servidor
- O prompt padrão instrui a LLM a reescrever mensagens de forma mais acolhedora, mantendo o sentido original
- `/chat` injeta o system prompt antes da mensagem do usuário no formato: `{SYSTEM_PROMPT}\n\nMensagem: {message}`
- `/generate` não usa system prompt — mantém comportamento genérico

## Known issues / Next steps
- `SYSTEM_PROMPT` é in-memory: resetado ao reiniciar o servidor. Para persistência, seria necessário um arquivo ou banco de dados.
- Considerar expor `GET /system-prompt` apenas internamente se o servidor for público
