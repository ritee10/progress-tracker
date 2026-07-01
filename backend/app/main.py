# ============================================================
# FastAPI Application Entrypoint
# ============================================================

import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.core.constants import API_V1_PREFIX
from app.database.session import engine
from app.middleware.logging import RequestLoggingMiddleware
from app.middleware.rate_limit import RateLimitMiddleware
from app.core.events_registry import register_events

# Routers
from app.routers import (
    achievements,
    auth,
    dashboard,
    leaderboard,
    milestones,
    progress,
    skills,
    streaks,
    tasks,
    users,
    topics,
    progress_engine,
    notes,
    search,
    imports,
)
from app.utils.response import error_response

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle events."""
    # Startup
    settings.validate_production_secrets()
    register_events()
    # In production, migrations should be run via Alembic.
    # Here we just verify the database connection.
    try:
        async with engine.begin() as conn:
            # We can run a dummy query to check connection
            pass
        yield
    finally:
        # Shutdown
        await engine.dispose()


# ── Initialize FastAPI ──────────────────────────────────────

# Disable API docs in production to reduce attack surface
_docs_url = None if settings.is_production else "/docs"
_redoc_url = None if settings.is_production else "/redoc"
_openapi_url = None if settings.is_production else "/openapi.json"

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Backend API for Skill Progress Tracker.",
    lifespan=lifespan,
    docs_url=_docs_url,
    redoc_url=_redoc_url,
    openapi_url=_openapi_url,
)

# ── Middleware ───────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' https://fonts.gstatic.com; connect-src 'self' https:"
        return response

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(RateLimitMiddleware, max_requests=settings.RATE_LIMIT_PER_MINUTE)


# ── Exception Handlers ───────────────────────────────────────
import logging as _logging
_exc_logger = _logging.getLogger("skill_tracker.exceptions")

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Fallback exception handler to ensure standard response shape."""
    # Log the full exception for debugging — never expose to client
    _exc_logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content=error_response(
            message="Internal Server Error",
            errors=[{"detail": "An unexpected error occurred. Please try again later."}],
            status_code=500,
        ),
    )


# ── Include Routers ──────────────────────────────────────────
app.include_router(auth.router, prefix=API_V1_PREFIX)
app.include_router(users.router, prefix=API_V1_PREFIX)
app.include_router(topics.router, prefix=API_V1_PREFIX)
app.include_router(skills.router, prefix=API_V1_PREFIX)
app.include_router(milestones.router, prefix=API_V1_PREFIX)
app.include_router(tasks.router, prefix=API_V1_PREFIX)
app.include_router(progress.router, prefix=API_V1_PREFIX)
app.include_router(progress_engine.router, prefix=API_V1_PREFIX)
app.include_router(streaks.router, prefix=API_V1_PREFIX)
app.include_router(imports.router, prefix=API_V1_PREFIX)
app.include_router(achievements.router, prefix=API_V1_PREFIX)
app.include_router(leaderboard.router, prefix=API_V1_PREFIX)
app.include_router(dashboard.router, prefix=API_V1_PREFIX)
app.include_router(notes.router, prefix=API_V1_PREFIX)
app.include_router(search.router, prefix=API_V1_PREFIX)


@app.get("/health", tags=["System"])
async def health_check():
    """Simple health check endpoint."""
    return {"status": "ok", "timestamp": time.time()}
