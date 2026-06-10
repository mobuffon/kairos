import pytest

from bot.telegram.week_check import (
    handle_week_check,
    is_week_check_message,
    parse_week_check_message,
)
from backend.services.geocoding import parse_sports_list


def test_is_week_check_message():
    assert is_week_check_message("Check my week for Lisbon and surf")
    assert is_week_check_message("/week Ericeira surfing")
    assert is_week_check_message("What can I do in Munich this week for hiking")
    assert not is_week_check_message("I broke my arm")


def test_parse_week_check_location_and_sport():
    req = parse_week_check_message("Check my week for Lisbon and surf")
    assert req is not None
    assert req.location_query == "Lisbon"
    assert req.sports == ["surf"]


def test_parse_week_check_multiple_sports():
    req = parse_week_check_message("/week Lisbon surfing, cycling")
    assert req is not None
    assert req.location_query == "Lisbon"
    assert req.sports == ["surf", "cycling"]


def test_parse_sports_list_aliases():
    assert parse_sports_list("surfing and biking") == ["surf", "cycling"]


@pytest.mark.asyncio
async def test_handle_week_check_mock_mode():
    reply = await handle_week_check(
        "Check my week for Lisbon and surf",
        {"user": {"default_scenario": "mo_surf_perfect", "hobbies": []}},
    )
    assert "Week ahead" in reply
    assert "surf" in reply.lower()
