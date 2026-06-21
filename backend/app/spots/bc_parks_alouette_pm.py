"""BC Parks — Alouette Lake South Beach Day-Use, PM parking pass.

Site: https://reserve.bcparks.ca/dayuse/  (Angular SPA, no bot detection)

Discovery notes
---------------
The site also exposes a clean public JSON API
(`GET /api/reservation?facility=Alouette Lake South Beach Day-Use Parking Lot&park=0008`,
needs an `Accept: application/json` header) returning per-day AM/PM capacity.
We nonetheless drive it through the browser like every other spot, for one
uniform engine. The booking flow:

  Book a Pass (Golden Ears) -> open date picker -> pick the date
  -> choose the parking lot in the <select> -> read the PM radio's state.

The PM radio (`#visitTimePM`) carries the native `disabled` attribute while the
slot is Full; it loses it when a pass opens -> that's our condition.

Fragility: the date selector is date-specific (`aria-label="Sunday, June 21,
2026"`). Update `steps` when targeting a different day.
"""
from .base import SpotDefinition

SPOT = SpotDefinition(
    key="bc_parks_alouette_pm",
    name="BC Parks — Alouette South Beach PM (Sun Jun 21)",
    url="https://reserve.bcparks.ca/dayuse/",
    headless=True,
    default_interval_seconds=60,
    steps=[
        {"action": "click", "selector": 'button[aria-label="Book a pass for Golden Ears Provincial Park"]'},
        {"action": "wait", "ms": 1500},
        {"action": "click", "selector": 'button[title="Select a Date"]'},
        {"action": "wait", "ms": 800},
        {"action": "click", "selector": 'div[aria-label="Sunday, June 21, 2026"]'},
        {"action": "wait", "ms": 800},
        {"action": "select", "selector": "select", "label": "Alouette Lake South Beach Day-Use Parking Lot - Parking"},
        {"action": "wait", "ms": 2000},
    ],
    condition={"selector": "#visitTimePM", "check": "enabled"},
)
