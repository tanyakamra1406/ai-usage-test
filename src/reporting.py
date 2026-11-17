import csv
from datetime import date
from pathlib import Path
from typing import Any


COLUMNS = ("week_start", "tool_id", "wau", "wpu", "wpu_rate", "measured")


def wpu_rate(wau: int, wpu: int) -> str:
    if wau == 0:
        return "Infinity"
    return f"{wpu / wau:.4f}"


def build_tool_row(
    week: date,
    tool_id: str,
    wau: set[str] | None,
    wpu: set[str] | None,
    measured: bool,
) -> dict[str, Any]:
    if not measured:
        return {
            "week_start": week.isoformat(),
            "tool_id": tool_id,
            "wau": "",
            "wpu": "",
            "wpu_rate": "",
            "measured": "false",
        }

    wau_count = len(wau or set())
    wpu_count = len(wpu or set())
    return {
        "week_start": week.isoformat(),
        "tool_id": tool_id,
        "wau": wau_count,
        "wpu": wpu_count,
        "wpu_rate": wpu_rate(wau_count, wpu_count),
        "measured": "true",
    }


def build_reporting_rows(
    weeks: list[date],
    quill_metrics: dict[date, dict[str, set[str]]],
    atlas_metrics: dict[date, dict[str, set[str]]],
    quill_measured: dict[date, bool],
    atlas_measured: dict[date, bool],
) -> list[dict[str, Any]]:
    rows = []

    for week in weeks:
        quill = quill_metrics[week]
        atlas = atlas_metrics[week]

        rows.append(build_tool_row(
            week,
            "quill",
            quill["wau"],
            quill["wpu"],
            quill_measured[week],
        ))
        rows.append(build_tool_row(
            week,
            "atlas",
            atlas["wau"],
            atlas["wpu"],
            atlas_measured[week],
        ))

        both_measured = quill_measured[week] and atlas_measured[week]
        if both_measured:
            any_wau = quill["wau"] | atlas["wau"]
            any_wpu = quill["wpu"] | atlas["wpu"]
            rows.append(build_tool_row(
                week,
                "ANY",
                any_wau,
                any_wpu,
                True,
            ))
        else:
            rows.append(build_tool_row(
                week,
                "ANY",
                None,
                None,
                False,
            ))

    return rows


def write_weekly_metrics(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
