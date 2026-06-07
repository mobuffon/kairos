from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

from jose import jwt

from backend.core.config import get_settings


def create_access_token(subject: str, extra: dict[str, Any] | None = None) -> str:
    settings = get_settings()
    expire = datetime.now(UTC) + timedelta(days=settings.jwt_expiry_days)
    payload: dict[str, Any] = {"sub": subject, "exp": expire}
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


def decode_access_token(token: str) -> dict[str, Any]:
    settings = get_settings()
    return jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])


def dev_user_ids() -> dict[str, UUID]:
    """Stable UUIDs for mock/dev users."""
    return {
        "mo": UUID("11111111-1111-4111-8111-111111111111"),
        "anneka": UUID("22222222-2222-4222-8222-222222222222"),
        "darian": UUID("33333333-3333-4333-8333-333333333333"),
    }
