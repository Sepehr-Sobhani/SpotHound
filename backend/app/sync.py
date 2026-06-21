"""Sync code-defined spots into the database as targets.

Definition-owned fields (name, url, steps, condition, headless) are refreshed
from the spot module. User-owned fields (enabled, interval, schedule,
subscriptions) are never touched. New spots are created disabled so they don't
start polling until a user turns them on.

Run on startup and via the admin `POST /admin/sync-spots` endpoint.
"""
from sqlalchemy.orm import Session

from .models import Target
from .spots import load_spots


def sync_spots(db: Session) -> dict[str, int]:
    created = updated = 0
    for key, spot in load_spots().items():
        target = db.query(Target).filter(Target.spot_key == key).first()
        if target is None:
            db.add(
                Target(
                    spot_key=key,
                    name=spot.name,
                    url=spot.url,
                    steps=spot.steps,
                    condition=spot.condition,
                    headless=spot.headless,
                    interval_seconds=spot.default_interval_seconds,
                    enabled=False,  # user turns it on
                )
            )
            created += 1
        else:
            target.name = spot.name
            target.url = spot.url
            target.steps = spot.steps
            target.condition = spot.condition
            target.headless = spot.headless
            updated += 1
    db.commit()
    return {"created": created, "updated": updated}
