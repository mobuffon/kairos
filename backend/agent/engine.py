from dataclasses import dataclass
from datetime import UTC, datetime
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


PHYSICAL_HOBBIES = frozenset({"surf", "cycling", "hiking", "running"})
OUTDOOR_HOBBIES = PHYSICAL_HOBBIES | frozenset({"call_friend"})


def _fact_is_active(fact: dict[str, Any], now: datetime | None = None) -> bool:
    valid_until = fact.get("valid_until")
    if valid_until is None:
        return True
    if isinstance(valid_until, str):
        until = datetime.fromisoformat(valid_until)
    else:
        until = valid_until
    ref = now or datetime.now(UTC)
    if ref.tzinfo is None:
        ref = ref.replace(tzinfo=UTC)
    if until.tzinfo is None:
        until = until.replace(tzinfo=UTC)
    return until > ref


def is_suppressed_by_facts(
    hobby_type: str,
    facts: list[dict[str, Any]],
    *,
    now: datetime | None = None,
) -> bool:
    active = [f for f in facts if _fact_is_active(f, now)]
    for fact in active:
        category = fact.get("category", "")
        if category == "injury" and hobby_type in PHYSICAL_HOBBIES:
            return True
        if category == "travel" and hobby_type in OUTDOOR_HOBBIES:
            return True
        if category == "preference":
            text = fact.get("fact", "").lower()
            if "no surf" in text and hobby_type == "surf":
                return True
            if "no cycling" in text and hobby_type == "cycling":
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
    prefer_diverse_hobbies: bool = True,
) -> list[RankedSuggestion]:
    settings = get_settings()
    threshold = min_score if min_score is not None else settings.min_suggestion_score
    remaining = max(0, daily_limit - already_sent_today)
    if remaining == 0:
        return []

    filtered = [c for c in candidates if c.score >= threshold]
    filtered.sort(key=lambda c: (c.score, c.hobby_type), reverse=True)

    deduped: list[RankedSuggestion] = []
    seen_windows: set[tuple[str, str]] = set()
    seen_hobbies: set[str] = set()

    for item in filtered:
        window_key = (item.hobby_type, item.window.start.isoformat())
        if window_key in seen_windows:
            continue
        if prefer_diverse_hobbies and item.hobby_type in seen_hobbies:
            continue
        seen_windows.add(window_key)
        seen_hobbies.add(item.hobby_type)
        deduped.append(item)
        if len(deduped) >= remaining:
            break

    if len(deduped) < remaining:
        for item in filtered:
            window_key = (item.hobby_type, item.window.start.isoformat())
            if window_key in seen_windows:
                continue
            seen_windows.add(window_key)
            deduped.append(item)
            if len(deduped) >= remaining:
                break

    return deduped[:remaining]
