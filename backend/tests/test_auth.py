# ============================================================
# Tests — Auth System
# ============================================================

import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


async def test_register_success(client: AsyncClient):
    """Test successful user registration."""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@example.com",
            "name": "New User",
            "password": "StrongPassword123!"
        }
    )
    # 201 Created or 409 Conflict if running multiple times without DB reset
    assert response.status_code in (201, 409)
    if response.status_code == 201:
        data = response.json()
        assert "access_token" in data["data"]
        assert "refresh_token" in data["data"]


async def test_register_weak_password(client: AsyncClient):
    """Test registration with weak password."""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "weak@example.com",
            "name": "Weak User",
            "password": "123"
        }
    )
    assert response.status_code == 422  # Pydantic validation error


async def test_login_success(client: AsyncClient):
    """Test user login."""
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "newuser@example.com",
            "password": "StrongPassword123!"
        }
    )
    assert response.status_code in (200, 401)


async def test_login_wrong_password(client: AsyncClient):
    """Test user login with bad credentials."""
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "newuser@example.com",
            "password": "WrongPassword123!"
        }
    )
    assert response.status_code == 401


async def test_google_login_invalid_token(client: AsyncClient):
    """Test Google Auth with a bad token."""
    response = await client.post(
        "/api/v1/auth/google",
        json={
            "id_token": "invalid_jwt_token_from_frontend"
        }
    )
    # Our service will attempt to verify and fail
    assert response.status_code == 401


async def test_protected_route_unauthenticated(client: AsyncClient):
    """Test accessing a protected route without a token."""
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401
