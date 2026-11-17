import argparse
import json
from datetime import date, timedelta
from pathlib import Path
from typing import Any


DEFAULT_DATA_DIR = Path("data")


def load_config(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        config = json.load(handle)

    if not isinstance(config, dict):
        raise ValueError("reporting_config.json must contain a JSON object")

    reporting_window = config.get("reporting_window")
    if not isinstance(reporting_window, dict):
        raise ValueError("reporting_window must be a JSON object")

    required_keys = ("first_week_start", "last_week_start")
    for key in required_keys:
        if not isinstance(reporting_window.get(key), str):
            raise ValueError(f"reporting_window.{key} must be a date string")

    tools = config.get("tools")
    if not isinstance(tools, list):
        raise ValueError("tools must be a JSON array")

    for tool in tools:
        if not isinstance(tool, dict) or not isinstance(tool.get("tool_id"), str):
            raise ValueError("each tool must contain a string tool_id")

    return config


def parse_config_date(value: str) -> date:
    parsed = date.fromisoformat(value)
    if parsed.weekday() != 6:
        raise ValueError(f"week_start must be a Sunday: {value}")
    return parsed


def reporting_weeks(config: dict[str, Any]) -> list[date]:
    reporting_window = config["reporting_window"]
    first = parse_config_date(reporting_window["first_week_start"])
    last = parse_config_date(reporting_window["last_week_start"])

    if last < first:
        raise ValueError("last_week_start must not be before first_week_start")

    weeks = []
    current = first
    while current <= last:
        weeks.append(current)
        current += timedelta(days=7)
    return weeks


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the weekly AI tool adoption rollup")
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=DEFAULT_DATA_DIR,
        help="directory containing reporting_config.json and source files",
    )
    args = parser.parse_args()

    config = load_config(args.data_dir / "reporting_config.json")
    weeks = reporting_weeks(config)
    print("\n".join(week.isoformat() for week in weeks))


if __name__ == "__main__":
    main()
