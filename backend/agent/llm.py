"""Shared LLM client — routes to Anthropic, OpenRouter, or mock."""

from typing import Literal

import httpx

from backend.core.config import Settings, get_settings

LLMProvider = Literal["anthropic", "openrouter", "mock"]

OPENROUTER_CHAT_URL = "https://openrouter.ai/api/v1/chat/completions"


async def complete(
    *,
    user: str,
    system: str | None = None,
    max_tokens: int = 200,
    settings: Settings | None = None,
) -> str | None:
    """Run a chat completion. Returns None if the provider is unavailable or fails."""
    cfg = settings or get_settings()
    provider = cfg.effective_llm_provider

    if provider == "mock":
        return None

    try:
        if provider == "anthropic":
            return await _anthropic_complete(cfg, user=user, system=system, max_tokens=max_tokens)
        if provider == "openrouter":
            return await _openrouter_complete(cfg, user=user, system=system, max_tokens=max_tokens)
    except Exception:
        return None

    return None


async def _anthropic_complete(
    settings: Settings,
    *,
    user: str,
    system: str | None,
    max_tokens: int,
) -> str:
    import anthropic

    client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
    kwargs: dict = {
        "model": settings.anthropic_model,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": user}],
    }
    if system:
        kwargs["system"] = system
    response = await client.messages.create(**kwargs)
    block = response.content[0]
    if hasattr(block, "text"):
        return block.text.strip()
    return ""


async def _openrouter_complete(
    settings: Settings,
    *,
    user: str,
    system: str | None,
    max_tokens: int,
) -> str:
    messages: list[dict[str, str]] = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": user})

    headers = {
        "Authorization": f"Bearer {settings.openrouter_api_key}",
        "HTTP-Referer": settings.frontend_url,
        "X-Title": "Kairos",
    }
    payload = {
        "model": settings.openrouter_model,
        "max_tokens": max_tokens,
        "messages": messages,
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(OPENROUTER_CHAT_URL, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()

    return data["choices"][0]["message"]["content"].strip()
