from fastapi import APIRouter, Depends

from ..deps import get_current_user, require_admin
from ..models import User
from ..notify import get_me, get_updates
from ..schemas import ChatUpdate, TelegramStatus

router = APIRouter(prefix="/telegram", tags=["telegram"])


@router.get("/status", response_model=TelegramStatus)
def status(_: User = Depends(get_current_user)):
    me = get_me()
    return TelegramStatus(configured=me is not None, username=me.get("username") if me else None)


@router.get("/updates", response_model=list[ChatUpdate])
def updates(_: User = Depends(require_admin)):
    """Recent chats that messaged the bot, for discovering chat ids."""
    return get_updates()
