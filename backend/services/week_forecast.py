"""Week-ahead sports conditions evaluation using live weather data."""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any
from zoneinfo import ZoneInfo

from backend.agent.engine import RankedSuggestion, score_hobby_windows
from backend.core.logging import get_logger
from backend.providers import get_data_provider
from backend.services.geocoding import (
    DEFAULT_SPORT_CONFIGS,
    WEATHER_SPORTS,
    ResolvedLocation,
    geocode_location,
)
from backend.skills.types import TimeWindow

logger = get_logger("services.week_forecast")

# Daily scoring windows (local time).
DAY_WINDOWS = (
    (7, 11, "morning"),
    (14, 18, "afternoon"),
)

MIN_DISPLAY_SCORE = 0.45


@dataclass
class DaySportWindow:
    date_label: str
    period: str
    hobby_type: str
    score: float
    conditions: str
    window_start: datetime
    window_end: datetime


@dataclass
class WeekForecastResult:
    location: ResolvedLocation
    sports: list[str]
    windows: list[DaySportWindow]
    weather_available: bool
    marine_available: bool
    message: str


def build_day_windows(
    *,
    days: int,
    timezone: str,
    reference: datetime | None = None,
) -> list[TimeWindow]:
    tz = ZoneInfo(timezone)
    ref = reference.astimezone(tz) if reference else datetime.now(tz)
    start_day = ref.date()
    windows: list[TimeWindow] = []

    for offset in range(days):
        day = start_day + timedelta(days=offset)
        for start_hour, end_hour, _ in DAY_WINDOWS:
            start = datetime(day.year, day.month, day.day, start_hour, 0, tzinfo=tz)
            end = datetime(day.year, day.month, day.day, end_hour, 0, tzinfo=tz)
            if end <= ref:
                continue
            windows.append(TimeWindow(start=start, end=end))
    return windows


def merge_hobby_configs(
    sports: list[str],
    user_hobbies: list[dict[str, Any]] | None,
) -> dict[str, dict[str, Any]]:
    configs: dict[str, dict[str, Any]] = {
        sport: dict(DEFAULT_SPORT_CONFIGS[sport]) for sport in sports if sport in DEFAULT_SPORT_CONFIGS
    }
    if not user_hobbies:
        return configs
    for hobby in user_hobbies:
        hobby_type = hobby.get("hobby_type")
        if hobby_type in configs and hobby.get("config"):
            configs[hobby_type].update(hobby["config"])
    return configs


async def evaluate_week_for_location(
    location: ResolvedLocation,
    sports: list[str],
    *,
    days: int = 7,
    hobby_configs: dict[str, dict[str, Any]] | None = None,
    reference: datetime | None = None,
) -> WeekForecastResult:
    valid_sports = [s for s in sports if s in WEATHER_SPORTS]
    if not valid_sports:
        valid_sports = list(WEATHER_SPORTS)

    configs = hobby_configs or {s: DEFAULT_SPORT_CONFIGS[s] for s in valid_sports}
    hours = days * 24
    provider = get_data_provider()

    weather = await provider.get_weather(location.latitude, location.longitude, hours=hours)
    marine = await provider.get_marine(location.latitude, location.longitude, hours=hours)

    weather_available = bool(weather.get("hourly"))
    marine_available = bool(marine.get("hourly"))

    context: dict[str, Any] = {
        "weather": weather,
        "marine": marine,
        "contacts": [],
        "calendar_busy": False,
        "reference_time": reference.isoformat() if reference else None,
    }

    gaps = build_day_windows(days=days, timezone=location.timezone, reference=reference)
    all_ranked: list[RankedSuggestion] = []

    for sport in valid_sports:
        config = configs.get(sport, DEFAULT_SPORT_CONFIGS.get(sport, {}))
        ranked = await score_hobby_windows(sport, config, context, gaps)
        all_ranked.extend(ranked)

    all_ranked.sort(key=lambda r: (r.window.start, -r.score))

    day_windows: list[DaySportWindow] = []
    for item in all_ranked:
        if item.score < MIN_DISPLAY_SCORE:
            continue
        period = period_label(item.window)
        day_windows.append(
            DaySportWindow(
                date_label=item.window.start.strftime("%a %d %b"),
                period=period,
                hobby_type=item.hobby_type,
                score=item.score,
                conditions=item.conditions_summary,
                window_start=item.window.start,
                window_end=item.window.end,
            )
        )

    message = format_week_message(location, valid_sports, day_windows, weather_available, marine_available)
    return WeekForecastResult(
        location=location,
        sports=valid_sports,
        windows=day_windows,
        weather_available=weather_available,
        marine_available=marine_available,
        message=message,
    )


