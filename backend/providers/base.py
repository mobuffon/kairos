from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any


class DataProvider(ABC):
    @abstractmethod
    async def get_weather(self, lat: float, lng: float, hours: int = 48) -> dict[str, Any]:
        ...

    @abstractmethod
    async def get_marine(self, lat: float, lng: float, hours: int = 48) -> dict[str, Any]:
        ...

    @abstractmethod
    async def get_calendar_gaps(
        self, user_id: str, hours: int = 48, reference: datetime | None = None
    ) -> list[dict[str, Any]]:
        ...

    @abstractmethod
    async def get_contacts(self, user_id: str) -> list[dict[str, Any]]:
        ...
