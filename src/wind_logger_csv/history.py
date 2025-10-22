"""Utilities for downloading historical wind data from Open-Meteo."""
from __future__ import annotations

import csv
from datetime import date, datetime
from typing import Any, Dict, Iterable, List, Sequence, Tuple

import requests

ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"
DEFAULT_HOURLY_FIELDS: Tuple[str, ...] = ("wind_speed_10m", "wind_direction_10m")


def parse_ymd(value: str) -> date:
    """Parse a YYYY-MM-DD string into a :class:`datetime.date`."""

    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as exc:  # pragma: no cover - defensive
        raise ValueError("日期格式必须为 YYYY-MM-DD。") from exc


def _prepare_hourly_rows(hourly: Dict[str, Sequence[Any]], fields: Sequence[str]) -> List[Dict[str, Any]]:
    if "time" not in hourly:
        raise RuntimeError("返回数据缺少 hourly.time 字段。")

    times = list(hourly["time"])
    rows: List[Dict[str, Any]] = []

    for field in fields:
        if field not in hourly:
            raise RuntimeError(f"返回数据缺少 hourly.{field} 字段。")
        if len(hourly[field]) != len(times):
            raise RuntimeError(f"hourly.{field} 长度与 time 不一致。")

    for idx, current_time in enumerate(times):
        row = {"time": current_time}
        for field in fields:
            row[field] = hourly[field][idx]
        rows.append(row)

    return rows


def fetch_history(
    lat: float,
    lon: float,
    start_date: date,
    end_date: date,
    *,
    timezone: str = "auto",
    hourly_fields: Sequence[str] = DEFAULT_HOURLY_FIELDS,
) -> List[Dict[str, Any]]:
    """Fetch hourly archive rows for the given time range."""

    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "timezone": timezone,
        "hourly": ",".join(hourly_fields),
    }

    response = requests.get(ARCHIVE_URL, params=params, timeout=30)
    response.raise_for_status()
    payload = response.json()

    hourly = payload.get("hourly")
    if not isinstance(hourly, dict):
        raise RuntimeError("返回数据缺少 hourly 字段。")

    return _prepare_hourly_rows(hourly, hourly_fields)


def write_history_csv(path: str, rows: Iterable[Dict[str, Any]], fields: Sequence[str]) -> None:
    """Write history rows to ``path`` using the provided hourly ``fields``."""

    fieldnames = ["time", *fields]
    with open(path, "w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key) for key in fieldnames})
