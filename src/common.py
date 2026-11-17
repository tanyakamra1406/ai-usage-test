from typing import Any


def normalize_id(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip().upper()
