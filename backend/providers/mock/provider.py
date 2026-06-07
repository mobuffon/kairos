from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

from backend.providers.base import DataProvider

FIXTURES_DIR = Path(__file__).parent / "fixtures"


class MockProvider(DataProvider):
    """Loads fixture data for dev, tests, and CLI mock mode."""

    def __init__(self, scenario: str | None = None) -> None:
        self.scenario_name = scenario
        self._users = self._load_yaml("users.yaml")
        self._scenarios = self._load_yaml("scenarios.yaml")
        self._active_scenario: dict[str, Any] | None = None
        if scenario:
            self.load_scenario(scenario)

    @staticmethod
    def _load_yaml(name: str) -> dict[str, Any]:
        path = FIXTURES_DIR / name
        with path.open() as f:
            return yaml.safe_load(f) or {}

    def load_scenario(self, name: str) -> None:
        if name not in self._scenarios:
            raise KeyError(f"Unknown scenario: {name}")
        self.scenario_name = name
        self._active_scenario = self._scenarios[name]

    def get_user_fixture(self, user_key: str) -> dict[str, Any]:
        if user_key not in self._users:
            raise KeyError(f"Unknown user fixture: {user_key}")
        return self._users[user_key]

    def list_users(self) -> list[str]:
        return list(self._users.keys())

    def list_scenarios(self) -> list[str]:
        return list(self._scenarios.keys())

    def _scenario_data(self) -> dict[str, Any]:
        return self._active_scenario or {}

    async def get_weather(self, lat: float, lng: float, hours: int = 48) -> dict[str, Any]:
        return self._scenario_data().get("weather", {"hourly": []})

    async def get_marine(self, lat: float, lng: float, hours: int = 48) -> dict[str, Any]:
        return self._scenario_data().get("marine", {"hourly": []})

    async def get_calendar_gaps(
        self, user_id: str, hours: int = 48, reference: datetime | None = None
    ) -> list[dict[str, Any]]:
        gaps = self._scenario_data().get("calendar_gaps", [])
        return [
            {
                "start": datetime.fromisoformat(g["start"]),
                "end": datetime.fromisoformat(g["end"]),
            }
            for g in gaps
        ]

    async def get_contacts(self, user_id: str) -> list[dict[str, Any]]:
        scenario_contacts = self._scenario_data().get("contacts")
        if scenario_contacts is not None:
            return scenario_contacts
        user_key = self._user_key_for_id(user_id)
        if user_key:
            return self._users[user_key].get("contacts", [])
        return []

    def _user_key_for_id(self, user_id: str) -> str | None:
        for key, data in self._users.items():
            if data.get("id") == user_id:
                return key
        return None

    def reference_time(self) -> datetime | None:
        ref = self._scenario_data().get("reference_time")
        if ref:
            return datetime.fromisoformat(ref)
        return None

    def is_calendar_busy(self) -> bool:
        return bool(self._scenario_data().get("calendar_busy", False))

    def build_evaluation_context(self, user_key: str) -> dict[str, Any]:
        user = dict(self.get_user_fixture(user_key))
        scenario_facts = self._scenario_data().get("profile_facts")
        if scenario_facts is not None:
            user["profile_facts"] = scenario_facts
        ref = self.reference_time()
        return {
            "user": user,
            "reference_time": ref.isoformat() if ref else None,
            "weather": self._scenario_data().get("weather", {"hourly": []}),
            "marine": self._scenario_data().get("marine", {"hourly": []}),
            "calendar_gaps": self._scenario_data().get("calendar_gaps", []),
            "calendar_busy": self.is_calendar_busy(),
            "contacts": self._scenario_data().get("contacts", user.get("contacts", [])),
        }
