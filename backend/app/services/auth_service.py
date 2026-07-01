# ============================================================
# Service — Authentication
# ============================================================

import hashlib
import uuid
from datetime import datetime, timezone
from typing import Sequence

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from app.core.config import get_settings
from app.utils.jwt import (
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.utils.security import hash_password, verify_password, validate_password_strength
from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.utils.date_utils import utc_now

settings = get_settings()


class AuthService:
    """Business logic for authentication flows, Google OAuth, and Session Management."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)

    async def register(self, data: RegisterRequest) -> TokenResponse:
        """Register a new user account with Email/Password."""
        # Check email uniqueness
        if await self.user_repo.email_exists(data.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email is already registered",
            )

        # Validate password strength
        is_valid, error_msg = validate_password_strength(data.password)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg,
            )

        # Generate unique placeholder username
        base_username = data.name.lower().replace(" ", "_")
        unique_username = f"{base_username}_{str(uuid.uuid4())[:8]}"

        # Create user
        user = User(
            email=data.email,
            username=unique_username,
            full_name=data.name,
            password_hash=hash_password(data.password),
            provider="EMAIL",
            role="USER",
            is_active=True,
            is_verified=False,
        )
        user = await self.user_repo.create(user)

        return await self._generate_and_save_tokens(user)

    async def login(self, data: LoginRequest) -> TokenResponse:
        """Authenticate with email and password."""
        user = await self.user_repo.get_by_email(data.email)

        if user is None or user.password_hash is None or not verify_password(data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is deactivated",
            )

        user.last_login_at = utc_now()
        await self.user_repo.update(user)

        return await self._generate_and_save_tokens(user)

    async def google_login(self, token: str) -> TokenResponse:
        """Authenticate using Google OAuth ID token."""
        try:
            # Verify the token with Google
            idinfo = id_token.verify_oauth2_token(
                token, 
                google_requests.Request(), 
                settings.GOOGLE_CLIENT_ID
            )
            
            google_id = idinfo['sub']
            email = idinfo['email']
            name = idinfo.get('name', 'Google User')
            avatar_url = idinfo.get('picture')

        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Google token",
            )

        # Check if user exists by google_id or email
        result = await self.db.execute(
            select(User).where(
                (User.google_id == google_id) | (User.email == email)
            )
        )
        user = result.scalar_one_or_none()

        if user:
            # Update google_id and provider if missing (e.g. linked existing email to Google)
            if not user.google_id:
                user.google_id = google_id
                user.provider = "GOOGLE"
            
            user.last_login_at = utc_now()
            await self.user_repo.update(user)
        else:
            # Create new user
            base_username = name.lower().replace(" ", "_")
            unique_username = f"{base_username}_{str(uuid.uuid4())[:8]}"

            user = User(
                email=email,
                username=unique_username,
                full_name=name,
                avatar_url=avatar_url,
                google_id=google_id,
                provider="GOOGLE",
                role="USER",
                is_active=True,
                is_verified=True,  # Google emails are pre-verified
                last_login_at=utc_now()
            )
            user = await self.user_repo.create(user)

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is deactivated",
            )

        return await self._generate_and_save_tokens(user)

    @staticmethod
    def _hash_token(token: str) -> str:
        """Hash a token using SHA-256 for secure storage."""
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    async def refresh(self, refresh_token: str) -> TokenResponse:
        """Token Rotation: Exchange valid refresh token for a new pair."""
        try:
            payload = decode_token(refresh_token, is_refresh=True)
            if payload.get("type") != "refresh":
                raise ValueError("Invalid token type")
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
            )

        # Invalidate old refresh token (Token Rotation)
        token_hash = self._hash_token(refresh_token)
        result = await self.db.execute(
            select(RefreshToken).where(
                RefreshToken.token_hash == token_hash,
                RefreshToken.is_revoked == False
            )
        )
        old_token_record = result.scalar_one_or_none()
        
        if not old_token_record:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token revoked or not found",
            )
            
        old_token_record.is_revoked = True
        
        user = await self.user_repo.get_by_id(uuid.UUID(payload["sub"]))
        if user is None or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
            )

        return await self._generate_and_save_tokens(user)

    async def logout(self, refresh_token: str) -> None:
        """Revoke a specific refresh token."""
        token_hash = self._hash_token(refresh_token)
        result = await self.db.execute(
            select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        )
        token_record = result.scalar_one_or_none()
        if token_record:
            token_record.is_revoked = True
            await self.db.flush()

    async def get_active_sessions(self, user_id: uuid.UUID) -> Sequence[RefreshToken]:
        """Return all active sessions for a user."""
        result = await self.db.execute(
            select(RefreshToken).where(
                RefreshToken.user_id == user_id,
                RefreshToken.is_revoked == False,
                RefreshToken.expires_at > utc_now()
            )
        )
        return result.scalars().all()

    async def _generate_and_save_tokens(self, user: User) -> TokenResponse:
        """Generate access/refresh tokens and save refresh token hash to DB for session tracking."""
        access_token = create_access_token(
            subject=str(user.id),
            extra_claims={"role": user.role, "email": user.email},
        )
        refresh_token_str = create_refresh_token(subject=str(user.id))

        # Decode to get the exact expiration timestamp for the DB
        refresh_payload = decode_token(refresh_token_str, is_refresh=True)
        expires_at = datetime.fromtimestamp(refresh_payload["exp"], tz=timezone.utc)

        # Save hashed token to database (never store raw JWTs)
        db_token = RefreshToken(
            user_id=user.id,
            token_hash=self._hash_token(refresh_token_str),
            expires_at=expires_at,
            is_revoked=False
        )
        self.db.add(db_token)
        await self.db.flush()

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token_str,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )
