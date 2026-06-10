from backend.services.geocoding import (
    DEFAULT_SPORT_CONFIGS,
    _lookup_sports_spots,
    normalize_sport,
    parse_sports_list,
)


def test_normalize_sport_aliases():
    assert normalize_sport("surfing") == "surf"
    assert normalize_sport("biking") == "cycling"
    assert normalize_sport("trail") == "hiking"


def test_parse_sports_list():
    assert parse_sports_list("surf, hiking") == ["surf", "hiking"]
    assert parse_sports_list("sports surfing") == ["surf"]


def test_lookup_sports_spots_lisbon():
    spots = _lookup_sports_spots("Lisbon", "Lisbon", "Portugal")
    assert "Costa da Caparica" in spots


def test_default_sport_configs_cover_weather_sports():
    assert "surf" in DEFAULT_SPORT_CONFIGS
    assert "cycling" in DEFAULT_SPORT_CONFIGS
    assert "hiking" in DEFAULT_SPORT_CONFIGS
