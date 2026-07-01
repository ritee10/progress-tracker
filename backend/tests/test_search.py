import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio

async def test_global_search(client: AsyncClient, token_headers: dict):
    response = await client.get("/api/v1/search?query=test", headers=token_headers)
    assert response.status_code in (200, 401)
    if response.status_code == 200:
        data = response.json()
        assert "items" in data
        assert "total" in data

async def test_topic_search(client: AsyncClient, token_headers: dict):
    response = await client.get("/api/v1/search/topics?query=test", headers=token_headers)
    assert response.status_code in (200, 401)
    if response.status_code == 200:
        data = response.json()
        assert "items" in data
        assert "total" in data

async def test_skill_search(client: AsyncClient, token_headers: dict):
    response = await client.get("/api/v1/search/skills?query=test", headers=token_headers)
    assert response.status_code in (200, 401)
    if response.status_code == 200:
        data = response.json()
        assert "items" in data
        assert "total" in data

async def test_note_search(client: AsyncClient, token_headers: dict):
    response = await client.get("/api/v1/search/notes?query=test", headers=token_headers)
    assert response.status_code in (200, 401)
    if response.status_code == 200:
        data = response.json()
        assert "items" in data
        assert "total" in data

async def test_cross_skill_search(client: AsyncClient, token_headers: dict):
    response = await client.get("/api/v1/search/cross-skill?query=test", headers=token_headers)
    assert response.status_code in (200, 401)
    if response.status_code == 200:
        data = response.json()
        assert "items" in data
        assert "total" in data
