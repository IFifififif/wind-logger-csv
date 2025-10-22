import time
from argparse import ArgumentParser
from typing import Optional, Tuple, Union
from dotenv import load_dotenv

from .core import (
    append_csv,
    build_row,
    fetch_wind,
    get_env,
    resolve_location,
)
from . import history

load_dotenv()


def resolve_csv_path(
    explicit: Optional[str],
    *,
    env_var: str = "CSV_FILE",
    default: str = "wind_log.csv",
) -> str:
    if explicit is not None:
        if explicit.strip() == "":
            raise ValueError("CSV 文件路径不能为空。")
        return explicit

    path = get_env(env_var, default)
    if not path:
        raise ValueError("CSV 文件路径不能为空。")
    return path


def resolve_interval(explicit: Optional[int]) -> int:
    candidate: Union[int, str, None] = explicit if explicit is not None else get_env("INTERVAL_SEC", "60")
    try:
        interval = int(candidate)
    except (TypeError, ValueError) as exc:
        raise ValueError("INTERVAL_SEC 必须为整数。") from exc
    if interval <= 0:
        raise ValueError("INTERVAL_SEC 必须为正整数。")
    return interval


def parse_hourly_arg(value: Optional[str]) -> Tuple[str, ...]:
    if value is None:
        return history.DEFAULT_HOURLY_FIELDS

    fields = tuple(filter(None, (item.strip() for item in value.split(","))))
    if not fields:
        raise ValueError("hourly 参数不能为空。")
    return fields


def cmd_once(args):
    lat, lon, name = resolve_location(place=args.place, lat=args.lat, lon=args.lon)
    cur = fetch_wind(lat, lon)
    row = build_row(cur, lat, lon, name)
    append_csv(resolve_csv_path(args.csv_file), row)
    print(f"[once] {name} | {row['wind_speed_ms']:.2f} m/s @ {row['utc_time']}")


def cmd_run(args):
    interval = resolve_interval(args.interval)
    lat, lon, name = resolve_location(place=args.place, lat=args.lat, lon=args.lon)
    csv_path = resolve_csv_path(args.csv_file)
    print(f"写入 CSV：{csv_path}")
    print(f"采集区域：{name}，间隔：{interval} 秒\n")
    while True:
        try:
            cur = fetch_wind(lat, lon)
            row = build_row(cur, lat, lon, name)
            append_csv(csv_path, row)
            direction_display = (
                f"{row['wind_direction_deg']:.2f}"
                if row["wind_direction_deg"] is not None
                else "-"
            )
            print(
                f"[{row['local_time']}] 已写入 {name} | 风速 {row['wind_speed_ms']:.2f} m/s, "
                f"风向 {direction_display}°"
            )
        except Exception as e:
            print("异常：", e)
        time.sleep(interval)


def cmd_show(args):
    path = resolve_csv_path(args.csv_file)
    limit = args.limit if args.limit is not None else 10
    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            header, rows = (lines[0], lines[1:]) if lines else ("", [])
            tail = rows if limit <= 0 else rows[-limit:]
            print(header.strip())
            for ln in tail:
                print(ln.strip())
    except FileNotFoundError:
        print(f"未找到 CSV：{path}")


def cmd_history(args):
    start = history.parse_ymd(args.start_date)
    end = history.parse_ymd(args.end_date)
    if end < start:
        raise ValueError("结束日期必须大于或等于开始日期。")

    lat, lon, name = resolve_location(place=args.place, lat=args.lat, lon=args.lon)
    hourly_fields: Tuple[str, ...] = parse_hourly_arg(args.hourly)
    rows = history.fetch_history(
        lat,
        lon,
        start,
        end,
        timezone=args.timezone,
        hourly_fields=hourly_fields,
    )

    csv_path = resolve_csv_path(
        args.csv_file,
        env_var="HISTORY_CSV_FILE",
        default="wind_history.csv",
    )
    history.write_history_csv(csv_path, rows, hourly_fields)
    print(
        f"[history] {name} {start.isoformat()} → {end.isoformat()} | "
        f"共 {len(rows)} 条记录，已保存至 {csv_path}"
    )


def main():
    parser = ArgumentParser(prog="wind-csv", description="Log wind speed to local CSV.")
    sub = parser.add_subparsers()

    def add_location_options(p):
        p.add_argument("--place", help="覆盖 PLACE_NAME 环境变量")
        p.add_argument("--lat", type=float, help="覆盖 LAT 环境变量 (需要同时提供 --lon)")
        p.add_argument("--lon", type=float, help="覆盖 LON 环境变量 (需要同时提供 --lat)")
        p.add_argument("--csv", dest="csv_file", help="覆盖 CSV_FILE 输出路径")

    p_once = sub.add_parser("once", help="Fetch once and append to CSV")
    add_location_options(p_once)
    p_once.set_defaults(func=cmd_once)

    p_run = sub.add_parser("run", help="Poll continuously and append to CSV")
    add_location_options(p_run)
    p_run.add_argument("--interval", type=int, help="覆盖 INTERVAL_SEC 轮询间隔 (秒)")
    p_run.set_defaults(func=cmd_run)

    p_show = sub.add_parser("show", help="Show last N lines from CSV")
    p_show.add_argument("--limit", type=int, default=10)
    p_show.add_argument("--csv", dest="csv_file", help="覆盖 CSV_FILE 输出路径")
    p_show.set_defaults(func=cmd_show)

    p_history = sub.add_parser("history", help="Download historical wind data and save to CSV")
    add_location_options(p_history)
    p_history.add_argument("--start-date", required=True, dest="start_date", help="开始日期 (YYYY-MM-DD)")
    p_history.add_argument("--end-date", required=True, dest="end_date", help="结束日期 (YYYY-MM-DD)")
    p_history.add_argument("--timezone", default="auto", help="Open-Meteo 接口的 timezone 参数")
    p_history.add_argument(
        "--hourly",
        help="逗号分隔的 hourly 字段列表 (默认 wind_speed_10m,wind_direction_10m)",
    )
    p_history.add_argument(
        "--csv",
        dest="csv_file",
        help="覆盖 HISTORY_CSV_FILE 输出路径 (默认 wind_history.csv)",
    )
    p_history.set_defaults(func=cmd_history)

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
