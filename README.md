# Raptor LLM

Hello World de um sistema LLM com **FastAPI** + **Ollama**.

## Pré-requisitos

- Python 3.11+
- [Ollama](https://ollama.com) instalado e rodando localmente

## Setup

```bash
# Instalar dependências
pip install -r requirements.txt

# Baixar um modelo no Ollama (ex: llama3.2)
ollama pull llama3.2

# Subir o servidor Ollama (se não tiver rodando)
ollama serve
```

## Rodando a API

```bash
python -m uvicorn main:app --reload
```

A API estará disponível em `http://localhost:8000`.

## Endpoints

### `GET /`
Health check.

### `POST /generate`
Gera uma resposta do LLM.

**Body:**
```json
{
  "prompt": "Olá! Quem é você?",
  "model": "llama3.2"
}
```

**Response:**
```json
{
  "model": "llama3.2",
  "response": "Olá! Sou um assistente de IA..."
}
```

## Testando com curl

```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Diga olá em português"}'
```

## Documentação interativa

Acesse `http://localhost:8000/docs` para o Swagger UI.
