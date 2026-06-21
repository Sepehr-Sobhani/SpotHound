"""Registry that auto-discovers spot modules.

Any module here defining ``SPOT = SpotDefinition(...)`` is picked up automatically.
"""
from __future__ import annotations

import importlib
import pkgutil

from .base import SpotDefinition

_EXCLUDE = {"base", "render"}


def load_spots() -> dict[str, SpotDefinition]:
    spots: dict[str, SpotDefinition] = {}
    for info in pkgutil.iter_modules(__path__):
        if info.name in _EXCLUDE or info.name.startswith("_"):
            continue
        module = importlib.import_module(f"{__name__}.{info.name}")
        spot = getattr(module, "SPOT", None)
        if not isinstance(spot, SpotDefinition):
            continue
        if spot.key in spots:
            raise ValueError(f"Duplicate spot key {spot.key!r}")
        spots[spot.key] = spot
    return spots


__all__ = ["SpotDefinition", "load_spots"]
