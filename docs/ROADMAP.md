# Roadmap & status

Where SpotHound is and what's next. Keep this current.

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
- `docs/ADDING_A_SPOT.md` documents the repeatable "add a site" workflow.

## Next

### Phase 2 — React + Tailwind UI (current focus)
- Login screen (JWT).
- Targets dashboard: list with status, last-checked, on/off toggle.
- Per-target panel: scheduling (interval + active days/time), subscribers,
  and a live **Test** button hitting `/targets/{id}/test`.
- Admin: user management, "Sync spots" button, view of code-defined recipes.
- Deploy target: Vercel.

### Phase 3 — Scheduling & notifications polish
- Richer active-window editing; per-user Telegram onboarding (capture chat id).
- Notification history / activity feed from the `events` table.
- Optional: re-notify cadence, quiet hours.

### Phase 4 — Deploy (all free)
- Backend Docker image (Chromium + xvfb) on Oracle Cloud Always Free VM.
- Postgres on Neon. Frontend on Vercel. Lock CORS to the Vercel domain.

## Pending user actions
- Create a Telegram bot via @BotFather → set `TELEGRAM_BOT_TOKEN` and the
  recipient chat id(s) so real alerts fire.
- Decide when to create/push the **public GitHub repo** (currently local-only).
- macOS: `sudo xcodebuild -license accept` once, to use `make`.

## Reference targets (live now, disabled by default)
- `bc_parks_alouette_pm` — BC Parks Alouette South Beach PM pass (easy site).
- `buntzen_lake_all_day` — Buntzen Lake all-day pass (headful; bot-protected).
