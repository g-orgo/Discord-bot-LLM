# Decisões — raptor-chatbot-llm

## LLM local com Ollama
Uso do Ollama rodando localmente, sem dependência de API cloud (OpenAI, Anthropic, etc.).

## Modelo padrão
`llama3.2:3b` como modelo default — leve o suficiente para rodar local.

## System prompt sem persistência
O system prompt fica em memória (`system_prompt.py`). Reiniciar o container reseta para o padrão. Persistência não foi adicionada intencionalmente.

---

## Escolhido pelo agente AI

- **FastAPI** como framework Python (em vez de Flask, Django, etc.).
- **`stream: false` no Ollama** — resposta aguardada completa antes de retornar ao cliente.
- **Swagger UI em `/docs`** — habilitado automaticamente pelo FastAPI.
