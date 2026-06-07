from abc import ABC, abstractmethod

from backend.skills.types import TimeWindow


class BaseSkill(ABC):
    name: str
    required_data_sources: list[str]

    @abstractmethod
    async def fetch_context(self, user_id: str, window_hours: int = 48) -> dict:
        """Fetch all external data needed to evaluate this skill."""

    @abstractmethod
    async def score_window(
        self, window: TimeWindow, context: dict, user_config: dict
    ) -> float:
        """Return 0.0–1.0 score for this time window. 0 means do not suggest."""

    @abstractmethod
    def format_conditions(self, window: TimeWindow, context: dict) -> str:
        """Return a human-readable conditions summary for the Claude prompt."""
