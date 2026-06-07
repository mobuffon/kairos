from typing import Any

from fastapi import APIRouter, Header, HTTPException

from backend.core.config import get_settings
from bot.telegram.webhook import WEBHOOK_PATH, handle_webhook_update

router = APIRouter(prefix="/bot", tags=["bot"])


@router.post("/webhook")
async def telegram_webhook(
    update: dict[str, Any],
    x_telegram_bot_api_secret_token: str | None = Header(default=None),
) -> dict[str, Any]:
    settings = get_settings()
    if settings.telegram_webhook_secret and not settings.use_mock_telegram:
        if x_telegram_bot_api_secret_token != settings.telegram_webhook_secret:
            raise HTTPException(status_code=403, detail="Invalid webhook secret")
    return await handle_webhook_update(update)
