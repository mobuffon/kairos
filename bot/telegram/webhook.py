"""Telegram webhook handler (stub for Phase 2)."""

WEBHOOK_PATH = "/bot/webhook"


async def handle_webhook_update(update: dict) -> dict:
    return {"ok": True, "update_id": update.get("update_id")}
