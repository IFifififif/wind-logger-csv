import os
import csv
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

import requests

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"


def get_env(name: str, default: Optional[str] = None) -> Optional[str]:
    v = os.getenv(name)
    return v if (v is not None and v != "") else default


def geocode(place: str) -> Tuple[float, float, str]:
    r = requests.get(GEOCODE_URL, params={"name": place, "count": 1, "language": "zh"}, timeout=15)
    r.raise_for_status()
    results = r.json().get("results")
    if not results:
        raise ValueError(f"找不到地点：{place}")
    top = results[0]
    return float(top["latitude"]), float(top["longitude"]), top["name"]


def fetch_wind(lat: float, lon: float) -> Dict[str, Any]:
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "wind_speed_10m,wind_direction_10m",
        "timezone": "auto",
    }
    r = requests.get(OPEN_METEO_URL, params=params, timeout=15)
    r.raise_for_status()
    cur = r.json().get("current", {})
    if "time" not in cur or "wind_speed_10m" not in cur:
        raise RuntimeError(f"返回数据异常：{cur}")
    return cur


def append_csv(file_path: str, row: Dict[str, Any]):
    exists = os.path.exists(file_path)
    with open(file_path, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "local_time","utc_time","place_name","latitude","longitude",
            "wind_speed_ms","wind_direction_deg"
        ])
        if not exists:
            writer.writeheader()
        writer.writerow(row)


def resolve_location(
    place: Optional[str] = None,
    lat: Optional[float] = None,
    lon: Optional[float] = None,
) -> Tuple[float, float, str]:
    """Resolve latitude/longitude/name from CLI or environment values."""

    env_place = get_env("PLACE_NAME")
    env_lat = get_env("LAT")
    env_lon = get_env("LON")

    place_candidate = place or env_place

    lat_candidate = lat if lat is not None else env_lat
    lon_candidate = lon if lon is not None else env_lon

    if lat_candidate is not None or lon_candidate is not None:
        if lat_candidate is None or lon_candidate is None:
            raise ValueError("请同时提供 LAT 和 LON。")
        lat_value = float(lat_candidate)
        lon_value = float(lon_candidate)
        display_name = place_candidate or f"({lat_value},{lon_value})"
        return lat_value, lon_value, display_name

    if place_candidate:
        lata, lona, name = geocode(place_candidate)
        return float(lata), float(lona), name

    raise ValueError("请设置 PLACE_NAME 或 LAT/LON。")


def build_row(
    cur: Dict[str, Any],
    lat: float,
    lon: float,
    name: str,
    *,
    now: Optional[datetime] = None,
) -> Dict[str, Any]:
    """Return a normalized CSV row for the given wind payload."""

    now = now or datetime.now()
    direction = cur.get("wind_direction_10m")
    return {
        "local_time": now.strftime("%Y-%m-%d %H:%M:%S"),
        "utc_time": cur["time"],
        "place_name": name,
        "latitude": float(lat),
        "longitude": float(lon),
        "wind_speed_ms": float(cur["wind_speed_10m"]),
        "wind_direction_deg": float(direction) if direction is not None else None,
    }
