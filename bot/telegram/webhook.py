"""Telegram webhook handler — DB-backed profile CRUD and learning pipeline."""

from datetime import datetime
from typing import Any

from backend.agent.learning import ExtractedFact, process_inbound_message
from backend.core.config import get_settings
from backend.core.db import async_session_factory
from backend.core.logging import get_logger
from backend.services.profile import (
    apply_extracted_facts,
    build_user_context,
    get_or_create_user_by_telegram_id,
    handle_profile_command,
    record_conversation,
)
from bot.telegram.notifier import send_message
from bot.telegram.week_check import handle_week_check, is_week_check_message

WEBHOOK_PATH = "/bot/webhook"
logger = get_logger("bot.webhook")


def _extract_message_fields(
    update: dict[str, Any],
) -> tuple[str | None, int | None, int | None, str | None]:
    message = update.get("message") or update.get("edited_message")
    if not message:
        callback = update.get("callback_query")
        if callback:
            from_user = callback.get("from", {})
            chat = callback.get("message", {}).get("chat", {})
            return (
                callback.get("data"),
                chat.get("id"),
                from_user.get("id"),
                from_user.get("username"),
            )
        return None, None, None, None

    from_user = message.get("from", {})
    chat_id = message.get("chat", {}).get("id")
    telegram_id = from_user.get("id") or chat_id
    return message.get("text"), chat_id, telegram_id, from_user.get("username")


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


def _welcome_message(*, created: bool) -> str:
    intro = "Welcome to Kairos!" if created else "Welcome back to Kairos!"
    return (
        f"{intro} I watch the weather, your calendar, and your hobbies "
        "to suggest the right moment for things you love.\n\n"
        "Tell me about your location and hobbies, or use /help for commands.\n\n"
        'Try: "Check my week for Lisbon and surf"'
    )


def _extracted_from_result(extracted: list[dict[str, Any]]) -> list[ExtractedFact]:
    facts: list[ExtractedFact] = []
    for item in extracted:
        valid_until = None
        if item.get("valid_until"):
            valid_until = datetime.fromisoformat(item["valid_until"])
        facts.append(
            ExtractedFact(
                category=item["category"],
                fact=item["fact"],
                valid_until=valid_until,
                action=item.get("action", "add"),
            )
        )
    return facts


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


async def _dispatch_message(session, user, text: str, context: dict[str, Any]) -> str:
    normalized = text.strip().split("@")[0].lower()
    if normalized.startswith("/start"):
        return _welcome_message(created=False)

    profile_reply = await handle_profile_command(session, user, text)
    if profile_reply is not None:
        return profile_reply

    if is_week_check_message(text):
        return await handle_week_check(text, context)

    result = await process_inbound_message(text, context)
    extracted = _extracted_from_result(result["extracted"])
    await record_conversation(
        session,
        user.id,
        direction="inbound",
        message_text=text,
        extracted_facts=result["extracted"] or None,
    )
    if extracted:
        await apply_extracted_facts(session, user.id, extracted)
    reply = result["reply"]
    await record_conversation(session, user.id, direction="outbound", message_text=reply)
    logger.info("facts_extracted", count=len(result["extracted"]))
    return reply


async def handle_webhook_update(update: dict[str, Any]) -> dict[str, Any]:
    settings = get_settings()
    text, chat_id, telegram_id, telegram_username = _extract_message_fields(update)
    update_id = update.get("update_id")

    if chat_id is None:
        return {"ok": True, "update_id": update_id, "handled": False}

    callback_data = update.get("callback_query", {}).get("data")
    if callback_data:
        result = await _handle_callback(callback_data, chat_id)
        logger.info("callback_handled", action=result, chat_id=chat_id)
        return {"ok": True, "update_id": update_id, "action": result}

    if not text or telegram_id is None:
        return {"ok": True, "update_id": update_id, "handled": False}

    async with async_session_factory() as session:
        user, created = await get_or_create_user_by_telegram_id(
            session,
            telegram_id,
            telegram_username=telegram_username,
        )
        context = await build_user_context(session, user)

        if text.strip().split("@")[0].lower().startswith("/start"):
            reply = _welcome_message(created=created)
        else:
            reply = await _dispatch_message(session, user, text, context)

        await session.commit()
        user_id = str(user.id)

    try:
        await send_message(chat_id, reply, user_id=user_id)
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
