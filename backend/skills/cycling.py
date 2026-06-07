from datetime import datetime

from backend.skills.base import BaseSkill
from backend.skills.types import TimeWindow


def _weather_for_window(context: dict, window: TimeWindow) -> dict | None:
    weather = context.get("weather", {})
    for entry in weather.get("hourly", []):
        ts = datetime.fromisoformat(entry["time"])
        if window.start <= ts < window.end:
            return entry
    return None


class CyclingSkill(BaseSkill):
    name = "cycling"
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

        min_temp = float(user_config.get("min_temp_c", 14))
        max_rain = float(user_config.get("max_rain_probability", 20))
        max_wind = float(user_config.get("max_wind_kmh", 30))
        weekend_only = user_config.get("weekend_only", False)

        if temp_c < min_temp or rain_prob > max_rain or wind_kmh > max_wind:
            return 0.0

        if weekend_only and window.start.weekday() < 5:
            return 0.0

        temp_component = min(1.0, (temp_c - min_temp) / 10.0 + 0.5)
        rain_component = 1.0 - rain_prob / 100.0
        wind_component = 1.0 - min(1.0, wind_kmh / max_wind)

        score = 0.4 * temp_component + 0.35 * rain_component + 0.25 * wind_component
        return round(min(1.0, max(0.0, score)), 3)

    def format_conditions(self, window: TimeWindow, context: dict) -> str:
        entry = _weather_for_window(context, window)
        if not entry:
            return "Weather unavailable"
        return (
            f"{entry.get('temperature_c', '?')}°C, "
            f"{entry.get('rain_probability', '?')}% rain, "
            f"{entry.get('wind_speed_kmh', '?')}km/h wind"
        )
