from typing import Any

from fastapi import APIRouter, Header, HTTPException

from backend.core.config import get_settings
from backend.core.logging import get_logger
from bot.telegram.webhook import handle_webhook_update

router = APIRouter(prefix="/bot", tags=["bot"])
logger = get_logger("bot.webhook")


@router.post("/webhook")
async def telegram_webhook(
    update: dict[str, Any],
    x_telegram_bot_api_secret_token: str | None = Header(default=None),
) -> dict[str, Any]:
    settings = get_settings()
    update_id = update.get("update_id")
    text, chat_id = _extract_log_fields(update)
    logger.info(
        "webhook_received",
        update_id=update_id,
        chat_id=chat_id,
        text_preview=(text[:80] if text else None),
        mock=settings.use_mock_telegram,
    )

    if settings.telegram_webhook_secret and not settings.use_mock_telegram:
        if x_telegram_bot_api_secret_token != settings.telegram_webhook_secret:
            logger.warning("webhook_secret_rejected", update_id=update_id)
            raise HTTPException(status_code=403, detail="Invalid webhook secret")

    result = await handle_webhook_update(update)
    logger.info("webhook_handled", **{k: v for k, v in result.items() if k != "ok"})
    return result


def _extract_log_fields(update: dict[str, Any]) -> tuple[str | None, int | None]:
    message = update.get("message") or update.get("edited_message")
    if message:
        return message.get("text"), message.get("chat", {}).get("id")
    callback = update.get("callback_query")
    if callback:
        return callback.get("data"), callback.get("from", {}).get("id")
    return None, None
