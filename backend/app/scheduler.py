"""Per-target polling: each enabled target is one APScheduler job.

Jobs run in background threads, so the synchronous Playwright engine is safe to
call directly without touching the FastAPI event loop.
"""
import datetime as dt

from apscheduler.schedulers.background import BackgroundScheduler

from .database import SessionLocal
from .engine import run_check
from .models import Event, Target
from .notify import notify_subscribers
from .spots.render import has_unresolved, render

scheduler = BackgroundScheduler()


def _within_window(target: Target, now: dt.datetime | None = None) -> bool:
    now = now or dt.datetime.now()
    if target.active_days is not None and now.weekday() not in target.active_days:
        return False
    if target.active_start and target.active_end:
        if not (target.active_start <= now.strftime("%H:%M") <= target.active_end):
            return False
    return True


def check_target(target_id: int) -> None:
    db = SessionLocal()
    try:
        target = db.get(Target, target_id)
        if not target or not target.enabled or not _within_window(target):
            return

        steps = render(target.steps, target.target_date)
        condition = render(target.condition, target.target_date)
        if has_unresolved(steps) or has_unresolved(condition):
            target.last_checked_at = dt.datetime.utcnow()
            target.last_status = "needs_date"
            target.last_observed = "target_date is not set"
            db.commit()
            print(f"[check] {target.name}: needs_date")
            return

        result = run_check(target.url, steps, condition, headless=target.headless)
        previous = target.last_status
        if result["error"]:
            status = "error"
        else:
            status = "met" if result["met"] else "not_met"

        target.last_checked_at = dt.datetime.utcnow()
        target.last_status = status
        target.last_observed = result.get("error") or result.get("observed")

        # notify only on the transition into "met" to avoid repeats
        notified = False
        if status == "met" and previous != "met":
            notify_subscribers(db, target)
            notified = True

        db.add(Event(target_id=target.id, status=status,
                     observed=target.last_observed, notified=notified))
        db.commit()
        print(f"[check] {target.name}: {status} ({target.last_observed})")
    except Exception as exc:  # noqa: BLE001
        print(f"[check-error] target {target_id}: {exc}")
    finally:
        db.close()


def reload_jobs() -> None:
    """Resync scheduler jobs with the enabled targets in the DB."""
    scheduler.remove_all_jobs()
    db = SessionLocal()
    try:
        for target in db.query(Target).filter(Target.enabled.is_(True)).all():
            scheduler.add_job(
                check_target,
                "interval",
                seconds=target.interval_seconds,
                args=[target.id],
                id=f"target-{target.id}",
                next_run_time=dt.datetime.now(),
                max_instances=1,
                coalesce=True,
            )
    finally:
        db.close()


def start_scheduler() -> None:
    if not scheduler.running:
        scheduler.start()
    reload_jobs()
