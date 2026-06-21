"""Target management: list, scheduling/enabled updates, test, and subscribers.

Targets come from code-defined spots (app/sync.py); this API only manages them,
it does not create check logic.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user, require_admin
from ..engine import run_check
from ..models import Subscription, Target, User
from ..schemas import CheckResult, SubscriberOut, TargetOut, TargetUpdate
from ..scheduler import reload_jobs
from ..spots.render import has_unresolved, render

router = APIRouter(prefix="/targets", tags=["targets"])


def _get_target(db: Session, target_id: int) -> Target:
    target = db.get(Target, target_id)
    if not target:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Target not found")
    return target


@router.get("", response_model=list[TargetOut])
def list_targets(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.query(Target).all()


@router.get("/{target_id}", response_model=TargetOut)
def get_target(
    target_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)
):
    return _get_target(db, target_id)


@router.patch("/{target_id}", response_model=TargetOut)
def update_target(
    target_id: int,
    payload: TargetUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Update user-owned fields only (scheduling + enabled)."""
    target = _get_target(db, target_id)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(target, key, value)
    db.commit()
    db.refresh(target)
    reload_jobs()
    return target


@router.post("/{target_id}/toggle", response_model=TargetOut)
def toggle_target(
    target_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)
):
    target = _get_target(db, target_id)
    target.enabled = not target.enabled
    db.commit()
    db.refresh(target)
    reload_jobs()
    return target


@router.post("/{target_id}/test", response_model=CheckResult)
async def test_target(
    target_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)
):
    """Run the check right now and return what it observed — the live 'Test' button."""
    target = _get_target(db, target_id)
    steps = render(target.steps, target.target_date)
    condition = render(target.condition, target.target_date)
    if has_unresolved(steps) or has_unresolved(condition):
        return CheckResult(met=False, error="target_date is not set")
    result = await run_in_threadpool(
        run_check, target.url, steps, condition, target.headless
    )
    return CheckResult(**result)


# --- subscriptions: who gets notified -------------------------------------

@router.get("/{target_id}/subscribers", response_model=list[SubscriberOut])
def list_subscribers(
    target_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)
):
    _get_target(db, target_id)
    subs = db.query(Subscription).filter(Subscription.target_id == target_id).all()
    out = []
    for sub in subs:
        user = db.get(User, sub.user_id)
        if user:
            out.append(SubscriberOut(user_id=user.id, username=user.username))
    return out


def _subscribe(db: Session, target_id: int, user_id: int) -> None:
    exists = (
        db.query(Subscription)
        .filter(Subscription.target_id == target_id, Subscription.user_id == user_id)
        .first()
    )
    if not exists:
        db.add(Subscription(target_id=target_id, user_id=user_id))
        db.commit()


@router.post("/{target_id}/subscribe", status_code=status.HTTP_204_NO_CONTENT)
def subscribe_self(
    target_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    _get_target(db, target_id)
    _subscribe(db, target_id, user.id)


@router.delete("/{target_id}/subscribe", status_code=status.HTTP_204_NO_CONTENT)
def unsubscribe_self(
    target_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    db.query(Subscription).filter(
        Subscription.target_id == target_id, Subscription.user_id == user.id
    ).delete()
    db.commit()


@router.post("/{target_id}/subscribers/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def subscribe_user(
    target_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    """Admin: subscribe another user to a target."""
    _get_target(db, target_id)
    if not db.get(User, user_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    _subscribe(db, target_id, user_id)


@router.delete("/{target_id}/subscribers/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def unsubscribe_user(
    target_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    """Admin: unsubscribe another user from a target."""
    db.query(Subscription).filter(
        Subscription.target_id == target_id, Subscription.user_id == user_id
    ).delete()
    db.commit()
