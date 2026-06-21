# 🐕 SpotHound

Watch any website for a condition and get pinged when it's met. Built originally to catch a sold-out parking pass the moment it opens — now general enough to monitor anything.

## How it works

Every check goes through the same path: **a real browser (Playwright) opens the page, runs a few steps (clicks/selects), and evaluates a condition.** Because it drives a real browser, it handles everything — plain pages, JSON-API apps, and JavaScript sites with bot detection — through one engine.

**Spots vs targets** (see `CLAUDE.md`):

- A **spot** is a code-defined recipe (URL + steps + condition) living in
  `backend/app/spots/<key>.py`. Adding one is a developer task — see
  `docs/ADDING_A_SPOT.md`.
- A **target** is the DB row that recipe becomes. Users manage targets in the UI
  — **on/off, scheduling, and who gets notified** — but never the check logic.

A spot module looks like:

```python
SPOT = SpotDefinition(
    key="buntzen_lake_all_day",
    name="Buntzen Lake — All Day Pass (Sun Jun 21)",
    url="https://yodelportal.com/buntzen-lake/All-Day-Pass",
    headless=False,                       # site blocks headless browsers
    default_interval_seconds=300,
    steps=[
        {"action": "wait", "ms": 4000},
        {"action": "click", "selector": 'button[aria-label="Sunday 21"]'},
    ],
    condition={"selector": 'a:has-text("Add To Cart")', "check": "enabled"},
)
```

When the condition flips to true, every subscribed user gets a Telegram message.

## Architecture

| Piece | Tech | Hosting (all free) |
|-------|------|--------------------|
| Frontend | React + Tailwind | Vercel |
| API + scheduler + browser | FastAPI + APScheduler + Playwright | Oracle Cloud Always Free VM (Docker + Chromium + xvfb) |
| Database | Postgres | Neon |
| Notifications | Telegram bot | — |

## Status

Phase 1 (backend) and the spots architecture are **done**. Phase 2 (React +
Tailwind UI) is next. Full detail in `docs/ROADMAP.md`.

## Local development

Everything is wrapped in the Makefile — `make help` lists targets:

```bash
make db        # start local Postgres (waits until ready)
make install   # uv sync
cp backend/.env.example backend/.env   # then edit secrets
make seed      # admin user + sync spots into targets (created disabled)
make dev       # API + scheduler on :8000

make test                                # run all spots through the engine, no DB
make selftest spot=bc_parks_alouette_pm  # one spot
make reset                               # wipe DB + reseed
```

> Uses **uv** (not pip) and Python 3.13. macOS: run `sudo xcodebuild -license
> accept` once to enable `make`.

See `CLAUDE.md` for architecture and conventions, and `docs/ADDING_A_SPOT.md` to
add a new site to monitor.