async def evaluate_week_query(
    location_query: str,
    sports: list[str] | None = None,
    *,
    user_hobbies: list[dict[str, Any]] | None = None,
    days: int = 7,
) -> WeekForecastResult:
    locations = await geocode_location(location_query)
    if not locations:
        raise ValueError(f"I couldn't find a place matching '{location_query}'.")

    location = locations[0]
    chosen_sports = sports or list(WEATHER_SPORTS)
    configs = merge_hobby_configs(chosen_sports, user_hobbies)
    return await evaluate_week_for_location(
        location,
        chosen_sports,
        days=days,
        hobby_configs=configs,
    )


def period_label(window: TimeWindow) -> str:
    hour = window.start.hour
    if hour < 12:
        return "morning"
    return "afternoon"


def format_week_message(
    location: ResolvedLocation,
    sports: list[str],
    windows: list[DaySportWindow],
    weather_available: bool,
    marine_available: bool,
) -> str:
    sport_labels = ", ".join(s.replace("_", " ") for s in sports)
    lines = [f"Week ahead for {location.name} ({sport_labels}):"]

    if location.sports_spots:
        lines.append(f"Nearby spots: {', '.join(location.sports_spots[:4])}")

    if not weather_available:
        lines.append("Weather data unavailable — try again shortly.")
        return "\n".join(lines)

    if "surf" in sports and not marine_available:
        lines.append("Note: marine/swell data unavailable inland — surf scores may be limited.")

    if not windows:
        lines.append("No strong windows this week for your thresholds. Conditions look marginal.")
        return "\n".join(lines)

    by_day: dict[str, list[DaySportWindow]] = {}
    for w in windows:
        by_day.setdefault(w.date_label, []).append(w)

    for day_label, day_items in by_day.items():
        day_items.sort(key=lambda w: -w.score)
        best = day_items[0]
        extras = [w for w in day_items[1:3] if w.hobby_type != best.hobby_type]
        slot = (
            f"{best.period} {best.window_start.strftime('%H:%M')}–"
            f"{best.window_end.strftime('%H:%M')}"
        )
        lines.append(
            f"• {day_label}: {best.hobby_type} ({slot}, score {best.score:.0%}) — {best.conditions}"
        )
        for extra in extras:
            slot = (
                f"{extra.period} {extra.window_start.strftime('%H:%M')}–"
                f"{extra.window_end.strftime('%H:%M')}"
            )
            lines.append(
                f"    also {extra.hobby_type} ({slot}, {extra.score:.0%}) — {extra.conditions}"
            )

    return "\n".join(lines)


async def evaluate_week_from_context(
    location: ResolvedLocation,
    sports: list[str],
    context: dict[str, Any],
    *,
    user_hobbies: list[dict[str, Any]] | None = None,
    days: int = 7,
    reference: datetime | None = None,
) -> str:
    """Score pre-loaded weather/marine context (fixtures or live) into a reply."""
    configs = merge_hobby_configs(sports, user_hobbies)
    gaps = build_day_windows(days=days, timezone=location.timezone, reference=reference)
    all_ranked: list[RankedSuggestion] = []
    for sport in sports:
        ranked = await score_hobby_windows(sport, configs.get(sport, {}), context, gaps)
        all_ranked.extend(ranked)

    day_windows: list[DaySportWindow] = []
    for item in sorted(all_ranked, key=lambda r: (r.window.start, -r.score)):
        if item.score < MIN_DISPLAY_SCORE:
            continue
        day_windows.append(
            DaySportWindow(
                date_label=item.window.start.strftime("%a %d %b"),
                period=period_label(item.window),
                hobby_type=item.hobby_type,
                score=item.score,
                conditions=item.conditions_summary,
                window_start=item.window.start,
                window_end=item.window.end,
            )
        )

    return format_week_message(
        location,
        sports,
        day_windows,
        bool(context.get("weather", {}).get("hourly")),
        bool(context.get("marine", {}).get("hourly")),
    )
