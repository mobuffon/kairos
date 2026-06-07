from datetime import datetime, timezone

import pytest

from backend.skills.cycling import CyclingSkill
from backend.skills.surf import SurfSkill
from backend.skills.types import TimeWindow


@pytest.mark.asyncio
async def test_surf_scores_perfect_conditions():
    skill = SurfSkill()
    window = TimeWindow(
        start=datetime(2025, 6, 9, 7, 30, tzinfo=timezone.utc),
        end=datetime(2025, 6, 9, 10, 30, tzinfo=timezone.utc),
    )
    context = {
        "marine": {
            "hourly": [
                {
                    "time": "2025-06-09T07:30:00+00:00",
                    "wave_height": 1.6,
                    "wind_speed_knots": 8,
                    "swell_period": 11,
                }
            ]
        }
    }
    config = {
        "min_wave_height": 1.0,
        "max_wave_height": 2.5,
        "max_wind_knots": 15,
        "min_swell_period": 8,
        "prefer_morning": True,
    }
    score = await skill.score_window(window, context, config)
    assert score >= 0.7


@pytest.mark.asyncio
async def test_surf_rejects_flat_swell():
    skill = SurfSkill()
    window = TimeWindow(
        start=datetime(2025, 6, 9, 7, 30, tzinfo=timezone.utc),
        end=datetime(2025, 6, 9, 10, 30, tzinfo=timezone.utc),
    )
    context = {
        "marine": {
            "hourly": [
                {
                    "time": "2025-06-09T07:30:00+00:00",
                    "wave_height": 0.4,
                    "wind_speed_knots": 5,
                    "swell_period": 6,
                }
            ]
        }
    }
    score = await skill.score_window(window, context, {})
    assert score == 0.0


@pytest.mark.asyncio
async def test_cycling_scores_clear_weekend():
    skill = CyclingSkill()
    window = TimeWindow(
        start=datetime(2025, 6, 7, 9, 0, tzinfo=timezone.utc),
        end=datetime(2025, 6, 7, 12, 0, tzinfo=timezone.utc),
    )
    context = {
        "weather": {
            "hourly": [
                {
                    "time": "2025-06-07T09:00:00+00:00",
                    "temperature_c": 18,
                    "rain_probability": 5,
                    "wind_speed_kmh": 12,
                }
            ]
        }
    }
    config = {"min_temp_c": 14, "max_rain_probability": 20, "weekend_only": True}
    score = await skill.score_window(window, context, config)
    assert score >= 0.6


@pytest.mark.asyncio
async def test_cycling_rejects_rain():
    skill = CyclingSkill()
    window = TimeWindow(
        start=datetime(2025, 6, 7, 9, 0, tzinfo=timezone.utc),
        end=datetime(2025, 6, 7, 12, 0, tzinfo=timezone.utc),
    )
    context = {
        "weather": {
            "hourly": [
                {
                    "time": "2025-06-07T09:00:00+00:00",
                    "temperature_c": 16,
                    "rain_probability": 80,
                    "wind_speed_kmh": 10,
                }
            ]
        }
    }
    score = await skill.score_window(window, context, {"max_rain_probability": 20})
    assert score == 0.0
