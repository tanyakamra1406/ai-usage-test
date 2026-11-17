import re
from datetime import date, datetime, timedelta
from pathlib import Path

from openpyxl import load_workbook

from src.common import normalize_id


def atlas_week_start(week_ending: date) -> date:
    return week_ending - timedelta(days=6)


def find_usage_header(workbook) -> tuple[int, dict[str, int]]:
    sheet = workbook["Usage"]
    required = ("User ID", "Week Ending", "Queries Run", "Active Days")

    for row_number, row in enumerate(sheet.iter_rows(values_only=True), start=1):
        headers = {}
        for index, value in enumerate(row):
            if value in required:
                headers[str(value)] = index
        if all(name in headers for name in required):
            return row_number, headers

    raise ValueError("Atlas Usage sheet is missing required columns")


def extract_delivery_date(path: Path) -> date:
    match = re.search(r"_(\d{8})\.xlsx$", path.name)
    if match is None:
        raise ValueError(f"Atlas filename does not contain an extract date: {path.name}")
    return datetime.strptime(match.group(1), "%Y%m%d").date()


def parse_week_ending(value: date | datetime | str) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return datetime.strptime(str(value).strip(), "%Y-%m-%d").date()


def read_atlas_delivery(
    path: Path,
    known_hr_ids: set[str],
    advisory: set[str],
    reporting_weeks: list[date],
    stats: dict[str, int],
) -> dict[date, dict[str, tuple[int, int]]]:
    workbook = load_workbook(path, data_only=True, read_only=True)
    header_row, headers = find_usage_header(workbook)
    sheet = workbook["Usage"]
    week_rows: dict[date, dict[str, tuple[int, int]]] = {}

    for row in sheet.iter_rows(min_row=header_row + 1, values_only=True):
        stats["atlas_rows"] += 1
        employee_id = normalize_id(row[headers["User ID"]])

        if not employee_id:
            stats["atlas_blank_ids"] += 1
            continue
        if employee_id not in known_hr_ids:
            stats["atlas_unknown_hr_rows"] += 1
            continue
        if employee_id not in advisory:
            stats["atlas_non_advisory_rows"] += 1
            continue

        week = atlas_week_start(parse_week_ending(row[headers["Week Ending"]]))
        if week not in reporting_weeks:
            continue

        queries = int(row[headers["Queries Run"]] or 0)
        active_days = int(row[headers["Active Days"]] or 0)
        week_rows.setdefault(week, {})[employee_id] = (queries, active_days)

    workbook.close()
    return week_rows


def build_atlas_metrics(
    reporting_weeks: list[date],
    deliveries: dict[date, tuple[date, dict[str, tuple[int, int]]]],
    wau_threshold: int,
    wpu_threshold: int,
) -> dict[date, dict[str, set[str]]]:
    metrics: dict[date, dict[str, set[str]]] = {}

    for week in reporting_weeks:
        active = set()
        power = set()
        delivery = deliveries.get(week)

        if delivery is not None:
            people = delivery[1]
            for employee_id, values in people.items():
                queries, active_days = values
                if active_days >= wau_threshold:
                    active.add(employee_id)
                if queries >= wpu_threshold:
                    power.add(employee_id)

        metrics[week] = {"wau": active, "wpu": power}

    return metrics


def load_atlas_metrics(
    atlas_dir: Path,
    known_hr_ids: set[str],
    advisory: set[str],
    reporting_weeks: list[date],
    wau_threshold: int,
    wpu_threshold: int,
) -> tuple[dict[date, dict[str, set[str]]], dict[str, int]]:
    if wau_threshold < 1:
        raise ValueError("Atlas WAU threshold must be at least 1")
    if wpu_threshold < 1:
        raise ValueError("Atlas WPU threshold must be at least 1")

    deliveries: dict[date, tuple[date, dict[str, tuple[int, int]]]] = {}
    stats = {
        "atlas_files": 0,
        "atlas_rows": 0,
        "atlas_blank_ids": 0,
        "atlas_unknown_hr_rows": 0,
        "atlas_non_advisory_rows": 0,
        "atlas_replacements": 0,
    }

    for path in sorted(atlas_dir.glob("atlas_usage_*.xlsx")):
        stats["atlas_files"] += 1
        extract_date = extract_delivery_date(path)
        week_rows = read_atlas_delivery(
            path,
            known_hr_ids,
            advisory,
            reporting_weeks,
            stats,
        )

        for week, people in week_rows.items():
            previous = deliveries.get(week)
            if previous is not None and extract_date > previous[0]:
                stats["atlas_replacements"] += 1
            if previous is None or extract_date > previous[0]:
                deliveries[week] = (extract_date, people)

    metrics = build_atlas_metrics(
        reporting_weeks,
        deliveries,
        wau_threshold,
        wpu_threshold,
    )
    return metrics, stats
