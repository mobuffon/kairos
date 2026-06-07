"""Agent layer: suggestion generation and evaluation."""

from backend.agent.engine import RankedSuggestion, rank_suggestions, score_hobby_windows
from backend.agent.suggestion import generate_suggestion_message

__all__ = [
    "RankedSuggestion",
    "rank_suggestions",
    "score_hobby_windows",
    "generate_suggestion_message",
]
