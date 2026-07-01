# ============================================================
# Schemas — Authentication
# ============================================================

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    """POST /auth/register request body."""
    email: EmailStr
    name: str = Field(..., min_length=2, max_length=100)
    password: str = Field(
        ..., min_length=8, max_length=128,
        description="Minimum 8 characters"
    )

class LoginRequest(BaseModel):
    """POST /auth/login request body."""
    email: EmailStr
    password: str

class GoogleLoginRequest(BaseModel):
    """POST /auth/google request body."""
    id_token: str


class RefreshRequest(BaseModel):
    """POST /auth/refresh request body."""
    refresh_token: str


class TokenResponse(BaseModel):
    """JWT token pair returned on login/register/refresh."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = Field(
        description="Access token expiration in seconds"
    )


class TokenPayload(BaseModel):
    """Decoded JWT payload (internal use)."""
    sub: str          # User ID
    exp: int          # Expiration timestamp
    type: str         # "access" or "refresh"
    role: str = "user"
