"""
Integration tests for PokéChat Advisor.
"""
import pytest
from httpx import AsyncClient
from backend.main import app


@pytest.mark.asyncio
async def test_health_endpoint():
    """Test the health check endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "model_loaded" in data
        assert "api_accessible" in data


@pytest.mark.asyncio
async def test_root_endpoint():
    """Test the root endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data


@pytest.mark.asyncio
async def test_chat_endpoint_basic():
    """Test the chat endpoint with a basic query."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        payload = {
            "message": "What's Pikachu's type?",
            "conversation_history": []
        }
        response = await client.post("/api/chat", json=payload, timeout=60.0)
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "cards" in data
        assert "query_used" in data


@pytest.mark.asyncio
async def test_chat_endpoint_with_history():
    """Test the chat endpoint with conversation history."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        payload = {
            "message": "Now tell me about Charizard",
            "conversation_history": [
                {"role": "user", "content": "What's Pikachu's type?"},
                {"role": "assistant", "content": "Pikachu is an Electric-type Pokémon."}
            ]
        }
        response = await client.post("/api/chat", json=payload, timeout=60.0)
        assert response.status_code == 200
        data = response.json()
        assert "response" in data


@pytest.mark.asyncio
async def test_chat_endpoint_no_results():
    """Test the chat endpoint when no cards are found."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        payload = {
            "message": "Show me Pokémon named XYZ123NOTREAL",
            "conversation_history": []
        }
        response = await client.post("/api/chat", json=payload, timeout=60.0)
        assert response.status_code == 200
        data = response.json()
        assert "rephrase" in data["response"].lower() or "couldn't find" in data["response"].lower()


@pytest.mark.asyncio
async def test_test_endpoint():
    """Test the test endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/test")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"