from datetime import datetime

import pytest

import wind_logger_csv.core as core


def test_resolve_location_with_coordinates(monkeypatch):
    monkeypatch.delenv("PLACE_NAME", raising=False)
    monkeypatch.delenv("LAT", raising=False)
    monkeypatch.delenv("LON", raising=False)

    lat, lon, name = core.resolve_location(lat=10.5, lon=20.25)

    assert lat == pytest.approx(10.5)
    assert lon == pytest.approx(20.25)
    assert name == "(10.5,20.25)"


def test_resolve_location_requires_both_coordinates(monkeypatch):
    monkeypatch.delenv("LAT", raising=False)
    monkeypatch.delenv("LON", raising=False)

    with pytest.raises(ValueError):
        core.resolve_location(lat=10.0)


def test_resolve_location_uses_geocode(monkeypatch):
    monkeypatch.delenv("PLACE_NAME", raising=False)
    monkeypatch.delenv("LAT", raising=False)
    monkeypatch.delenv("LON", raising=False)

    calls = {}

    def fake_geocode(place: str):
        calls["place"] = place
        return 1.0, 2.0, "Resolved"

    monkeypatch.setattr(core, "geocode", fake_geocode)

    lat, lon, name = core.resolve_location(place="Test City")

    assert calls["place"] == "Test City"
    assert lat == pytest.approx(1.0)
    assert lon == pytest.approx(2.0)
    assert name == "Resolved"


def test_resolve_location_prefers_environment(monkeypatch):
    monkeypatch.setenv("LAT", "33.3")
    monkeypatch.setenv("LON", "44.4")
    monkeypatch.setenv("PLACE_NAME", "Env City")

    lat, lon, name = core.resolve_location()

    assert lat == pytest.approx(33.3)
    assert lon == pytest.approx(44.4)
    assert name == "Env City"


def test_build_row_handles_optional_direction():
    cur = {"time": "2024-01-01T00:00:00Z", "wind_speed_10m": 5.5}
    now = datetime(2024, 1, 1, 12, 0, 0)

    row = core.build_row(cur, 10.0, 20.0, "Test", now=now)

    assert row["local_time"] == "2024-01-01 12:00:00"
    assert row["wind_direction_deg"] is None


def test_build_row_normalizes_numeric_types():
    cur = {
        "time": "2024-01-01T00:00:00Z",
        "wind_speed_10m": "7.5",
        "wind_direction_10m": "180",
    }
    now = datetime(2024, 1, 1, 8, 30, 0)

    row = core.build_row(cur, 30, 40, "City", now=now)

    assert row["local_time"] == "2024-01-01 08:30:00"
    assert row["wind_speed_ms"] == pytest.approx(7.5)
    assert row["wind_direction_deg"] == pytest.approx(180.0)
    assert row["latitude"] == pytest.approx(30.0)
    assert row["longitude"] == pytest.approx(40.0)
