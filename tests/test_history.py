from datetime import date

import pytest

import wind_logger_csv.history as history


class FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):  # pragma: no cover - simple stub
        return None

    def json(self):
        return self._payload


def test_parse_ymd_success():
    assert history.parse_ymd("2024-01-02") == date(2024, 1, 2)


def test_fetch_history_returns_rows(monkeypatch):
    payload = {
        "hourly": {
            "time": ["2024-01-01T00:00", "2024-01-01T01:00"],
            "wind_speed_10m": [1.0, 2.0],
        }
    }
    captured = {}

    def fake_get(url, params, timeout):
        captured["url"] = url
        captured["params"] = params
        assert timeout == 30
        return FakeResponse(payload)

    monkeypatch.setattr(history.requests, "get", fake_get)

    rows = history.fetch_history(
        42.0,
        118.0,
        date(2024, 1, 1),
        date(2024, 1, 2),
        hourly_fields=("wind_speed_10m",),
    )

    assert captured["url"] == history.ARCHIVE_URL
    assert captured["params"]["start_date"] == "2024-01-01"
    assert captured["params"]["end_date"] == "2024-01-02"
    assert rows == [
        {"time": "2024-01-01T00:00", "wind_speed_10m": 1.0},
        {"time": "2024-01-01T01:00", "wind_speed_10m": 2.0},
    ]


def test_fetch_history_requires_field(monkeypatch):
    payload = {"hourly": {"time": ["2024-01-01T00:00"]}}

    def fake_get(url, params, timeout):
        return FakeResponse(payload)

    monkeypatch.setattr(history.requests, "get", fake_get)

    with pytest.raises(RuntimeError):
        history.fetch_history(
            42.0,
            118.0,
            date(2024, 1, 1),
            date(2024, 1, 2),
            hourly_fields=("wind_speed_10m",),
        )


def test_write_history_csv(tmp_path):
    rows = [
        {"time": "2024-01-01T00:00", "wind_speed_10m": 1.0, "wind_direction_10m": 180},
    ]
    path = tmp_path / "out.csv"

    history.write_history_csv(str(path), rows, ("wind_speed_10m", "wind_direction_10m"))

    content = path.read_text(encoding="utf-8").strip().splitlines()
    assert content[0] == "time,wind_speed_10m,wind_direction_10m"
    assert "2024-01-01T00:00" in content[1]
