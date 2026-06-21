# Roadmap & status

What's done. Detailed plan for the remaining phases is in `PLAN.md`.

## Done

### Phase 1 — Backend engine & API ✅
- Single Playwright browser engine (`app/engine.py`) — steps + condition,
  anti-bot context, headful support. Verified against both reference spots.
- FastAPI + APScheduler (one job per enabled target) + Postgres.
- JWT auth, admin role, user/target/subscription/event models.
- Telegram notify on transition-to-available (console fallback if unconfigured).
- Live `POST /targets/{id}/test`.

### Phase 1.5 — Spots architecture & permission model ✅
- Each spot is its own module in `app/spots/`, auto-discovered by a registry.
- `sync_spots()` upserts spot definitions into targets; definition-owned fields
  (url/steps/condition/headless) are read-only, user-owned fields
  (enabled/schedule/subscribers) are never overwritten. New targets start
  disabled.
- API restricted: no create/delete of check logic via API; users only manage
  scheduling, on/off, and subscriptions. Admin can `POST /admin/sync-spots`.
- **Dates are parameters, not hardcoded** — spots use `{date:<strftime>}` tokens
  rendered per-target from `target_date`; one recipe covers any date.
- `docs/ADDING_A_SPOT.md` documents the repeatable "add a site" workflow.

### Phase 2 — React + Tailwind UI ✅
- Vite + React + TS + Tailwind in `frontend/`. JWT login, targets dashboard with
  status + on/off toggles, target detail (date picker, interval, active window,
  subscribers, live Test button, read-only check logic), and an admin area
  (user management, spot catalog, sync). `GET /targets/{id}` added to the API.

## Next

- Phase 3 — scheduling & notifications polish
- Phase 4 — deploy (Vercel + Neon + Oracle VM)

See `PLAN.md` for the detailed task breakdown.

## Pending user actions
- Create a Telegram bot via @BotFather → set `TELEGRAM_BOT_TOKEN` and the
  recipient chat id(s) so real alerts fire.
- Decide when to create/push the **public GitHub repo** (currently local-only).
- macOS: `sudo xcodebuild -license accept` once, to use `make`.

## Reference targets (live now, disabled by default)
- `bc_parks_alouette_pm` — BC Parks Alouette South Beach PM pass (easy site).
- `buntzen_lake_all_day` — Buntzen Lake all-day pass (headful; bot-protected).
