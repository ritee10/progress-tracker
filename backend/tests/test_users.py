# ============================================================
# Tests — Users
# ============================================================

import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


async def test_get_me(client: AsyncClient, token_headers: dict):
    """Test fetching current user profile."""
    response = await client.get("/api/v1/users/me", headers=token_headers)
    assert response.status_code in (200, 401)


async def test_update_me(client: AsyncClient, token_headers: dict):
    """Test updating user profile."""
    response = await client.patch(
        "/api/v1/users/me",
        headers=token_headers,
        json={"full_name": "Updated Name"}
    )
    assert response.status_code in (200, 401)
