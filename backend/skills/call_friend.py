from datetime import UTC, datetime

from backend.skills.base import BaseSkill
from backend.skills.types import TimeWindow


class CallFriendSkill(BaseSkill):
    name = "call_friend"
    required_data_sources = ["calendar", "contacts"]

    async def fetch_context(self, user_id: str, window_hours: int = 48) -> dict:
        return {}

    async def score_window(
        self, window: TimeWindow, context: dict, user_config: dict
    ) -> float:
        contacts = context.get("contacts", [])
        if not contacts:
            return 0.0

        calendar_busy = context.get("calendar_busy", False)
        if calendar_busy:
            return 0.0

        min_duration = float(user_config.get("min_window_hours", 1.0))
        if window.duration_hours < min_duration:
            return 0.0

        now = context.get("reference_time", datetime.now(UTC))
        if isinstance(now, str):
            now = datetime.fromisoformat(now)

        overdue_scores: list[float] = []
        for contact in contacts:
            last = contact.get("last_contacted_at")
            freq_days = int(contact.get("contact_frequency_days", 30))
            if last is None:
                overdue_scores.append(1.0)
                continue
            if isinstance(last, str):
                last = datetime.fromisoformat(last)
            days_since = (now - last).days
            if days_since >= freq_days:
                ratio = min(1.0, days_since / (freq_days * 1.5))
                overdue_scores.append(ratio)

        if not overdue_scores:
            return 0.0

        base = max(overdue_scores)
        if window.start.weekday() in (5, 6):
            base = min(1.0, base + 0.1)
        return round(base, 3)

    def format_conditions(self, window: TimeWindow, context: dict) -> str:
        contacts = context.get("contacts", [])
        names = [c.get("name", "?") for c in contacts[:3]]
        return f"Free {window.duration_hours:.1f}h window; overdue contacts: {', '.join(names)}"
