"""Telegram webhook handler — structured for production, mock-safe for dev."""

from typing import Any

from backend.agent.learning import process_inbound_message
from backend.core.config import get_settings
from backend.core.logging import get_logger
from backend.providers.mock.provider import MockProvider
from bot.telegram.notifier import send_message

WEBHOOK_PATH = "/bot/webhook"
logger = get_logger("bot.webhook")


def _extract_text(update: dict[str, Any]) -> tuple[str | None, int | None]:
    message = update.get("message") or update.get("edited_message")
    if not message:
        callback = update.get("callback_query")
        if callback:
            return callback.get("data"), callback.get("from", {}).get("id")
        return None, None
    return message.get("text"), message.get("chat", {}).get("id")


def _suggestion_keyboard(suggestion_id: str) -> dict[str, Any]:
    return {
        "inline_keyboard": [
            [
                {"text": "✓ Do it", "callback_data": f"confirm:{suggestion_id}"},
                {"text": "✗ Not now", "callback_data": f"dismiss:{suggestion_id}"},
                {"text": "⏰ Snooze", "callback_data": f"snooze:{suggestion_id}"},
            ]
        ]
    }


async def _handle_start(chat_id: int) -> str:
    return (
        "Welcome to Kairos! I watch the weather, your calendar, and your hobbies "
        "to suggest the right moment for things you love.\n\n"
        "Tell me about your location and hobbies, or use the web app to set up."
    )


async def _handle_what_do_you_know(user_key: str = "mo") -> str:
    provider = MockProvider()
    user = provider.get_user_fixture(user_key)
    facts = user.get("profile_facts", [])
    if not facts:
        return "I don't have any stored facts about you yet."
    lines = [f"• [{f['category']}] {f['fact']}" for f in facts]
    return "Here's what I know:\n" + "\n".join(lines)


async def _handle_callback(data: str, chat_id: int) -> str:
    action, _, ref = data.partition(":")
    if action == "confirm":
        await send_message(chat_id, "Great — I'll add that to your calendar (mock).")
        return "confirmed"
    if action == "dismiss":
        await send_message(chat_id, "No problem — dismissed.")
        return "dismissed"
    if action == "snooze":
        await send_message(chat_id, "I'll remind you again in 4 hours.")
        return "snoozed"
    return "unknown"


async def handle_webhook_update(update: dict[str, Any]) -> dict[str, Any]:
    settings = get_settings()
    text, chat_id = _extract_text(update)
    update_id = update.get("update_id")

    if chat_id is None:
        return {"ok": True, "update_id": update_id, "handled": False}

    callback_data = update.get("callback_query", {}).get("data")
    if callback_data:
        result = await _handle_callback(callback_data, chat_id)
        logger.info("callback_handled", action=result, chat_id=chat_id)
        return {"ok": True, "update_id": update_id, "action": result}

    if not text:
        return {"ok": True, "update_id": update_id, "handled": False}

    reply: str
    if text.startswith("/start"):
        reply = await _handle_start(chat_id)
    elif text.startswith("/what"):
        reply = await _handle_what_do_you_know()
    else:
        provider = MockProvider()
        context = provider.build_evaluation_context("mo")
        result = await process_inbound_message(text, context)
        reply = result["reply"]
        logger.info("facts_extracted", count=len(result["extracted"]))

    try:
        await send_message(chat_id, reply, user_id="mock")
    except Exception as exc:
        logger.error("reply_send_failed", chat_id=chat_id, error=str(exc))
        return {
            "ok": True,
            "update_id": update_id,
            "handled": True,
            "reply_sent": False,
            "mock": settings.use_mock_telegram,
        }
    return {
        "ok": True,
        "update_id": update_id,
        "handled": True,
        "reply_sent": True,
        "mock": settings.use_mock_telegram,
    }
