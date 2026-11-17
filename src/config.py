import json
from datetime import date, timedelta
from pathlib import Path
from typing import Any


def load_config(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        config = json.load(handle)

    if not isinstance(config, dict):
        raise ValueError("reporting_config.json must contain a JSON object")

    reporting_window = config.get("reporting_window")
    if not isinstance(reporting_window, dict):
        raise ValueError("reporting_window must be a JSON object")

    for key in ("first_week_start", "last_week_start"):
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
    window = config["reporting_window"]
    first = parse_config_date(window["first_week_start"])
    last = parse_config_date(window["last_week_start"])

    if last < first:
        raise ValueError("last_week_start must not be before first_week_start")

    weeks = []
    current = first
    while current <= last:
        weeks.append(current)
        current += timedelta(days=7)
    return weeks
