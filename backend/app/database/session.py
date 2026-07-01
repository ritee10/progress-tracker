# ============================================================
# Database — Async Session Factory
# ============================================================
# Provides the async SQLAlchemy engine and session maker.
# Use `get_db()` as a FastAPI dependency for request-scoped sessions.
# ============================================================

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import get_settings

settings = get_settings()

# ── Engine ───────────────────────────────────────────────────
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG and not settings.is_production,  # Never echo SQL in production
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,            # Verify connections before use
    pool_recycle=3600,             # Recycle connections every hour
)

# ── Session Factory ──────────────────────────────────────────
async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,        # Keep objects usable after commit
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that yields a request-scoped async session.

    Usage in routers:
        @router.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
