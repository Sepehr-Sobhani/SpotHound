from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from ..engine import run_check
from ..models import Subscription, Target, User
from ..schemas import CheckResult, TargetCreate, TargetOut, TargetUpdate
from ..scheduler import reload_jobs

router = APIRouter(prefix="/targets", tags=["targets"])


@router.get("", response_model=list[TargetOut])
def list_targets(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.query(Target).all()


@router.post("", response_model=TargetOut, status_code=status.HTTP_201_CREATED)
def create_target(
    payload: TargetCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    target = Target(**payload.model_dump(), created_by=user.id)
    db.add(target)
    db.commit()
    db.refresh(target)
    # subscribe the creator by default
    db.add(Subscription(target_id=target.id, user_id=user.id))
    db.commit()
    reload_jobs()
    return target


@router.patch("/{target_id}", response_model=TargetOut)
def update_target(
    target_id: int,
    payload: TargetUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    target = db.get(Target, target_id)
    if not target:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Target not found")
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
    target = db.get(Target, target_id)
    if not target:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Target not found")
    target.enabled = not target.enabled
    db.commit()
    db.refresh(target)
    reload_jobs()
    return target


@router.delete("/{target_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_target(
    target_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)
):
    target = db.get(Target, target_id)
    if not target:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Target not found")
    db.delete(target)
    db.commit()
    reload_jobs()


@router.post("/{target_id}/test", response_model=CheckResult)
async def test_target(
    target_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)
):
    """Run the check right now and return what it observed — the live 'Test' button."""
    target = db.get(Target, target_id)
    if not target:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Target not found")
    result = await run_in_threadpool(
        run_check, target.url, target.steps, target.condition, target.headless
    )
    return CheckResult(**result)
