from backend.providers.open_meteo import _localize_time, _normalize_marine, _normalize_weather


def test_normalize_weather_maps_hourly_fields():
    raw = {
        "timezone": "Europe/Lisbon",
        "hourly": {
            "time": ["2025-06-09T09:00"],
            "temperature_2m": [18.5],
            "precipitation_probability": [10],
            "wind_speed_10m": [12.0],
        },
    }
    result = _normalize_weather(raw)
    assert len(result["hourly"]) == 1
    entry = result["hourly"][0]
    assert entry["temperature_c"] == 18.5
    assert entry["rain_probability"] == 10
    assert entry["wind_speed_kmh"] == 12.0
    assert "+01:00" in entry["time"] or "09:00" in entry["time"]


def test_normalize_marine_converts_wind_to_knots():
    raw = {
        "timezone": "Europe/Lisbon",
        "hourly": {
            "time": ["2025-06-09T07:00"],
            "wave_height": [1.5],
            "swell_wave_height": [1.4],
            "swell_wave_period": [10],
            "wind_speed_10m": [18.52],
        },
    }
    result = _normalize_marine(raw)
    entry = result["hourly"][0]
    assert entry["wave_height"] == 1.5
    assert entry["swell_period"] == 10
    assert entry["wind_speed_knots"] == 10.0


def test_localize_time_adds_timezone():
    iso = _localize_time("2025-06-09T07:00", "Europe/Lisbon")
    assert "2025-06-09T07:00" in iso
