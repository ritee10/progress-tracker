# ============================================================
# Core Configuration — Environment & Application Settings
# ============================================================
# Central configuration loaded from environment variables.
# Uses pydantic-settings for type-safe, validated config.
# ============================================================

from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables / .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ──────────────────────────────────────────
    APP_NAME: str = "Skill Progress Tracker"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    DEBUG: bool = True

    # ── Database ─────────────────────────────────────────────
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/skill_tracker"
    DATABASE_URL_SYNC: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/skill_tracker"

    # ── Security / JWT ───────────────────────────────────────
    SECRET_KEY: str = "change-me-to-a-random-64-char-string-in-production"
    JWT_SECRET_KEY: str = "change-me-to-a-random-64-char-string-in-production"
    JWT_REFRESH_SECRET: str = "change-me-to-a-random-refresh-secret-string"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # ── Google OAuth ─────────────────────────────────────────
    GOOGLE_CLIENT_ID: str = "your-google-client-id"
    GOOGLE_CLIENT_SECRET: str = "your-google-client-secret"

    # ── Redis ────────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"

    # ── Celery ───────────────────────────────────────────────
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # ── CORS ─────────────────────────────────────────────────
    #CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    from typing import List

    CORS_ORIGINS: List[str] = ["*"]

    # ── Rate Limiting ────────────────────────────────────────
    RATE_LIMIT_PER_MINUTE: int = 100

    # ── Supabase / Storage ───────────────────────────────────
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    STORAGE_BUCKET_UPLOADS: str = "uploads"

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"

    @property
    def is_development(self) -> bool:
        return self.APP_ENV == "development"

    def validate_production_secrets(self) -> None:
        """Fail-safe: Ensure default/placeholder secrets are not used in production."""
        if not self.is_production:
            return
        _dangerous_defaults = {"change-me", "your-", "secret", "placeholder"}
        for field_name in ("SECRET_KEY", "JWT_SECRET_KEY", "JWT_REFRESH_SECRET"):
            value = getattr(self, field_name, "")
            if any(d in value.lower() for d in _dangerous_defaults) or len(value) < 32:
                raise ValueError(
                    f"FATAL: {field_name} is using a default/weak value in production. "
                    f"Generate a secure key with: openssl rand -hex 32"
                )


@lru_cache()
def get_settings() -> Settings:
    """Cached settings singleton — parsed once, reused everywhere."""
    return Settings()
