"""Telegram webhook structure tests — no real bot token required."""

import pytest
from httpx import ASGITransport, AsyncClient

from backend.core.config import Settings, get_settings
from backend.main import app

_START_UPDATE = {
    "update_id": 42,
    "message": {
        "message_id": 1,
        "date": 0,
        "text": "/start",
        "chat": {"id": 123456789, "type": "private"},
        "from": {"id": 123456789, "username": "webhook_test"},
    },
}


@pytest.fixture
def live_telegram_settings(monkeypatch):
    get_settings.cache_clear()
    settings = Settings(
        _env_file=None,
        mock_external_apis=False,
        telegram_bot_token="123456789:ABCdefGHIjklMNOpqrsTUVwxyz",
        telegram_webhook_secret="test-webhook-secret-abc123",
    )
    for module in (
        "backend.core.config",
        "backend.api.auth",
        "backend.api.bot",
        "bot.telegram.webhook",
        "bot.telegram.notifier",
    ):
        monkeypatch.setattr(f"{module}.get_settings", lambda: settings)
    yield settings
    get_settings.cache_clear()


@pytest.fixture
async def live_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_webhook_start_replies_in_mock_mode(client):
    response = await client.post("/bot/webhook", json=_START_UPDATE)
    assert response.status_code == 200
    body = response.json()
    assert body["handled"] is True
    assert body["reply_sent"] is True
    assert body["mock"] is True


@pytest.mark.asyncio
async def test_webhook_rejects_missing_secret_when_live(live_client, live_telegram_settings):
    response = await live_client.post("/bot/webhook", json=_START_UPDATE)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_webhook_rejects_wrong_secret_when_live(live_client, live_telegram_settings):
    response = await live_client.post(
        "/bot/webhook",
        json=_START_UPDATE,
        headers={"X-Telegram-Bot-Api-Secret-Token": "wrong-secret"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_webhook_accepts_secret_and_handles_start(live_client, live_telegram_settings, monkeypatch):
    sent: list[dict] = []

    async def fake_send(chat_id, text, **kwargs):
        sent.append({"chat_id": chat_id, "text": text})
        return {"ok": True, "mock": False}

    monkeypatch.setattr("bot.telegram.webhook.send_message", fake_send)

    response = await live_client.post(
        "/bot/webhook",
        json=_START_UPDATE,
        headers={"X-Telegram-Bot-Api-Secret-Token": live_telegram_settings.telegram_webhook_secret},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["handled"] is True
    assert body["reply_sent"] is True
    assert len(sent) == 1
    assert "Welcome" in sent[0]["text"]
    assert "Kairos" in sent[0]["text"]
