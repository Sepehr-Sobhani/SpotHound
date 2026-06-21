"""Upsert code-defined spots into target rows.

Refreshes definition fields (name/url/steps/condition/headless) and leaves
user-managed fields untouched. New targets are created disabled.
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
                    enabled=False,
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
