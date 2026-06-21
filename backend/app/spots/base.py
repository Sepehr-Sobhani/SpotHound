"""The shape of a spot definition.

A *spot* is a code-defined recipe for checking one thing on one site: the URL,
the browser steps to reach the state, and the single condition that means
"available". Spots are authored by a developer (with Claude) — see
docs/ADDING_A_SPOT.md. End users never edit these; they only manage the
*targets* (DB rows) these definitions create: on/off, schedule, subscribers.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class SpotDefinition:
    # Stable unique id, snake_case, also the module filename. NEVER rename —
    # it's the link between this code and its DB row.
    key: str

    # Human-friendly label shown in the UI.
    name: str

    url: str
    steps: list[dict[str, Any]]
    condition: dict[str, Any]

    # Used only when the target row is first created; users tune it afterwards.
    default_interval_seconds: int = 300

    # headful (headless=False) is required for sites with bot detection.
    headless: bool = True

    # Free-form: how this recipe was derived, selectors, gotchas, fragility.
    notes: str = ""
