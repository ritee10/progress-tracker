# ============================================================
# Tests — Notes
# ============================================================

import pytest
import uuid
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


async def test_create_note_leaf_validation(client: AsyncClient, token_headers: dict):
    """Note creation should fail with 404/400 without a valid leaf topic."""
    response = await client.post(
        "/api/v1/notes",
        headers=token_headers,
        json={
            "topic_id": str(uuid.uuid4()),
            "content": "This is a valid note under 100 words."
        }
    )
    # The topic does not exist so 404
    assert response.status_code in (404, 400)


async def test_word_limit_validation(client: AsyncClient, token_headers: dict):
    """Pydantic should reject > 100 words."""
    long_content = " ".join(["word"] * 105)
    response = await client.post(
        "/api/v1/notes",
        headers=token_headers,
        json={
            "topic_id": str(uuid.uuid4()),
            "content": long_content
        }
    )
    assert response.status_code == 422
    assert "Note cannot exceed 100 words" in str(response.json())


async def test_url_limit_validation(client: AsyncClient, token_headers: dict):
    """Pydantic should reject > 2 URLs."""
    response = await client.post(
        "/api/v1/notes",
        headers=token_headers,
        json={
            "topic_id": str(uuid.uuid4()),
            "content": "Look at these docs.",
            "urls": [
                "https://example.com/1",
                "https://example.com/2",
                "https://example.com/3"
            ]
        }
    )
    assert response.status_code == 422
    assert "Maximum 2 URLs allowed" in str(response.json())


async def test_invalid_url_format(client: AsyncClient, token_headers: dict):
    """Pydantic should reject invalid URLs."""
    response = await client.post(
        "/api/v1/notes",
        headers=token_headers,
        json={
            "topic_id": str(uuid.uuid4()),
            "content": "Look at these docs.",
            "urls": [
                "not-a-url"
            ]
        }
    )
    assert response.status_code == 422
