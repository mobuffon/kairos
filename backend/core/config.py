from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "postgresql+asyncpg://kairos:kairos@localhost:5432/kairos"
    redis_url: str = "redis://localhost:6379/0"

    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-20250514"

    telegram_bot_token: str = ""
    telegram_webhook_secret: str = "dev-webhook-secret"
    telegram_webhook_url: str = ""

    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:3000/auth/google/callback"

    jwt_secret: str = "dev-jwt-secret-change-in-production"
    jwt_expiry_days: int = 30

    environment: Literal["local", "staging", "production"] = "local"
    log_level: str = "INFO"
    frontend_url: str = "http://localhost:3000"

    min_suggestion_score: float = 0.55
    scheduler_interval_minutes: int = 30


@lru_cache
def get_settings() -> Settings:
    return Settings()
