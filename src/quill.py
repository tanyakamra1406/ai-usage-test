import csv
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from src.common import normalize_id


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
) -> tuple[dict[date, dict[str, set[str]]], dict[str, Any]]:
    if wau_threshold < 1:
        raise ValueError("Quill WAU threshold must be at least 1")
    if wpu_threshold < wau_threshold:
        raise ValueError("Quill WPU threshold must not be below the WAU threshold")

    allowed_weeks = set(reporting_weeks)
    counts: dict[date, dict[str, int]] = {}
    for week in reporting_weeks:
        counts[week] = {}

    stats = {
        "quill_rows": 0,
        "exact_duplicate_rows_removed": 0,
        "normalized_whitespace_or_case_rows": 0,
        "timestamp_errors": 0,
        "outside_reporting_window_rows": 0,
        "unknown_hr_rows": 0,
        "non_advisory_rows": 0,
        "generation_rows": 0,
        "measured_weeks": set(),
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

            stats["measured_weeks"].add(week)

            if not employee_id or employee_id not in known_hr_ids:
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
        active = set()
        power = set()
        for employee_id, generation_count in counts[week].items():
            if generation_count >= wau_threshold:
                active.add(employee_id)
            if generation_count >= wpu_threshold:
                power.add(employee_id)
        metrics[week] = {"wau": active, "wpu": power}

    return metrics, stats
