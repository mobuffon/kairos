"""External data providers (weather, calendar, etc.)."""

from backend.core.config import get_settings
from backend.providers.base import DataProvider
from backend.providers.mock.provider import MockProvider
from backend.providers.open_meteo import OpenMeteoProvider


def get_data_provider(*, scenario: str | None = None) -> DataProvider:
    if get_settings().mock_external_apis:
        return MockProvider(scenario=scenario)
    return OpenMeteoProvider()


__all__ = ["DataProvider", "MockProvider", "OpenMeteoProvider", "get_data_provider"]
