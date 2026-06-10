"""Open-Meteo weather and marine forecast provider (no API key required)."""

import json
from datetime import UTC, datetime
from typing import Any
from zoneinfo import ZoneInfo

import httpx

from backend.core.db import get_redis
from backend.core.logging import get_logger
from backend.providers.base import DataProvider

logger = get_logger("providers.open_meteo")

WEATHER_URL = "https://api.open-meteo.com/v1/forecast"
MARINE_URL = "https://marine-api.open-meteo.com/v1/marine"
CACHE_TTL_SECONDS = 7200  # 2h per architecture convention


def _cache_key(kind: str, lat: float, lng: float, hours: int) -> str:
    return f"{kind}:{lat:.2f}:{lng:.2f}:{hours}"


def _kmh_to_knots(kmh: float | None) -> float:
    if kmh is None:
        return 0.0
    return round(kmh / 1.852, 1)


class OpenMeteoProvider(DataProvider):
    """Fetches live forecasts from Open-Meteo with optional Redis caching."""

    async def _get_cached(self, key: str) -> dict[str, Any] | None:
        try:
            redis = await get_redis()
            raw = await redis.get(key)
            if raw:
                return json.loads(raw)
        except Exception as exc:
            logger.warning("cache_read_failed", key=key, error=str(exc))
        return None

    async def _set_cached(self, key: str, data: dict[str, Any]) -> None:
        try:
            redis = await get_redis()
            await redis.set(key, json.dumps(data), ex=CACHE_TTL_SECONDS)
        except Exception as exc:
            logger.warning("cache_write_failed", key=key, error=str(exc))

    async def get_weather(self, lat: float, lng: float, hours: int = 48) -> dict[str, Any]:
        days = min(16, max(2, (hours + 23) // 24))
        cache_key = _cache_key("weather", lat, lng, days)
        cached = await self._get_cached(cache_key)
        if cached:
            return cached

        params = {
            "latitude": lat,
            "longitude": lng,
            "hourly": "temperature_2m,precipitation_probability,wind_speed_10m",
            "forecast_days": days,
            "timezone": "auto",
        }
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                response = await client.get(WEATHER_URL, params=params)
                response.raise_for_status()
                raw = response.json()
        except Exception as exc:
            logger.error("weather_fetch_failed", lat=lat, lng=lng, error=str(exc))
            return {"hourly": []}

        result = _normalize_weather(raw)
        await self._set_cached(cache_key, result)
        return result

    async def get_marine(self, lat: float, lng: float, hours: int = 48) -> dict[str, Any]:
        days = min(16, max(2, (hours + 23) // 24))
        cache_key = _cache_key("marine", lat, lng, days)
        cached = await self._get_cached(cache_key)
        if cached:
            return cached

        params = {
            "latitude": lat,
            "longitude": lng,
            "hourly": "wave_height,swell_wave_height,swell_wave_period,wind_speed_10m",
            "forecast_days": days,
            "timezone": "auto",
        }
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                response = await client.get(MARINE_URL, params=params)
                response.raise_for_status()
                raw = response.json()
        except Exception as exc:
            logger.error("marine_fetch_failed", lat=lat, lng=lng, error=str(exc))
            return {"hourly": []}

        result = _normalize_marine(raw)
        await self._set_cached(cache_key, result)
        return result

    async def get_calendar_gaps(
        self, user_id: str, hours: int = 48, reference: datetime | None = None
    ) -> list[dict[str, Any]]:
        """Week-check flow does not use calendar; return open windows for scoring."""
        ref = reference or datetime.now(UTC)
        return [{"start": ref, "end": ref}]

    async def get_contacts(self, user_id: str) -> list[dict[str, Any]]:
        return []


def _normalize_weather(raw: dict[str, Any]) -> dict[str, Any]:
    hourly_block = raw.get("hourly") or {}
    times = hourly_block.get("time") or []
    temps = hourly_block.get("temperature_2m") or []
    rain = hourly_block.get("precipitation_probability") or []
    wind = hourly_block.get("wind_speed_10m") or []

    hourly: list[dict[str, Any]] = []
    for i, time_str in enumerate(times):
        hourly.append(
            {
                "time": _localize_time(time_str, raw.get("timezone")),
                "temperature_c": temps[i] if i < len(temps) else None,
                "rain_probability": (rain[i] if i < len(rain) else None) or 0,
                "wind_speed_kmh": wind[i] if i < len(wind) else None,
            }
        )
    return {"hourly": hourly, "timezone": raw.get("timezone")}


def _normalize_marine(raw: dict[str, Any]) -> dict[str, Any]:
    hourly_block = raw.get("hourly") or {}
    times = hourly_block.get("time") or []
    wave_heights = hourly_block.get("wave_height") or []
    swell_heights = hourly_block.get("swell_wave_height") or []
    swell_periods = hourly_block.get("swell_wave_period") or []
    wind = hourly_block.get("wind_speed_10m") or []

    hourly: list[dict[str, Any]] = []
    for i, time_str in enumerate(times):
        wave = wave_heights[i] if i < len(wave_heights) else None
        if wave is None and i < len(swell_heights):
            wave = swell_heights[i]
        wind_kmh = wind[i] if i < len(wind) else None
        hourly.append(
            {
                "time": _localize_time(time_str, raw.get("timezone")),
                "wave_height": wave or 0,
                "wind_speed_knots": _kmh_to_knots(wind_kmh),
                "swell_period": (swell_periods[i] if i < len(swell_periods) else None) or 0,
            }
        )
    return {"hourly": hourly, "timezone": raw.get("timezone")}


def _localize_time(time_str: str, timezone: str | None) -> str:
    """Attach timezone to Open-Meteo local wall-clock timestamps."""
    if not time_str:
        return time_str
    try:
        dt = datetime.fromisoformat(time_str.replace("Z", "+00:00"))
        if dt.tzinfo is not None:
            return dt.isoformat()
        if timezone:
            return dt.replace(tzinfo=ZoneInfo(timezone)).isoformat()
        return time_str
    except Exception:
        return time_str
