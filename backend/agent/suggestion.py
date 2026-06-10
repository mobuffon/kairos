from typing import Any

from backend.agent.engine import RankedSuggestion
from backend.agent.llm import complete
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

    settings = get_settings()
    if mock or settings.use_mock_llm:
        hobby = suggestion.hobby_type.replace("_", " ")
        return (
            f"Hey {user_name}! {hobby.title()} looks great "
            f"{suggestion.window.start.strftime('%A %H:%M')}–"
            f"{suggestion.window.end.strftime('%H:%M')}: "
            f"{suggestion.conditions_summary}."
        )

    prompt = SUGGESTION_USER.format(
        user_name=user_name,
        location=location,
        hobby_type=suggestion.hobby_type,
        window_start=suggestion.window.start.isoformat(),
        window_end=suggestion.window.end.isoformat(),
        conditions=suggestion.conditions_summary,
        score=suggestion.score,
    )
    text = await complete(
        system=SUGGESTION_SYSTEM,
        user=prompt,
        max_tokens=200,
        settings=settings,
    )
    if text:
        return text

    return (
        f"Good moment for {suggestion.hobby_type}: "
        f"{suggestion.conditions_summary} "
        f"({suggestion.window.start.strftime('%a %H:%M')})."
    )
