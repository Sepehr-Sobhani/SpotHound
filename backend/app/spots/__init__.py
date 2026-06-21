"""Spot registry — auto-discovers every spot module in this package.

Drop a new file in this directory that defines a module-level ``SPOT =
SpotDefinition(...)`` and it is picked up automatically; no other code changes
needed. ``app.sync.sync_spots`` then upserts each into the database.
"""
from __future__ import annotations

import importlib
import pkgutil

from .base import SpotDefinition

_EXCLUDE = {"base"}


def load_spots() -> dict[str, SpotDefinition]:
    """Return {key: SpotDefinition} for every spot module in this package."""
    spots: dict[str, SpotDefinition] = {}
    for info in pkgutil.iter_modules(__path__):
        if info.name in _EXCLUDE or info.name.startswith("_"):
            continue
        module = importlib.import_module(f"{__name__}.{info.name}")
        spot = getattr(module, "SPOT", None)
        if not isinstance(spot, SpotDefinition):
            continue
        if spot.key in spots:
            raise ValueError(
                f"Duplicate spot key {spot.key!r} (in {info.name} and another module)"
            )
        spots[spot.key] = spot
    return spots


__all__ = ["SpotDefinition", "load_spots"]
