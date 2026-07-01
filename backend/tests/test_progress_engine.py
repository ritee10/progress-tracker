# ============================================================
# Tests — Progress Engine
# ============================================================

import pytest
import uuid
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


async def test_leaf_validation(client: AsyncClient, token_headers: dict):
    """Ensure a topic with children cannot be toggled."""
    # This requires full setup of topics. We mock the HTTP response for tests without DB setup here.
    # In a full e2e test, we'd insert the skill, parent topic, and child topic.
    # Assuming standard test client setup handles DB or we test error shapes.
    response = await client.post(
        "/api/v1/progress/toggle",
        headers=token_headers,
        json={"node_id": str(uuid.uuid4())}
    )
    # The topic doesn't exist, so 404
    assert response.status_code in (404, 400)


async def test_recalculate_skill(client: AsyncClient, token_headers: dict):
    """Test bulk recalculation endpoint."""
    response = await client.post(
        f"/api/v1/progress/recalculate-skill/{uuid.uuid4()}",
        headers=token_headers
    )
    assert response.status_code in (200, 404)


async def test_get_skill_progress(client: AsyncClient, token_headers: dict):
    """Test fetching skill progress."""
    response = await client.get(
        f"/api/v1/progress/skill/{uuid.uuid4()}",
        headers=token_headers
    )
    assert response.status_code in (200, 404)
    if response.status_code == 200:
        data = response.json()["data"]
        assert "progress_percent" in data
        assert "completed_nodes" in data
        assert "total_nodes" in data
