from datetime import datetime
from typing import Any

from backend.agent.engine import is_suppressed_by_facts, rank_suggestions, score_hobby_windows
from backend.agent.suggestion import generate_suggestion_message
from backend.providers.mock.provider import MockProvider


async def evaluate_user(
    user_key: str,
    *,
    mock: bool = True,
    scenario: str | None = None,
) -> dict[str, Any]:
    provider = MockProvider(scenario=scenario)
    context = provider.build_evaluation_context(user_key)
    user = context["user"]
    facts = user.get("profile_facts", [])

    all_candidates = []
    for hobby in user.get("hobbies", []):
        if not hobby.get("enabled", True):
            continue
        hobby_type = hobby["hobby_type"]
        if is_suppressed_by_facts(hobby_type, facts):
            continue
        scored = await score_hobby_windows(
            hobby_type,
            hobby.get("config", {}),
            context,
            context.get("calendar_gaps", []),
        )
        all_candidates.extend(scored)

    ranked = rank_suggestions(all_candidates)
    messages = []
    for suggestion in ranked:
        text = await generate_suggestion_message(suggestion, context, mock=mock)
        messages.append(
            {
                "hobby_type": suggestion.hobby_type,
                "score": suggestion.score,
                "window_start": suggestion.window.start.isoformat(),
                "window_end": suggestion.window.end.isoformat(),
                "conditions": suggestion.conditions_summary,
                "message": text,
            }
        )

    return {
        "user": user_key,
        "scenario": provider.scenario_name,
        "reference_time": context.get("reference_time"),
        "candidates_count": len(all_candidates),
        "suggestions": messages,
    }


async def load_user_context_mock(user_key: str) -> dict[str, Any]:
    provider = MockProvider()
    return provider.build_evaluation_context(user_key)
