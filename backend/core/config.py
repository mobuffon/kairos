from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

_PLACEHOLDER_VALUES = frozenset({
    "...",
    "sk-ant-...",
    "sk-or-...",
    "change-me-to-random-32-char-string",
})


def _is_real_secret(value: str) -> bool:
    return bool(value.strip()) and value.strip() not in _PLACEHOLDER_VALUES


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "postgresql+asyncpg://kairos:kairos@localhost:5432/kairos"
    redis_url: str = "redis://localhost:6379/0"

    llm_provider: str = ""
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-20250514"
    openrouter_api_key: str = ""
    openrouter_model: str = "anthropic/claude-sonnet-4"

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

    mock_external_apis: bool = False

    @property
    def effective_llm_provider(self) -> Literal["anthropic", "openrouter", "mock"]:
        if self.mock_external_apis:
            return "mock"

        provider = self.llm_provider.strip().lower()
        if provider == "mock":
            return "mock"
        if provider == "openrouter":
            return "openrouter" if _is_real_secret(self.openrouter_api_key) else "mock"
        if provider == "anthropic":
            return "anthropic" if _is_real_secret(self.anthropic_api_key) else "mock"

        if _is_real_secret(self.anthropic_api_key):
            return "anthropic"
        if _is_real_secret(self.openrouter_api_key):
            return "openrouter"
        return "mock"

    @property
    def use_mock_llm(self) -> bool:
        return self.effective_llm_provider == "mock"

    @property
    def use_mock_telegram(self) -> bool:
        return self.mock_external_apis or not _is_real_secret(self.telegram_bot_token)

    @property
    def use_mock_calendar(self) -> bool:
        return self.mock_external_apis or not _is_real_secret(self.google_client_id)


@lru_cache
def get_settings() -> Settings:
    return Settings()
