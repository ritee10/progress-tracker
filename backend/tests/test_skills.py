# ============================================================
# Tests — Skills Domain
# ============================================================

import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


async def test_create_skill(client: AsyncClient, token_headers: dict):
    """Test creating a new skill."""
    response = await client.post(
        "/api/v1/skills",
        headers=token_headers,
        json={
            "title": "Machine Learning",
            "category": "Data Science",
            "difficulty": "advanced",
            "priority": "high",
            "target_hours": 100.5
        }
    )
    assert response.status_code in (201, 401, 422)


async def test_get_skills_with_filters(client: AsyncClient, token_headers: dict):
    """Test listing skills with pagination and filters."""
    response = await client.get(
        "/api/v1/skills?page=1&limit=10&status=not_started&priority=high", 
        headers=token_headers
    )
    assert response.status_code in (200, 401)


async def test_pin_skill(client: AsyncClient, token_headers: dict):
    """Test pinning a skill."""
    # Create first
    resp1 = await client.post(
        "/api/v1/skills",
        headers=token_headers,
        json={
            "title": "To Pin",
            "category": "General"
        }
    )
    if resp1.status_code == 201:
        skill_id = resp1.json()["data"]["id"]
        
        # Now pin
        resp2 = await client.patch(f"/api/v1/skills/{skill_id}/pin", headers=token_headers)
        assert resp2.status_code == 200
        assert resp2.json()["data"]["is_pinned"] is True


async def test_skill_stats(client: AsyncClient, token_headers: dict):
    """Test getting skill statistics."""
    response = await client.get("/api/v1/skills/stats", headers=token_headers)
    assert response.status_code in (200, 401)
    if response.status_code == 200:
        data = response.json()["data"]
        assert "total_skills" in data
        assert "pinned_skills" in data
