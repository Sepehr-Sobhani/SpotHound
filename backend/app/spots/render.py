"""Fill date placeholders in a spot's steps/condition for a specific target date.

Spots keep dates out of their selectors by using ``{date:<strftime>}`` tokens,
e.g. ``{date:%A, %B %-d, %Y}`` -> "Sunday, June 21, 2026". The target supplies
the concrete date; this module renders the tokens just before a check runs.
"""
from __future__ import annotations

import datetime as dt
import re
from typing import Any

_TOKEN = re.compile(r"\{date:([^}]+)\}")


def render(obj: Any, on_date: dt.date | None) -> Any:
    """Recursively replace {date:FMT} tokens in strings within obj."""
    if isinstance(obj, str):
        if on_date is None:
            return obj
        return _TOKEN.sub(lambda m: on_date.strftime(m.group(1)), obj)
    if isinstance(obj, list):
        return [render(x, on_date) for x in obj]
    if isinstance(obj, dict):
        return {k: render(v, on_date) for k, v in obj.items()}
    return obj


def has_unresolved(obj: Any) -> bool:
    """True if any {date:...} token remains (i.e. a date was required but missing)."""
    if isinstance(obj, str):
        return bool(_TOKEN.search(obj))
    if isinstance(obj, list):
        return any(has_unresolved(x) for x in obj)
    if isinstance(obj, dict):
        return any(has_unresolved(v) for v in obj.values())
    return False
