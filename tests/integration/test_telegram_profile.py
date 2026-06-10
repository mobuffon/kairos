import uuid

import pytest
from sqlalchemy import select

from backend.core.crud import get_user_by_telegram_id
from backend.models import UserContact


@pytest.fixture
def capture_send(monkeypatch):
    sent: list[dict] = []

    async def fake_send(chat_id, text, **kwargs):
        sent.append({"chat_id": chat_id, "text": text, **kwargs})
        return {"ok": True, "mock": True}

    monkeypatch.setattr("bot.telegram.webhook.send_message", fake_send)
    return sent


def _message_update(
    text: str,
    *,
    telegram_id: int,
    username: str = "testuser",
    update_id: int = 1,
) -> dict:
    return {
        "update_id": update_id,
        "message": {
            "message_id": update_id,
            "date": 0,
            "text": text,
            "chat": {"id": telegram_id, "type": "private"},
            "from": {"id": telegram_id, "username": username},
        },
    }


@pytest.mark.asyncio
async def test_webhook_start_creates_user(client, capture_send):
    telegram_id = 9_900_000 + uuid.uuid4().int % 100_000
    response = await client.post(
        "/bot/webhook",
        json=_message_update("/start", telegram_id=telegram_id),
    )
    assert response.status_code == 200
    body = response.json()
    assert body["handled"] is True
    assert body["reply_sent"] is True
    assert len(capture_send) == 1
    assert "Welcome" in capture_send[0]["text"]
    assert "Kairos" in capture_send[0]["text"]

    from backend.core.db import async_session_factory

    async with async_session_factory() as session:
        user = await get_user_by_telegram_id(session, telegram_id)
        assert user is not None
        assert user.telegram_username == "testuser"


@pytest.mark.asyncio
async def test_webhook_add_contact_command(client, capture_send):
    telegram_id = 9_910_000 + uuid.uuid4().int % 100_000
    contact_name = f"Alex_{uuid.uuid4().hex[:8]}"
    start = await client.post(
        "/bot/webhook",
        json=_message_update("/start", telegram_id=telegram_id, update_id=10),
    )
    assert start.status_code == 200

    response = await client.post(
        "/bot/webhook",
        json=_message_update(
            f"/add_contact {contact_name} | friend | 30",
            telegram_id=telegram_id,
            update_id=11,
        ),
    )
    assert response.status_code == 200
    assert response.json()["reply_sent"] is True
    assert any(f"Added contact {contact_name}" in item["text"] for item in capture_send)

    from backend.core.db import async_session_factory

    async with async_session_factory() as session:
        user = await get_user_by_telegram_id(session, telegram_id)
        assert user is not None
        result = await session.execute(
            select(UserContact).where(
                UserContact.user_id == user.id,
                UserContact.name == contact_name,
            )
        )
        contact = result.scalar_one_or_none()
        assert contact is not None
        assert contact.relationship_type == "friend"
        assert contact.contact_frequency_days == 30
