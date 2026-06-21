from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user, require_admin
from ..models import User
from ..notify import send_telegram
from ..schemas import MeUpdate, UserCreate, UserOut
from ..security import hash_password

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    return db.query(User).all()


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserCreate, db: Session = Depends(get_db), _: User = Depends(require_admin)
):
    if db.query(User).filter(User.username == payload.username).first():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Username already exists")
    user = User(
        username=payload.username,
        password_hash=hash_password(payload.password),
        role=payload.role,
        telegram_chat_id=payload.telegram_chat_id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user


@router.patch("/me", response_model=UserOut)
def update_me(
    payload: MeUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    user.telegram_chat_id = payload.telegram_chat_id or None
    db.commit()
    db.refresh(user)
    return user


@router.post("/me/telegram/test")
def test_my_telegram(user: User = Depends(get_current_user)):
    if not user.telegram_chat_id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Set your Telegram chat id first")
    if not send_telegram(user.telegram_chat_id, "🐕 SpotHound test — notifications are working!"):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "Could not send. Check the bot token and that you've messaged the bot.",
        )
    return {"sent": True}
