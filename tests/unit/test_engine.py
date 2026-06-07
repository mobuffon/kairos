from datetime import datetime, timezone

from backend.agent.engine import is_suppressed_by_facts, rank_suggestions
from backend.agent.engine import RankedSuggestion
from backend.skills.types import TimeWindow


def _suggestion(hobby: str, score: float, hour: int = 9) -> RankedSuggestion:
    return RankedSuggestion(
        hobby_type=hobby,
        window=TimeWindow(
            start=datetime(2025, 6, 8, hour, 0, tzinfo=timezone.utc),
            end=datetime(2025, 6, 8, hour + 2, 0, tzinfo=timezone.utc),
        ),
        score=score,
        conditions_summary="test",
    )


def test_rank_suggestions_respects_daily_limit():
    candidates = [_suggestion("surf", 0.9), _suggestion("cycling", 0.8)]
    ranked = rank_suggestions(candidates, daily_limit=1)
    assert len(ranked) == 1
    assert ranked[0].hobby_type == "surf"


def test_rank_suggestions_prefers_diverse_hobbies():
    candidates = [
        _suggestion("surf", 0.9, hour=9),
        _suggestion("surf", 0.85, hour=14),
        _suggestion("cycling", 0.8, hour=10),
    ]
    ranked = rank_suggestions(candidates, daily_limit=2, prefer_diverse_hobbies=True)
    hobbies = {r.hobby_type for r in ranked}
    assert "surf" in hobbies
    assert "cycling" in hobbies


def test_injury_suppresses_physical_hobbies():
    facts = [
        {
            "category": "injury",
            "fact": "broken arm",
            "valid_until": "2030-01-01T00:00:00+00:00",
        }
    ]
    assert is_suppressed_by_facts("surf", facts)
    assert is_suppressed_by_facts("hiking", facts)
    assert not is_suppressed_by_facts("call_friend", facts)


def test_expired_injury_does_not_suppress():
    facts = [
        {
            "category": "injury",
            "fact": "old sprain",
            "valid_until": "2020-01-01T00:00:00+00:00",
        }
    ]
    assert not is_suppressed_by_facts("surf", facts)
