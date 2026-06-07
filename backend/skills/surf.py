from datetime import datetime

from backend.skills.base import BaseSkill
from backend.skills.types import TimeWindow


def _window_slice(context: dict, window: TimeWindow) -> dict | None:
    marine = context.get("marine", {})
    for entry in marine.get("hourly", []):
        ts = datetime.fromisoformat(entry["time"])
        if window.start <= ts < window.end:
            return entry
    return None


def _wind_score(knots: float, max_knots: float) -> float:
    if knots > max_knots:
        return 0.0
    return 1.0 - (knots / max_knots) * 0.4


class SurfSkill(BaseSkill):
    name = "surf"
    required_data_sources = ["marine", "calendar"]

    async def fetch_context(self, user_id: str, window_hours: int = 48) -> dict:
        return {}

    async def score_window(
        self, window: TimeWindow, context: dict, user_config: dict
    ) -> float:
        entry = _window_slice(context, window)
        if entry is None:
            return 0.0

        wave_height = float(entry.get("wave_height", 0))
        wind_knots = float(entry.get("wind_speed_knots", 99))
        swell_period = float(entry.get("swell_period", 0))

        min_height = float(user_config.get("min_wave_height", 1.0))
        max_height = float(user_config.get("max_wave_height", 2.5))
        max_wind = float(user_config.get("max_wind_knots", 15))
        min_period = float(user_config.get("min_swell_period", 8))
        prefer_morning = user_config.get("prefer_morning", True)

        if wave_height < min_height or wave_height > max_height:
            return 0.0
        if swell_period < min_period:
            return 0.0

        wind_component = _wind_score(wind_knots, max_wind)
        if wind_component == 0.0:
            return 0.0

        height_mid = (min_height + max_height) / 2
        height_component = 1.0 - abs(wave_height - height_mid) / (max_height - min_height + 0.01)
        period_component = min(1.0, swell_period / 12.0)

        score = 0.45 * height_component + 0.35 * wind_component + 0.2 * period_component

        if prefer_morning and window.start.hour >= 12:
            score *= 0.6

        return round(min(1.0, max(0.0, score)), 3)

    def format_conditions(self, window: TimeWindow, context: dict) -> str:
        entry = _window_slice(context, window)
        if not entry:
            return "Marine conditions unavailable"
        return (
            f"{entry.get('wave_height', '?')}m swell, "
            f"{entry.get('wind_speed_knots', '?')}kt wind, "
            f"{entry.get('swell_period', '?')}s period"
        )
