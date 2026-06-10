import pytest
from unittest.mock import AsyncMock, patch

from backend.agent.llm import complete
from backend.core.config import Settings, get_settings


@pytest.fixture(autouse=True)
def clear_settings_cache():
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def test_effective_provider_mock_when_no_keys():
    settings = Settings(mock_external_apis=False, llm_provider="")
    assert settings.effective_llm_provider == "mock"
    assert settings.use_mock_llm is True


def test_effective_provider_anthropic_auto():
    settings = Settings(
        mock_external_apis=False,
        anthropic_api_key="sk-ant-real-key-12345",
    )
    assert settings.effective_llm_provider == "anthropic"
    assert settings.use_mock_llm is False


def test_effective_provider_openrouter_explicit():
    settings = Settings(
        mock_external_apis=False,
        llm_provider="openrouter",
        openrouter_api_key="sk-or-real-key-12345",
    )
    assert settings.effective_llm_provider == "openrouter"


def test_effective_provider_openrouter_without_key_falls_back_to_mock():
    settings = Settings(mock_external_apis=False, llm_provider="openrouter")
    assert settings.effective_llm_provider == "mock"


def test_placeholder_keys_treated_as_unset():
    settings = Settings(
        mock_external_apis=False,
        llm_provider="openrouter",
        openrouter_api_key="sk-or-...",
    )
    assert settings.effective_llm_provider == "mock"


@pytest.mark.asyncio
async def test_openrouter_complete_sends_expected_request():
    settings = Settings(
        mock_external_apis=False,
        llm_provider="openrouter",
        openrouter_api_key="sk-or-test-key",
        openrouter_model="anthropic/claude-sonnet-4",
        frontend_url="http://localhost:3000",
    )

    mock_response = AsyncMock()
    mock_response.raise_for_status = lambda: None
    mock_response.json = lambda: {
        "choices": [{"message": {"content": "  Hello from OpenRouter  "}}]
    }

    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_response)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch("backend.agent.llm.httpx.AsyncClient", return_value=mock_client):
        text = await complete(
            system="You are helpful.",
            user="Say hi",
            max_tokens=50,
            settings=settings,
        )

    assert text == "Hello from OpenRouter"
    mock_client.post.assert_awaited_once()
    call_kwargs = mock_client.post.call_args
    assert call_kwargs.args[0] == "https://openrouter.ai/api/v1/chat/completions"
    headers = call_kwargs.kwargs["headers"]
    assert headers["Authorization"] == "Bearer sk-or-test-key"
    assert headers["X-Title"] == "Kairos"
    payload = call_kwargs.kwargs["json"]
    assert payload["model"] == "anthropic/claude-sonnet-4"
    assert payload["messages"][0] == {"role": "system", "content": "You are helpful."}
    assert payload["messages"][1] == {"role": "user", "content": "Say hi"}
