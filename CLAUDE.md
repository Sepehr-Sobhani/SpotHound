# CLAUDE.md — SpotHound

Guide for Claude (and humans) working in this repo. Read this first.

## What SpotHound is

A web app that watches websites for a condition and notifies users when it's
met (e.g. a sold-out parking pass opening up).

## The one big idea: Spots vs Targets

There are **two layers**, and the permission model follows the split:

- **Spot** — a *code-defined recipe* for checking one thing: URL + browser
  steps + one condition. Lives in `backend/app/spots/<key>.py`. Authoring a spot
  is a developer task (do it with Claude). **End users cannot create or edit the
  check logic.** See `docs/ADDING_A_SPOT.md`.
- **Target** — a *database row* created by syncing a spot. This is what users
  manage in the UI: **enable/disable, scheduling, and subscribers**. They never
  touch url/steps/condition.

Field ownership on a `Target` (`backend/app/models.py`):

| Definition-owned (synced from the spot, read-only in UI) | User-owned (editable in UI) |
|---|---|
| `name`, `url`, `steps`, `condition`, `headless` | `target_date`, `enabled`, `interval_seconds`, `active_days`, `active_start`, `active_end`, subscriptions |

**Dates are parameters, never hardcoded.** A spot's selectors use
`{date:<strftime>}` tokens (e.g. `{date:%A, %B %-d, %Y}` →
"Sunday, June 21, 2026"); each target supplies its own `target_date`, rendered
into the steps/condition just before a check by `app/spots/render.py`. So one
spot recipe monitors any date — the user just sets/changes the target's date. A
target whose tokens can't be filled (no date set) reports `needs_date` and is
skipped.

`app/sync.py::sync_spots` upserts definition-owned fields and **never** overwrites
user-owned ones. New targets are created **disabled**. Sync runs on startup and
via `POST /admin/sync-spots`.

## One engine for everything

Every check goes through `backend/app/engine.py::run_check` — a real Playwright
browser with an anti-bot context (real UA, `--disable-blink-features=
AutomationControlled`, hidden `navigator.webdriver`). It opens the URL, runs the
steps, evaluates the condition. No HTTP-only fast path; the browser handles
plain pages, JSON-API SPAs, and bot-protected sites uniformly.

- **Steps**: `click`, `select` (by `label` or `value`), `fill`, `wait` (`ms` or
  `selector`). Each has a `selector`.
- **Conditions** (`check`): `enabled`, `disabled`, `exists`, `not_exists`,
  `text_present`, `text_absent` (+ `value` for the text checks). "Disabled" is
  detected across `[disabled]`, `aria-disabled="true"`, and classes containing
  `disabled`/`disbled`.
- **`headless`**: set `False` for sites that 403 a headless browser
  (e.g. Yodel/Buntzen). On the server, headful runs under `xvfb` (see Dockerfile).

## Architecture / hosting

| Piece | Tech | Hosting (all free) |
|---|---|---|
| Frontend (Phase 2) | React + Tailwind | Vercel |
| API + scheduler + browser | FastAPI + APScheduler + Playwright | Oracle Cloud Always Free VM (Docker + Chromium + xvfb) |
| Database | Postgres | Neon |
| Notifications | Telegram bot | — |

Each enabled target is one APScheduler job on its own interval
(`backend/app/scheduler.py`). On a transition into "available" it notifies every
subscriber via Telegram (`backend/app/notify.py`); it does **not** re-notify
while it stays available.

## Repo layout

```
backend/
  app/
    engine.py        # the Playwright check engine (depends only on Playwright)
    spots/           # one module per spot (the recipes) + registry + base
    sync.py          # sync_spots(): spot modules -> Target rows
    scheduler.py     # APScheduler; one job per enabled target
    notify.py        # Telegram
    models.py schemas.py security.py deps.py config.py database.py
    routers/         # auth, users, targets, admin
    seed.py          # create admin + sync spots + subscribe admin
  selftest.py        # run spots through the engine, no DB needed
  Dockerfile         # python + uv + chromium + xvfb
docker-compose.yml   # local Postgres (service `db`)
Makefile             # make targets wrapping the commands below
docs/                # ADDING_A_SPOT.md, ROADMAP.md
```

## Conventions (important)

- **uv only** for Python — `uv add`, `uv sync`, `uv run`. No pip/requirements.txt.
- **Python 3.13** (latest stable).
- **bcrypt directly**, not passlib (passlib 1.7.4 breaks with bcrypt 5.x).
- Keep `engine.py` dependency-light (Playwright only) so `selftest.py` runs it
  without the DB/app.
- Spot `key` is permanent — it's the DB link. Never rename a key.

## Dev workflow

Use the Makefile (run `make help` to list targets):

```bash
make db        # start local Postgres (waits until ready)
make install   # uv sync
# cp backend/.env.example backend/.env  then edit secrets
make seed      # admin user + sync spots into targets (created disabled)
make dev       # API + scheduler on :8000

make test            # run all spots through the engine, no DB
make selftest spot=bc_parks_alouette_pm   # one spot
make reset           # wipe DB + reseed
```

> macOS note: the system `make` needs `sudo xcodebuild -license accept` once.
> Raw equivalents live in each target if you prefer `cd backend && uv run ...`.

API: `POST /auth/login` (form) → bearer token. `GET /targets`,
`PATCH /targets/{id}` (scheduling/enabled), `POST /targets/{id}/toggle`,
`POST /targets/{id}/test`, subscriber endpoints, `POST /admin/sync-spots`.

## Status & plan

Backend and the spots architecture are done. Status is in `docs/ROADMAP.md`;
the detailed plan for the remaining phases (UI, polish, deploy) is in
`docs/PLAN.md`.
