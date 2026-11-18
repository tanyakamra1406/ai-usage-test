import csv
from datetime import date
from pathlib import Path

from src.common import normalize_id


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
    result = set()
    for employee_id, row in latest_hr.items():
        if normalize_id(row.get("Division")) == "ADV":
            result.add(employee_id)
    return result
