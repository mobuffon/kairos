"""Outbound message delivery — mock logs to file when no bot token."""

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from backend.core.config import get_settings
from backend.core.logging import get_logger

logger = get_logger("bot.notifier")
MOCK_LOG_PATH = Path(__file__).resolve().parents[2] / "data" / "mock_notifications.jsonl"


def _append_mock_log(entry: dict[str, Any]) -> None:
    MOCK_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with MOCK_LOG_PATH.open("a") as f:
        f.write(json.dumps(entry) + "\n")


async def send_message(
    chat_id: int,
    text: str,
    *,
    reply_markup: dict[str, Any] | None = None,
    user_id: str | None = None,
) -> dict[str, Any]:
    settings = get_settings()

    if settings.use_mock_telegram:
        entry = {
            "timestamp": datetime.now(UTC).isoformat(),
            "chat_id": chat_id,
            "user_id": user_id,
            "text": text,
            "reply_markup": reply_markup,
            "mock": True,
        }
        _append_mock_log(entry)
        logger.info("mock_telegram_send", chat_id=chat_id, text=text[:80])
        return {"ok": True, "mock": True, "message_id": int(datetime.now(UTC).timestamp())}

    try:
        import httpx

        url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"
        payload: dict[str, Any] = {"chat_id": chat_id, "text": text}
        if reply_markup:
            payload["reply_markup"] = reply_markup
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, timeout=10)
            response.raise_for_status()
            return response.json()
    except Exception as exc:
        logger.error("telegram_send_failed", chat_id=chat_id, error=str(exc))
        raise
