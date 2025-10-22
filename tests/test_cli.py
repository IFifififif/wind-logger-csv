from types import SimpleNamespace

import pytest

import wind_logger_csv.cli as cli


def test_resolve_csv_path_prefers_argument(monkeypatch):
    monkeypatch.setenv("CSV_FILE", "env.csv")
    assert cli.resolve_csv_path("cli.csv") == "cli.csv"


def test_resolve_csv_path_falls_back_to_env(monkeypatch):
    monkeypatch.setenv("CSV_FILE", "env.csv")
    assert cli.resolve_csv_path(None) == "env.csv"


def test_resolve_csv_path_rejects_empty(monkeypatch):
    monkeypatch.delenv("CSV_FILE", raising=False)
    with pytest.raises(ValueError):
        cli.resolve_csv_path("")


def test_resolve_csv_path_custom_env(monkeypatch):
    monkeypatch.setenv("HISTORY_CSV_FILE", "history.csv")
    assert (
        cli.resolve_csv_path(None, env_var="HISTORY_CSV_FILE", default="wind_history.csv")
        == "history.csv"
    )


def test_resolve_interval_with_argument():
    assert cli.resolve_interval(5) == 5


def test_resolve_interval_from_env(monkeypatch):
    monkeypatch.setenv("INTERVAL_SEC", "15")
    assert cli.resolve_interval(None) == 15


def test_resolve_interval_rejects_invalid(monkeypatch):
    monkeypatch.setenv("INTERVAL_SEC", "abc")
    with pytest.raises(ValueError):
        cli.resolve_interval(None)


def test_resolve_interval_requires_positive(monkeypatch):
    monkeypatch.setenv("INTERVAL_SEC", "0")
    with pytest.raises(ValueError):
        cli.resolve_interval(None)


def test_parse_hourly_arg_defaults():
    assert cli.parse_hourly_arg(None) == cli.history.DEFAULT_HOURLY_FIELDS


def test_parse_hourly_arg_custom():
    assert cli.parse_hourly_arg("wind_speed_10m,wind_direction_10m") == (
        "wind_speed_10m",
        "wind_direction_10m",
    )


def test_parse_hourly_arg_rejects_empty():
    with pytest.raises(ValueError):
        cli.parse_hourly_arg(", , ")


def test_cmd_history(monkeypatch, tmp_path, capsys):
    args = SimpleNamespace(
        place="赤峰",
        lat=None,
        lon=None,
        csv_file=str(tmp_path / "history.csv"),
        start_date="2024-01-01",
        end_date="2024-01-02",
        timezone="Asia/Shanghai",
        hourly="wind_speed_10m",
    )

    monkeypatch.setattr(cli, "resolve_location", lambda **kwargs: (42.0, 118.0, "赤峰"))

    rows = [
        {"time": "2024-01-01T00:00", "wind_speed_10m": 1.0},
        {"time": "2024-01-01T01:00", "wind_speed_10m": 2.0},
    ]

    def fake_fetch_history(lat, lon, start, end, timezone, hourly_fields):
        assert timezone == "Asia/Shanghai"
        assert hourly_fields == ("wind_speed_10m",)
        return rows

    recorded = {}

    def fake_write_history_csv(path, payload, hourly_fields):
        recorded["path"] = path
        recorded["payload"] = list(payload)
        recorded["fields"] = hourly_fields

    monkeypatch.setattr(cli.history, "fetch_history", fake_fetch_history)
    monkeypatch.setattr(cli.history, "write_history_csv", fake_write_history_csv)

    cli.cmd_history(args)

    assert recorded["path"] == args.csv_file
    assert recorded["fields"] == ("wind_speed_10m",)
    assert recorded["payload"] == rows

    out = capsys.readouterr().out
    assert "history" in out
