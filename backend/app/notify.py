import httpx
from sqlalchemy.orm import Session

from .config import settings
from .models import Subscription, Target, User


def send_telegram(chat_id: str | None, text: str) -> bool:
    """Send one Telegram message. Falls back to logging if unconfigured."""
    token = settings.telegram_bot_token
    if not token or not chat_id:
        print(f"[notify-fallback] {text}")
        return False
    try:
        r = httpx.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": text},
            timeout=15,
        )
        return r.status_code == 200
    except Exception as exc:  # noqa: BLE001
        print(f"[notify-error] {exc}")
        return False


def notify_subscribers(db: Session, target: Target) -> int:
    """Ping every user subscribed to this target. Returns count sent."""
    text = f"🐕 SpotHound\n'{target.name}' is AVAILABLE!\n{target.url}"
    subs = db.query(Subscription).filter(Subscription.target_id == target.id).all()
    sent = 0
    for sub in subs:
        user = db.get(User, sub.user_id)
        chat_id = user.telegram_chat_id if user else None
        if send_telegram(chat_id, text):
            sent += 1
    return sent
