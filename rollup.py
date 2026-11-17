import argparse
import csv
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


def normalize_id(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip().upper()


def load_latest_hr(path: Path) -> tuple[dict[str, dict[str, str]], dict[str, int]]:
    latest: dict[str, dict[str, str]] = {}
    stats = {
        "hr_rows": 0,
        "blank_ids": 0,
        "normalized_whitespace_or_case_rows": 0,
        "duplicate_normalized_ids": 0,
    }

    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {"Employee_ID", "Division", "Effective_Date"}
        if reader.fieldnames is None or not required.issubset(reader.fieldnames):
            raise ValueError("hr_roster.csv is missing required columns")

        seen_ids: dict[str, int] = {}
        for row in reader:
            stats["hr_rows"] += 1
            raw_id = row["Employee_ID"]
            employee_id = normalize_id(raw_id)

            if not employee_id:
                stats["blank_ids"] += 1
                continue

            if raw_id != employee_id:
                stats["normalized_whitespace_or_case_rows"] += 1

            seen_ids[employee_id] = seen_ids.get(employee_id, 0) + 1

            effective_date = date.fromisoformat(row["Effective_Date"])
            existing = latest.get(employee_id)
            if existing is None:
                latest[employee_id] = dict(row)
                continue

            existing_date = date.fromisoformat(existing["Effective_Date"])
            if effective_date > existing_date:
                latest[employee_id] = dict(row)

    stats["duplicate_normalized_ids"] = sum(
        count - 1 for count in seen_ids.values() if count > 1
    )
    return latest, stats


def advisory_ids(latest_hr: dict[str, dict[str, str]]) -> set[str]:
    return {
        employee_id
        for employee_id, row in latest_hr.items()
        if normalize_id(row.get("Division")) == "ADV"
    }


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
    latest_hr, hr_stats = load_latest_hr(args.data_dir / "hr_roster.csv")
    advisory = advisory_ids(latest_hr)
    print("\n".join(week.isoformat() for week in weeks))
    print(f"latest_advisory_ids={len(advisory)}")
    print(f"hr_rows={hr_stats['hr_rows']}")


if __name__ == "__main__":
    main()
