"""Integration tests for FastAPI routes with mocked Ollama."""
from unittest.mock import AsyncMock, patch
import httpx
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


# ── Health check ──────────────────────────────────────────────
def test_root_health_check():
    res = client.get("/")
    assert res.status_code == 200
    assert "running" in res.json()["message"].lower()


# ── System prompt ─────────────────────────────────────────────
def test_get_system_prompt_returns_string():
    res = client.get("/system-prompt")
    assert res.status_code == 200
    assert isinstance(res.json()["prompt"], str)


def test_put_system_prompt_updates_value():
    res = client.put("/system-prompt", json={"prompt": "Be concise."})
    assert res.status_code == 200
    assert res.json()["prompt"] == "Be concise."

    verify = client.get("/system-prompt")
    assert verify.json()["prompt"] == "Be concise."


def test_put_system_prompt_allows_empty_string():
    res = client.put("/system-prompt", json={"prompt": ""})
    assert res.status_code == 200


# ── /chat (mocked Ollama) ─────────────────────────────────────
@patch("routes.chat._translate_message", new_callable=AsyncMock)
@patch("routes.chat._context_gate_response", new_callable=AsyncMock)
@patch("routes.chat._linkedinfy_message", new_callable=AsyncMock)
def test_chat_returns_response(mock_linkedinfy, mock_context_gate, mock_translate):
    mock_linkedinfy.return_value = "How are you?"
    mock_context_gate.return_value = "How are you?"
    mock_translate.return_value = "I'm doing well!"

    res = client.post("/chat", json={"message": "How are you?"})
    assert res.status_code == 200
    assert res.json()["response"] == "I'm doing well!"
    assert "model" in res.json()
    mock_linkedinfy.assert_awaited_once()
    mock_context_gate.assert_awaited_once()
    mock_translate.assert_awaited_once()


@patch("routes.chat._translate_message", new_callable=AsyncMock)
@patch("routes.chat._context_gate_response", new_callable=AsyncMock)
@patch("routes.chat.ollama_chat", new_callable=AsyncMock)
def test_chat_retries_transient_http_500(mock_ollama_chat, mock_context_gate, mock_translate):
    request = httpx.Request("POST", "http://ollama.local/api/chat")
    response = httpx.Response(500, request=request)
    mock_ollama_chat.side_effect = [
        httpx.HTTPStatusError("internal", request=request, response=response),
        "I'm doing well!",
    ]
    mock_context_gate.return_value = "I'm doing well!"
    mock_translate.return_value = "I'm doing well!"

    res = client.post("/chat", json={"message": "How are you?"})

    assert res.status_code == 200
    assert res.json()["response"] == "I'm doing well!"
    assert mock_ollama_chat.await_count == 2


def test_chat_rejects_empty_message():
    res = client.post("/chat", json={"message": ""})
    assert res.status_code == 422  # Pydantic validation


# ── /generate (mocked Ollama) ─────────────────────────────────
@patch("routes.generate.ollama_generate", new_callable=AsyncMock)
def test_generate_returns_response(mock_generate):
    mock_generate.return_value = "Paris is the capital of France."

    res = client.post("/generate", json={"prompt": "Capital of France?"})
    assert res.status_code == 200
    assert res.json()["response"] == "Paris is the capital of France."
