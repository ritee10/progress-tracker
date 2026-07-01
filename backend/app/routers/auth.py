# ============================================================
# Router — Authentication
# ============================================================

from fastapi import APIRouter

from app.core.dependencies import CurrentUser, DBSession
from app.schemas.auth import LoginRequest, RefreshRequest, RegisterRequest, TokenResponse, GoogleLoginRequest
from app.schemas.user import UserResponse
from app.services.auth_service import AuthService
from app.utils.response import success_response

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=dict,
    status_code=201,
    summary="Register a new user account via Email",
)
async def register(data: RegisterRequest, db: DBSession):
    """Create a new user account. Returns JWT access and refresh tokens."""
    service = AuthService(db)
    tokens = await service.register(data)
    return success_response(data=tokens.model_dump(), message="Registration successful")


@router.post(
    "/login",
    response_model=dict,
    summary="Authenticate with email and password",
)
async def login(data: LoginRequest, db: DBSession):
    """Login with email and password. Returns JWT access and refresh tokens."""
    service = AuthService(db)
    tokens = await service.login(data)
    return success_response(data=tokens.model_dump(), message="Login successful")


@router.post(
    "/google",
    response_model=dict,
    summary="Authenticate via Google OAuth",
)
async def google_login(data: GoogleLoginRequest, db: DBSession):
    """Login using a Google ID token from the frontend."""
    service = AuthService(db)
    tokens = await service.google_login(data.id_token)
    return success_response(data=tokens.model_dump(), message="Google Login successful")


@router.post(
    "/refresh",
    response_model=dict,
    summary="Refresh an expired access token (Token Rotation)",
)
async def refresh(data: RefreshRequest, db: DBSession):
    """Exchange a valid refresh token for a new token pair. Invalidates the old refresh token."""
    service = AuthService(db)
    tokens = await service.refresh(data.refresh_token)
    return success_response(data=tokens.model_dump(), message="Token refreshed")


@router.post(
    "/logout",
    response_model=dict,
    summary="Logout and revoke current refresh token",
)
async def logout(data: RefreshRequest, db: DBSession):
    """Revoke the given refresh token, effectively logging the user out for that session."""
    service = AuthService(db)
    await service.logout(data.refresh_token)
    return success_response(message="Logged out successfully")


@router.get(
    "/sessions",
    response_model=dict,
    summary="Get active sessions",
)
async def get_sessions(current_user: CurrentUser, db: DBSession):
    """Return all active refresh token sessions for the current user."""
    service = AuthService(db)
    sessions = await service.get_active_sessions(current_user.id)
    data = [
        {
            "id": str(s.id),
            "created_at": str(s.created_at),
            "expires_at": str(s.expires_at),
            "device": s.device_info or "Unknown Device"
        }
        for s in sessions
    ]
    return success_response(data=data)


@router.get(
    "/me",
    response_model=dict,
    summary="Get current authenticated user",
)
async def get_me(current_user: CurrentUser):
    """Return the profile of the currently authenticated user."""
    user_data = UserResponse.model_validate(current_user)
    return success_response(data=user_data.model_dump(mode="json"))
