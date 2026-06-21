"""Definition of a spot: the URL, browser steps, and condition for one check.

See docs/ADDING_A_SPOT.md for how to add one.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class SpotDefinition:
    # Stable unique id (also the module filename); never rename — it links to
    # the target row in the database.
    key: str
    name: str
    url: str

    # May contain {date:<strftime>} tokens, rendered per-target by render.py.
    steps: list[dict[str, Any]]
    condition: dict[str, Any]

    # If True, the target needs a date set before it can run.
    requires_date: bool = True

    default_interval_seconds: int = 300

    # headless=False is required for sites with bot detection.
    headless: bool = True

    # How this recipe was derived; selectors and gotchas.
    notes: str = ""
