import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from backend.core.config import Settings, get_settings
from backend.core.db import engine
from backend.main import app


@pytest_asyncio.fixture(autouse=True)
async def reset_db_engine():
    yield
    await engine.dispose()


@pytest.fixture(autouse=True)
def isolated_test_settings(monkeypatch):
    get_settings.cache_clear()
    settings = Settings(
        _env_file=None,
        mock_external_apis=True,
        anthropic_api_key="",
        openrouter_api_key="",
        google_client_id="",
        telegram_bot_token="",
    )
    for module in (
        "backend.core.config",
        "backend.api.auth",
        "backend.api.bot",
        "bot.telegram.webhook",
        "bot.telegram.notifier",
    ):
        monkeypatch.setattr(f"{module}.get_settings", lambda: settings)
    yield
    get_settings.cache_clear()


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
