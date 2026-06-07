from typing import Any

from backend.agent.engine import RankedSuggestion
from backend.agent.prompts import SUGGESTION_SYSTEM, SUGGESTION_USER
from backend.core.config import get_settings


async def generate_suggestion_message(
    suggestion: RankedSuggestion,
    user_context: dict[str, Any],
    *,
    mock: bool = False,
) -> str:
    user = user_context.get("user", {})
    user_name = user.get("telegram_username", "friend")
    location = user.get("location_label", "your area")

    if mock or not get_settings().anthropic_api_key:
        hobby = suggestion.hobby_type.replace("_", " ")
        return (
            f"Hey {user_name}! {hobby.title()} looks great "
            f"{suggestion.window.start.strftime('%A %H:%M')}–"
            f"{suggestion.window.end.strftime('%H:%M')}: "
            f"{suggestion.conditions_summary}."
        )

    try:
        import anthropic

        client = anthropic.AsyncAnthropic(api_key=get_settings().anthropic_api_key)
        prompt = SUGGESTION_USER.format(
            user_name=user_name,
            location=location,
            hobby_type=suggestion.hobby_type,
            window_start=suggestion.window.start.isoformat(),
            window_end=suggestion.window.end.isoformat(),
            conditions=suggestion.conditions_summary,
            score=suggestion.score,
        )
        response = await client.messages.create(
            model=get_settings().anthropic_model,
            max_tokens=200,
            system=SUGGESTION_SYSTEM,
            messages=[{"role": "user", "content": prompt}],
        )
        block = response.content[0]
        if hasattr(block, "text"):
            return block.text.strip()
    except Exception:
        pass

    return (
        f"Good moment for {suggestion.hobby_type}: "
        f"{suggestion.conditions_summary} "
        f"({suggestion.window.start.strftime('%a %H:%M')})."
    )
