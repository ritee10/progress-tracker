# ============================================================
# Middleware — JWT Authentication
# ============================================================

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.utils.jwt import decode_token
from jose import JWTError


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Optional global middleware to attach user payload to request.state.
    Note: Route protection and authorization should still use `Depends()`.
    This just preemptively parses the Authorization header if present.
    """
    async def dispatch(self, request: Request, call_next):
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            try:
                payload = decode_token(token)
                request.state.user = payload
            except JWTError:
                # Malformed or expired token, but we don't block here.
                # Let the router's `Depends(get_current_user)` handle the 401.
                request.state.user = None
        else:
            request.state.user = None

        return await call_next(request)
