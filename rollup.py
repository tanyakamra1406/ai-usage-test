import argparse
import csv
import json
from datetime import date, datetime, timedelta, timezone
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


def get_tool_config(config: dict[str, Any], tool_id: str) -> dict[str, Any]:
    for tool in config["tools"]:
        if tool["tool_id"] == tool_id:
            return tool
    raise ValueError(f"tools must contain a {tool_id} tool configuration")


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


def parse_utc_timestamp(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError(f"event_time_utc must include a UTC offset: {value}")
    return parsed.astimezone(timezone.utc)


def quill_week_start(timestamp: datetime) -> date:
    days_since_sunday = (timestamp.weekday() + 1) % 7
    return timestamp.date() - timedelta(days=days_since_sunday)


def load_quill_metrics(
    path: Path,
    known_hr_ids: set[str],
    advisory: set[str],
    reporting_weeks: list[date],
    wau_threshold: int,
    wpu_threshold: int,
) -> tuple[dict[date, dict[str, set[str]]], dict[str, int]]:
    if wau_threshold < 1:
        raise ValueError("Quill WAU threshold must be at least 1")
    if wpu_threshold < wau_threshold:
        raise ValueError("Quill WPU threshold must not be below the WAU threshold")

    allowed_weeks = set(reporting_weeks)
    counts: dict[date, dict[str, int]] = {
        week: {} for week in reporting_weeks
    }
    stats = {
        "quill_rows": 0,
        "exact_duplicate_rows_removed": 0,
        "normalized_whitespace_or_case_rows": 0,
        "timestamp_errors": 0,
        "outside_reporting_window_rows": 0,
        "unknown_hr_rows": 0,
        "non_advisory_rows": 0,
        "generation_rows": 0,
    }
    seen_rows: set[tuple[tuple[str, str], ...]] = set()

    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {"user_id", "event_time_utc", "event_type", "client"}
        if reader.fieldnames is None or not required.issubset(reader.fieldnames):
            raise ValueError("quill_events.csv is missing required columns")

        for row in reader:
            stats["quill_rows"] += 1
            row_key = tuple(sorted(row.items()))
            if row_key in seen_rows:
                stats["exact_duplicate_rows_removed"] += 1
                continue
            seen_rows.add(row_key)

            raw_id = row["user_id"]
            employee_id = normalize_id(raw_id)
            if raw_id != employee_id:
                stats["normalized_whitespace_or_case_rows"] += 1

            try:
                timestamp = parse_utc_timestamp(row["event_time_utc"])
            except (TypeError, ValueError):
                stats["timestamp_errors"] += 1
                continue

            week = quill_week_start(timestamp)
            if week not in allowed_weeks:
                stats["outside_reporting_window_rows"] += 1
                continue

            if not employee_id:
                stats["unknown_hr_rows"] += 1
                continue

            if employee_id not in known_hr_ids:
                stats["unknown_hr_rows"] += 1
                continue

            if employee_id not in advisory:
                stats["non_advisory_rows"] += 1
                continue

            if row["event_type"].strip().lower() != "generation":
                continue

            stats["generation_rows"] += 1
            counts[week][employee_id] = counts[week].get(employee_id, 0) + 1

    metrics: dict[date, dict[str, set[str]]] = {}
    for week in reporting_weeks:
        week_counts = counts[week]
        active = {
            employee_id
            for employee_id, generation_count in week_counts.items()
            if generation_count >= wau_threshold
        }
        power = {
            employee_id
            for employee_id, generation_count in week_counts.items()
            if generation_count >= wpu_threshold
        }
        metrics[week] = {"wau": active, "wpu": power}

    return metrics, stats


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

    quill_config = get_tool_config(config, "quill")

    quill_metrics, quill_stats = load_quill_metrics(
        args.data_dir / "quill_events.csv",
        set(latest_hr),
        advisory,
        weeks,
        int(quill_config["wau_threshold"]),
        int(quill_config["wpu_threshold"]),
    )

    print("\n".join(week.isoformat() for week in weeks))
    print(f"latest_advisory_ids={len(advisory)}")
    print(f"hr_rows={hr_stats['hr_rows']}")
    for week in weeks:
        metrics = quill_metrics[week]
        print(
            f"quill {week.isoformat()} "
            f"wau={len(metrics['wau'])} wpu={len(metrics['wpu'])}"
        )
    print(f"quill_rows={quill_stats['quill_rows']}")
    print(f"exact_duplicate_rows_removed={quill_stats['exact_duplicate_rows_removed']}")
    print(f"unknown_hr_rows={quill_stats['unknown_hr_rows']}")
    print(f"non_advisory_rows={quill_stats['non_advisory_rows']}")


if __name__ == "__main__":
    main()
