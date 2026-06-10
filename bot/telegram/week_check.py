"""Natural-language week-ahead sports weather queries via Telegram."""

import re
from dataclasses import dataclass
from typing import Any

from backend.core.config import get_settings
from backend.core.logging import get_logger
from backend.providers.mock.provider import MockProvider
from backend.services.geocoding import ResolvedLocation, parse_sports_list
from backend.services.week_forecast import evaluate_week_from_context, evaluate_week_query

logger = get_logger("bot.week_check")

WEEK_CHECK_PATTERNS: list[re.Pattern[str]] = [
    re.compile(
        r"(?:check|look at|scan|review|show)\s+(?:my\s+)?week\s+(?:for|in|around|at)\s+(.+)",
        re.IGNORECASE,
    ),
    re.compile(
        r"what\s+can\s+i\s+do\s+(?:in|at|around)\s+(.+?)(?:\s+this\s+week)?(?:\s+for\s+(.+))?$",
        re.IGNORECASE,
    ),
    re.compile(r"^/week(?:@\w+)?\s+(.+)$", re.IGNORECASE),
]

SPORTS_SUFFIX = re.compile(
    r"\s+(?:and\s+)?(?:for\s+)?(?:sports?\s+)?(.+)$",
    re.IGNORECASE,
)
THIS_WEEK_SUFFIX = re.compile(r"\s+this\s+week\s*$", re.IGNORECASE)


@dataclass
class WeekCheckRequest:
    location_query: str
    sports: list[str]


def is_week_check_message(text: str) -> bool:
    return parse_week_check_message(text) is not None


def parse_week_check_message(text: str) -> WeekCheckRequest | None:
    text = text.strip()
    if not text:
        return None

    for pattern in WEEK_CHECK_PATTERNS:
        match = pattern.search(text)
        if not match:
            continue
        location_part = match.group(1).strip().rstrip("?.!")
        sports_part = (
            match.group(2).strip()
            if match.lastindex and match.lastindex >= 2 and match.group(2)
            else None
        )

        if not sports_part:
            sports_match = SPORTS_SUFFIX.search(location_part)
            if sports_match:
                sports_part = sports_match.group(1).strip()
                location_part = location_part[: sports_match.start()].strip()

        location_part = THIS_WEEK_SUFFIX.sub("", location_part).strip(" ,.")
        sports = parse_sports_list(sports_part)

        if location_part:
            return WeekCheckRequest(location_query=location_part, sports=sports)

    return None


async def handle_week_check(
    text: str,
    user_context: dict[str, Any] | None = None,
) -> str:
    request = parse_week_check_message(text)
    if request is None:
        return (
            'Try: "Check my week for Lisbon and surf" or '
            '"/week Ericeira surfing, cycling"'
        )

    user = (user_context or {}).get("user", {})

    try:
        if get_settings().mock_external_apis:
            return await _handle_week_check_mock(request, user)
        result = await evaluate_week_query(
            request.location_query,
            request.sports or None,
            user_hobbies=user.get("hobbies"),
        )
        return result.message
    except ValueError as exc:
        return str(exc)
    except Exception as exc:
        logger.error("week_check_failed", error=str(exc), location=request.location_query)
        return "Sorry — I couldn't fetch the forecast right now. Please try again in a moment."


async def _handle_week_check_mock(request: WeekCheckRequest, user: dict[str, Any]) -> str:
    """Score against fixture weather while using the real user's hobbies and location."""
    from datetime import datetime

    provider = MockProvider()
    context = provider.build_evaluation_context("mo")
    merged_user = {**context.get("user", {}), **user}
    sports = request.sports or ["surf", "cycling"]
    location = await _resolve_location_for_mock(request.location_query, merged_user)

    ref_raw = context.get("reference_time")
    reference = datetime.fromisoformat(ref_raw) if ref_raw else None

    return await evaluate_week_from_context(
        location,
        sports,
        context,
        user_hobbies=merged_user.get("hobbies"),
        reference=reference,
    )


async def _resolve_location_for_mock(
    query: str,
    user: dict[str, Any],
) -> ResolvedLocation:
    from backend.services.geocoding import _lookup_sports_spots

    return ResolvedLocation(
        name=query.title(),
        latitude=float(user.get("location_lat", 38.72)),
        longitude=float(user.get("location_lng", -9.14)),
        country="",
        admin_area=None,
        timezone=user.get("timezone", "Europe/Lisbon"),
        sports_spots=_lookup_sports_spots(query, None, ""),
    )
