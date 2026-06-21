# 🐕 SpotHound

Watch any website for a condition and get pinged when it's met. Built originally to catch a sold-out parking pass the moment it opens — now general enough to monitor anything.

## How it works

Every target is checked the same way: **a real browser (Playwright) opens the page, runs a few steps (clicks/selects), and evaluates a condition.** Because it drives a real browser, it handles everything — plain pages, JSON-API apps, and JavaScript sites with bot detection — through one engine.

A target is just config you can edit in the UI:

```jsonc
{
  "name": "Buntzen Lake — All Day Pass (Sun Jun 21)",
  "url": "https://yodelportal.com/buntzen-lake/All-Day-Pass",
  "steps": [
    { "action": "wait",  "ms": 4000 },
    { "action": "click", "selector": "button[aria-label=\"Sunday 21\"]" }
  ],
  "condition": { "selector": "a:has-text(\"Add To Cart\")", "check": "enabled" },
  "interval_seconds": 300,
  "enabled": true
}
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

- **Phase 1 (this scaffold):** browser engine, target model, scheduler, Telegram, basic auth + CRUD API. ✅
- **Phase 2:** React + Tailwind UI (target editor with live "Test" button, on/off toggles, user management).
- **Phase 3:** richer schedules, multi-user notification routing.
- **Phase 4:** Dockerize + deploy (Vercel + Neon + Oracle VM).

## Local development

```bash
# 1. start Postgres
docker compose up -d db

# 2. backend
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
cp .env.example .env          # then edit secrets

# 3. seed admin user + the two reference targets
python -m app.seed

# 4. run the API + scheduler
uvicorn app.main:app --reload
```

Quick engine check without a database:

```bash
cd backend && source .venv/bin/activate
python selftest.py            # runs both reference targets through the engine
```
