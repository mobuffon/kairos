"""Location resolution — natural language to coordinates and nearby spots."""

from dataclasses import dataclass
from typing import Any

import httpx

from backend.core.logging import get_logger

logger = get_logger("services.geocoding")

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"

# Curated surf/sports spots keyed by lowercase region tokens (city, admin area, country).
SPORTS_SPOTS: dict[str, list[str]] = {
    "lisbon": ["Costa da Caparica", "Carcavelos", "Guincho"],
    "portugal": ["Costa da Caparica", "Ericeira", "Nazaré", "Peniche"],
    "ericeira": ["Ribeira d'Ilhas", "São Lourenço", "Coxos"],
    "london": ["Brighton (1h)", "Bournemouth (2h)", "Cornwall (4h+)"],
    "munich": ["Chiemsee", "Tegernsee", "Ammersee"],
    "berlin": ["Wannsee", "Müggelsee", "Grunewald trails"],
    "san francisco": ["Ocean Beach", "Pacifica", "Bolinas"],
    "los angeles": ["Malibu", "Manhattan Beach", "Huntington Beach"],
    "sydney": ["Bondi Beach", "Manly", "Cronulla"],
    "biarritz": ["Grande Plage", "Côte des Basques", "Hendaye"],
}

SPORT_ALIASES: dict[str, str] = {
    "surf": "surf",
    "surfing": "surf",
    "surfer": "surf",
    "cycle": "cycling",
    "cycling": "cycling",
    "bike": "cycling",
    "biking": "cycling",
    "hike": "hiking",
    "hiking": "hiking",
    "walk": "hiking",
    "trail": "hiking",
}


@dataclass(frozen=True)
class ResolvedLocation:
    name: str
    latitude: float
    longitude: float
    country: str
    admin_area: str | None
    timezone: str
    sports_spots: list[str]


async def geocode_location(query: str, *, count: int = 5) -> list[ResolvedLocation]:
    """Resolve a place name to coordinates via Open-Meteo Geocoding (no API key)."""
    query = query.strip()
    if not query:
        return []

    params = {"name": query, "count": count, "language": "en", "format": "json"}
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(GEOCODING_URL, params=params)
            response.raise_for_status()
            data = response.json()
    except Exception as exc:
        logger.error("geocoding_failed", query=query, error=str(exc))
        raise

    results: list[ResolvedLocation] = []
    for item in data.get("results") or []:
        results.append(_to_resolved_location(item))
    return results


def _to_resolved_location(item: dict[str, Any]) -> ResolvedLocation:
    name = item.get("name", "Unknown")
    admin = item.get("admin1")
    country = item.get("country", "")
    label = f"{name}, {country}" if country else name
    return ResolvedLocation(
        name=label,
        latitude=float(item["latitude"]),
        longitude=float(item["longitude"]),
        country=country,
        admin_area=admin,
        timezone=item.get("timezone", "UTC"),
        sports_spots=_lookup_sports_spots(name, admin, country),
    )


def _lookup_sports_spots(name: str, admin: str | None, country: str) -> list[str]:
    tokens = [name.lower(), (admin or "").lower(), country.lower()]
    seen: set[str] = set()
    spots: list[str] = []
    for token in tokens:
        if not token:
            continue
        for key, values in SPORTS_SPOTS.items():
            if key in token or token in key:
                for spot in values:
                    if spot not in seen:
                        seen.add(spot)
                        spots.append(spot)
    return spots


def normalize_sport(name: str) -> str | None:
    return SPORT_ALIASES.get(name.strip().lower())


def parse_sports_list(raw: str | None) -> list[str]:
    """Parse comma/and-separated sport names into canonical hobby types."""
    if not raw:
        return []
    cleaned = raw.replace(" and ", ",").replace("&", ",")
    sports: list[str] = []
    for part in cleaned.split(","):
        token = part.strip().lower()
        for prefix in ("sports ", "sport "):
            if token.startswith(prefix):
                token = token[len(prefix) :].strip()
                break
        if not token:
            continue
        canonical = normalize_sport(token)
        if canonical and canonical not in sports:
            sports.append(canonical)
    return sports


DEFAULT_SPORT_CONFIGS: dict[str, dict[str, Any]] = {
    "surf": {
        "min_wave_height": 1.0,
        "max_wave_height": 2.5,
        "max_wind_knots": 15,
        "min_swell_period": 8,
        "prefer_morning": True,
    },
    "cycling": {
        "min_temp_c": 14,
        "max_rain_probability": 20,
        "max_wind_kmh": 30,
        "weekend_only": False,
    },
    "hiking": {
        "min_temp_c": 10,
        "max_temp_c": 26,
        "max_rain_probability": 25,
        "max_wind_kmh": 35,
        "daylight_only": True,
    },
}

WEATHER_SPORTS = frozenset(DEFAULT_SPORT_CONFIGS.keys())
