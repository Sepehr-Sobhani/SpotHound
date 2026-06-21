"""Buntzen Lake — All Day Pass (Yodel portal).

Site: https://yodelportal.com/buntzen-lake/All-Day-Pass  (Framework7 SPA)

Discovery notes
---------------
HARDER target. The real backend is api.yodelpass.com, but the site has
**bot detection** (returns 403 to a headless browser) and **reCAPTCHA
Enterprise**. So:

  * `headless=False` is REQUIRED — with a headless browser the page renders
    only "403 Forbidden". The engine's anti-bot context (real UA,
    --disable-blink-features=AutomationControlled, navigator.webdriver hidden)
    plus headful is enough to load it. On the server this runs under xvfb.
  * reCAPTCHA only guards the actual *purchase*, not viewing availability, so
    SpotHound just detects the open slot and notifies; the human books.
  * Poll gently (every few minutes) so we don't trip rate limiting.

Flow: load page -> click the date button (`aria-label="Sunday 21"`) -> read the
"Add To Cart" link. It carries class `btn-disbled` (sic) and
`aria-disabled="true"` while full; both clear when a pass is available -> our
"enabled" condition (the engine treats the misspelled class as disabled too).

Fragility: the date button's aria-label is date-specific ("Sunday 21").
"""
from .base import SpotDefinition

SPOT = SpotDefinition(
    key="buntzen_lake_all_day",
    name="Buntzen Lake — All Day Pass (Sun Jun 21)",
    url="https://yodelportal.com/buntzen-lake/All-Day-Pass",
    headless=False,
    default_interval_seconds=300,
    steps=[
        {"action": "wait", "ms": 4000},
        {"action": "click", "selector": 'button[aria-label="Sunday 21"]'},
        {"action": "wait", "ms": 2500},
    ],
    condition={"selector": 'a:has-text("Add To Cart")', "check": "enabled"},
)
