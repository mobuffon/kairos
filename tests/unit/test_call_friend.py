from datetime import UTC, datetime

import pytest

from backend.skills.call_friend import CallFriendSkill
from backend.skills.types import TimeWindow


@pytest.mark.asyncio
async def test_call_friend_scores_overdue_contact():
    skill = CallFriendSkill()
    window = TimeWindow(
        start=datetime(2025, 6, 8, 15, 0, tzinfo=UTC),
        end=datetime(2025, 6, 8, 17, 0, tzinfo=UTC),
    )
    context = {
        "contacts": [
            {
                "name": "Maria",
                "contact_frequency_days": 30,
                "last_contacted_at": "2025-05-01T10:00:00+00:00",
            }
        ],
        "calendar_busy": False,
        "reference_time": "2025-06-08T14:00:00+00:00",
    }
    score = await skill.score_window(window, context, {"min_window_hours": 1.0})
    assert score >= 0.5


@pytest.mark.asyncio
async def test_call_friend_suppressed_when_busy():
    skill = CallFriendSkill()
    window = TimeWindow(
        start=datetime(2025, 6, 8, 15, 0, tzinfo=UTC),
        end=datetime(2025, 6, 8, 17, 0, tzinfo=UTC),
    )
    context = {
        "contacts": [{"name": "Maria", "contact_frequency_days": 30}],
        "calendar_busy": True,
        "reference_time": "2025-06-08T14:00:00+00:00",
    }
    score = await skill.score_window(window, context, {})
    assert score == 0.0
