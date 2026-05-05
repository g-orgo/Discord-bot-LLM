# Decisões — raptor-chatbot-llm

## LLM local com Ollama
Uso do Ollama rodando localmente, sem dependência de API cloud (OpenAI, Anthropic, etc.).

## Modelo padrão
`qwen2.5:1.5b` como modelo default, escolhido por melhor equilibrio local entre RAM, latencia e aderencia ao prompt.

Atualizacao em 2026-05-05: apos benchmark adicional focado em baixo consumo de memoria, o `qwen2.5:1.5b` substituiu o `qwen2.5:7b` como padrao operacional.

## System prompt sem persistência
O system prompt fica em memória (`system_prompt.py`). Reiniciar o container reseta para o padrão. Persistência não foi adicionada intencionalmente.

---

## Camada de tradução + validação de contexto no /chat (2026-04-30)

Antes de passar qualquer mensagem ao LLM via `/chat` e `/chat/stream`, o backend executa duas etapas: tradução para inglês e validação de fidelidade semântica entre original e tradução. Só depois disso a mensagem segue para o processo de linkedinfy no `system_prompt`.

**Motivação:** em alguns casos a tradução literal atenuava ou distorcia contexto emocional/semântico do texto original. Ex: "vocês estão mandando muito mal" perdia parte da intensidade crítica após tradução.

**Implementação:**
- `translation.py` — módulo compartilhado com:
	- `translate_to_english()`
	- `validate_translation_context()`
	- `translate_with_context_validation()`
- `routes/chat.py` — chama `translate_with_context_validation()` antes de `ollama_chat`/`ollama_chat_stream`
- `routes/translate.py` — passa a usar o mesmo pipeline validado
- Detecção de inglês: se o modelo retornar `"ENGLISH"`, a mensagem original é usada sem modificação
- Validação de fidelidade: compara original + tradução candidata e devolve uma versão em inglês corrigida quando houver perda de intenção/tom
- Nenhuma lib externa adicionada — usa o mesmo Ollama/`ollama_generate` já presente no projeto

---

## Escolhido pelo agente AI

- **FastAPI** como framework Python (em vez de Flask, Django, etc.).
- **`stream: false` no Ollama** — resposta aguardada completa antes de retornar ao cliente.
- **Swagger UI em `/docs`** — habilitado automaticamente pelo FastAPI.
