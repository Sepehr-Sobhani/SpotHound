# Remaining plan

Detailed, resumable plan for the phases after the backend. High-level status
lives in `ROADMAP.md`; architecture in `CLAUDE.md`.

## Phase 2 — React + Tailwind UI ✅ done

Implemented in `frontend/` (login, dashboard, target detail, admin). Telegram
onboarding and an events feed remain — moved to Phase 3.

Goal: a usable web UI for managing targets, backed by the existing API.

Tasks:
- Scaffold `frontend/` with Vite + React + TypeScript + Tailwind.
- Auth: login page hitting `POST /auth/login`; store the JWT; an axios/fetch
  client that attaches `Authorization: Bearer`; protected routes; logout.
- Targets dashboard: list each target with name, `spot_key`, `target_date`,
  `last_status` / `last_observed` / `last_checked_at`, and an enable toggle
  (`POST /targets/{id}/toggle`).
- Target panel (edit user-owned fields via `PATCH /targets/{id}`):
  - date picker for `target_date` (native `<input type="date">`);
  - `interval_seconds`; active window (`active_days`, `active_start`,
    `active_end`);
  - subscribers: list (`GET …/subscribers`), add/remove (self + admin variants);
  - **Test** button → `POST /targets/{id}/test`, show `met` / `observed` / error.
- Admin area: user management (`GET/POST /users`), spot catalog
  (`GET /admin/spots`), and a Sync button (`POST /admin/sync-spots`).
- Read-only display of the check logic (url/steps/condition) so users see what a
  target does without editing it.

Decisions / notes:
- Keep dependencies light: Tailwind + a small headless component lib only if
  needed. Native date input avoids a date-picker dependency.
- Dev: proxy API calls to `:8000`; prod: API base from an env var.

Done when: an admin can log in, set a target's date, schedule it, manage
subscribers, run a live test, and toggle it on — all from the browser.

## Phase 3 — Notifications & activity ✅ done

Done: Telegram onboarding (Settings page: set chat id, send test; bot status via
`getMe`; admin chat-id discovery via `getUpdates`) and the per-target activity
feed (`GET /targets/{id}/events` + Activity card).

Still optional / deferred:
- Active-window validation; re-notify cadence and quiet hours.
- A global activity feed across all targets.

## Phase 4 — Deploy (all free)

Tasks:
- Database: create a Neon Postgres project; set `DATABASE_URL`.
- Backend: build the Docker image (Chromium + xvfb already in `backend/Dockerfile`)
  and run it on an Oracle Cloud Always Free VM with env for `DATABASE_URL`,
  `JWT_SECRET`, `TELEGRAM_BOT_TOKEN`.
- HTTPS for the API: Caddy/nginx + Let's Encrypt, or a Cloudflare Tunnel (free).
- Frontend: deploy `frontend/` to Vercel; set the API base URL env; restrict
  backend CORS to the Vercel domain.

Done when: the app runs entirely off the user's machine, reachable over HTTPS,
checking targets and sending Telegram alerts.

## Cross-cutting backlog

- Alembic migrations (currently `Base.metadata.create_all`; needed once data is
  live and the schema changes).
- Tests (pytest): `render`/`has_unresolved`, `sync_spots`, API auth and the
  field-ownership guarantees.
- Calendar month navigation for far-future dates (the BC Parks date picker opens
  on the current month).
- Jitter / gentle intervals for bot-protected targets.
- Handle targets whose spot module was removed (orphans).
- Force-change the default admin password.

## Pending user actions

- Create a Telegram bot (@BotFather) → set `TELEGRAM_BOT_TOKEN` and recipient
  chat id(s).
- Decide when to create/push the public GitHub repo (currently local-only).
- macOS: `sudo xcodebuild -license accept` once to use `make`.
