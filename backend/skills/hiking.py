from datetime import datetime

from backend.skills.base import BaseSkill
from backend.skills.cycling import _weather_for_window
from backend.skills.types import TimeWindow


class HikingSkill(BaseSkill):
    name = "hiking"
    required_data_sources = ["weather", "calendar"]

    async def fetch_context(self, user_id: str, window_hours: int = 48) -> dict:
        return {}

    async def score_window(
        self, window: TimeWindow, context: dict, user_config: dict
    ) -> float:
        entry = _weather_for_window(context, window)
        if entry is None:
            return 0.0

        temp_c = float(entry.get("temperature_c", 0))
        rain_prob = float(entry.get("rain_probability", 100))
        wind_kmh = float(entry.get("wind_speed_kmh", 99))

        min_temp = float(user_config.get("min_temp_c", 10))
        max_temp = float(user_config.get("max_temp_c", 28))
        max_rain = float(user_config.get("max_rain_probability", 30))
        max_wind = float(user_config.get("max_wind_kmh", 35))
        daylight_only = user_config.get("daylight_only", True)

        if temp_c < min_temp or temp_c > max_temp:
            return 0.0
        if rain_prob > max_rain or wind_kmh > max_wind:
            return 0.0

        if daylight_only and (window.start.hour < 7 or window.end.hour > 20):
            return 0.0

        temp_mid = (min_temp + max_temp) / 2
        temp_component = 1.0 - abs(temp_c - temp_mid) / (max_temp - min_temp + 0.01)
        rain_component = 1.0 - rain_prob / 100.0
        wind_component = 1.0 - min(1.0, wind_kmh / max_wind)

        score = 0.35 * temp_component + 0.4 * rain_component + 0.25 * wind_component
        if window.start.weekday() in (5, 6):
            score = min(1.0, score + 0.05)

        return round(min(1.0, max(0.0, score)), 3)

    def format_conditions(self, window: TimeWindow, context: dict) -> str:
        entry = _weather_for_window(context, window)
        if not entry:
            return "Weather unavailable"
        return (
            f"{entry.get('temperature_c', '?')}°C, "
            f"{entry.get('rain_probability', '?')}% rain, "
            f"{entry.get('wind_speed_kmh', '?')}km/h wind — good trail weather"
        )
