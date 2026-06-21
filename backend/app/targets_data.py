"""The two reference targets, expressed purely as config.

Nothing here is special-cased in code — these are just the rows the seed
script inserts, and they double as fixtures for selftest.py. Add/edit targets
through the API/UI, not here.
"""

BCPARKS = {
    "name": "BC Parks — Alouette South Beach PM (Sun Jun 21)",
    "url": "https://reserve.bcparks.ca/dayuse/",
    "headless": True,  # plain Angular app, no bot detection
    "interval_seconds": 60,
    "steps": [
        {"action": "click", "selector": 'button[aria-label="Book a pass for Golden Ears Provincial Park"]'},
        {"action": "wait", "ms": 1500},
        {"action": "click", "selector": 'button[title="Select a Date"]'},
        {"action": "wait", "ms": 800},
        {"action": "click", "selector": 'div[aria-label="Sunday, June 21, 2026"]'},
        {"action": "wait", "ms": 800},
        {"action": "select", "selector": "select", "label": "Alouette Lake South Beach Day-Use Parking Lot - Parking"},
        {"action": "wait", "ms": 2000},
    ],
    "condition": {"selector": "#visitTimePM", "check": "enabled"},
}

BUNTZEN = {
    "name": "Buntzen Lake — All Day Pass (Sun Jun 21)",
    "url": "https://yodelportal.com/buntzen-lake/All-Day-Pass",
    "headless": False,  # site 403s headless; needs headful (xvfb on the server)
    "interval_seconds": 300,  # bot-protected — poll gently
    "steps": [
        {"action": "wait", "ms": 4000},
        {"action": "click", "selector": 'button[aria-label="Sunday 21"]'},
        {"action": "wait", "ms": 2500},
    ],
    "condition": {"selector": 'a:has-text("Add To Cart")', "check": "enabled"},
}

REFERENCE_TARGETS = [BCPARKS, BUNTZEN]
