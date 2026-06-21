"""Admin-only operations."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import require_admin
from ..models import User
from ..spots import load_spots
from ..sync import sync_spots
from ..scheduler import reload_jobs

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/spots")
def list_spot_definitions(_: User = Depends(require_admin)):
    """The code-defined spot recipes available to sync."""
    return [
        {"key": s.key, "name": s.name, "url": s.url, "headless": s.headless}
        for s in load_spots().values()
    ]


@router.post("/sync-spots")
def trigger_sync(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    """Upsert spot definitions into targets after adding/editing a spot module."""
    result = sync_spots(db)
    reload_jobs()
    return result
