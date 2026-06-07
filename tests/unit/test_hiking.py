from datetime import datetime, timezone

import pytest

from backend.skills.hiking import HikingSkill
from backend.skills.types import TimeWindow


@pytest.mark.asyncio
async def test_hiking_scores_sunny_trail_day():
    skill = HikingSkill()
    window = TimeWindow(
        start=datetime(2025, 6, 8, 10, 0, tzinfo=timezone.utc),
        end=datetime(2025, 6, 8, 14, 0, tzinfo=timezone.utc),
    )
    context = {
        "weather": {
            "hourly": [
                {
                    "time": "2025-06-08T10:00:00+00:00",
                    "temperature_c": 18,
                    "rain_probability": 10,
                    "wind_speed_kmh": 15,
                }
            ]
        }
    }
    config = {
        "min_temp_c": 10,
        "max_temp_c": 26,
        "max_rain_probability": 25,
        "daylight_only": True,
    }
    score = await skill.score_window(window, context, config)
    assert score >= 0.6


@pytest.mark.asyncio
async def test_hiking_rejects_heavy_rain():
    skill = HikingSkill()
    window = TimeWindow(
        start=datetime(2025, 6, 8, 10, 0, tzinfo=timezone.utc),
        end=datetime(2025, 6, 8, 14, 0, tzinfo=timezone.utc),
    )
    context = {
        "weather": {
            "hourly": [
                {
                    "time": "2025-06-08T10:00:00+00:00",
                    "temperature_c": 18,
                    "rain_probability": 70,
                    "wind_speed_kmh": 10,
                }
            ]
        }
    }
    score = await skill.score_window(window, context, {"max_rain_probability": 25})
    assert score == 0.0
