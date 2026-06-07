from dataclasses import dataclass
from datetime import datetime
from typing import Any

from backend.core.config import get_settings
from backend.skills import get_skill
from backend.skills.types import TimeWindow


@dataclass
class RankedSuggestion:
    hobby_type: str
    window: TimeWindow
    score: float
    conditions_summary: str


def _parse_gaps(gaps: list[Any]) -> list[TimeWindow]:
    windows: list[TimeWindow] = []
    for gap in gaps:
        if isinstance(gap, TimeWindow):
            windows.append(gap)
        elif isinstance(gap, dict):
            start = gap["start"]
            end = gap["end"]
            if isinstance(start, str):
                start = datetime.fromisoformat(start)
            if isinstance(end, str):
                end = datetime.fromisoformat(end)
            windows.append(TimeWindow(start=start, end=end))
    return windows


def is_suppressed_by_facts(hobby_type: str, facts: list[dict[str, Any]]) -> bool:
    physical = {"surf", "cycling", "hiking", "running"}
    for fact in facts:
        if fact.get("category") == "injury" and hobby_type in physical:
            return True
        if fact.get("category") == "travel" and hobby_type in physical:
            return True
    return False


async def score_hobby_windows(
    hobby_type: str,
    user_config: dict[str, Any],
    context: dict[str, Any],
    gaps: list[Any],
) -> list[RankedSuggestion]:
    skill = get_skill(hobby_type)
    windows = _parse_gaps(gaps)
    results: list[RankedSuggestion] = []

    skill_context = {
        "weather": context.get("weather", {}),
        "marine": context.get("marine", {}),
        "contacts": context.get("contacts", []),
        "calendar_busy": context.get("calendar_busy", False),
        "reference_time": context.get("reference_time"),
    }

    for window in windows:
        score = await skill.score_window(window, skill_context, user_config)
        if score <= 0:
            continue
        results.append(
            RankedSuggestion(
                hobby_type=hobby_type,
                window=window,
                score=score,
                conditions_summary=skill.format_conditions(window, skill_context),
            )
        )
    return results


def rank_suggestions(
    candidates: list[RankedSuggestion],
    *,
    daily_limit: int = 2,
    already_sent_today: int = 0,
    min_score: float | None = None,
) -> list[RankedSuggestion]:
    settings = get_settings()
    threshold = min_score if min_score is not None else settings.min_suggestion_score
    remaining = max(0, daily_limit - already_sent_today)

    filtered = [c for c in candidates if c.score >= threshold]
    filtered.sort(key=lambda c: c.score, reverse=True)

    deduped: list[RankedSuggestion] = []
    seen: set[tuple[str, str]] = set()
    for item in filtered:
        key = (item.hobby_type, item.window.start.isoformat())
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)

    return deduped[:remaining]
