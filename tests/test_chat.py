"""Tests for the secure Insight AI chat endpoint."""
import asyncio
from unittest.mock import AsyncMock, patch

import httpx
import pytest
from fastapi import HTTPException

from src.api.chat import ChatRequest, chat

def valid_payload():
    return ChatRequest(messages=[
        {"role": "user", "content": "Tell me about OULAD"}
    ])

def test_chat_requires_backend_groq_key(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    with pytest.raises(HTTPException) as exc:
        asyncio.run(chat(valid_payload()))
    assert exc.value.status_code == 503
    assert "GROQ_API_KEY" in exc.value.detail

def test_chat_rejects_assistant_only_history():
    with pytest.raises(ValueError):
        ChatRequest(messages=[{"role": "assistant", "content": "Hello"}])

def test_chat_rejects_empty_or_oversized_messages():
    with pytest.raises(ValueError):
        ChatRequest(messages=[{"role": "user", "content": ""}])
    with pytest.raises(ValueError):
        ChatRequest(messages=[
            {"role": "user", "content": "x" * 4001}
        ])

def test_chat_returns_groq_reply_and_passes_student_context(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-secret")
    monkeypatch.setenv("GROQ_MODEL", "test-model")

    mock_response = httpx.Response(
        200,
        json={"choices": [{"message": {"content": "OULAD is an open learning analytics dataset."}}]},
        request=httpx.Request("POST", "https://api.groq.com/openai/v1/chat/completions"),
    )

    class MockAsyncClient:
        def __init__(self, *args, **kwargs):
            pass
        async def __aenter__(self):
            return self
        async def __aexit__(self, *args):
            return False
        async def post(self, url, json, headers):
            assert json["model"] == "test-model"
            assert json["messages"][0]["role"] == "system"
            assert "individual_prediction" in json["messages"][0]["content"]
            assert json["messages"][-1]["content"] == "Tell me about OULAD"
            assert headers["Authorization"] == "Bearer test-secret"
            return mock_response

    with patch("src.api.chat.httpx.AsyncClient", MockAsyncClient):
        result = asyncio.run(chat(ChatRequest(
            messages=[{"role": "user", "content": "Tell me about OULAD"}],
            context={"individual_prediction": {"result": {"flagged_for_review": True}}},
        )))
    assert result.reply.startswith("OULAD is")

def test_chat_handles_groq_timeout(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-secret")

    class TimeoutClient:
        def __init__(self, *args, **kwargs):
            pass
        async def __aenter__(self):
            return self
        async def __aexit__(self, *args):
            return False
        async def post(self, *args, **kwargs):
            raise httpx.ReadTimeout("timed out")

    with patch("src.api.chat.httpx.AsyncClient", TimeoutClient):
        with pytest.raises(HTTPException) as exc:
            asyncio.run(chat(valid_payload()))
    assert exc.value.status_code == 504
