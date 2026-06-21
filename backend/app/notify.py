import httpx
from sqlalchemy.orm import Session

from .config import settings
from .models import Subscription, Target, User


def _api(method: str) -> str | None:
    token = settings.telegram_bot_token
    return f"https://api.telegram.org/bot{token}/{method}" if token else None


def send_telegram(chat_id: str | None, text: str) -> bool:
    url = _api("sendMessage")
    if not url or not chat_id:
        print(f"[notify-fallback] {text}")
        return False
    try:
        r = httpx.post(url, json={"chat_id": chat_id, "text": text}, timeout=15)
        return r.status_code == 200
    except Exception as exc:  # noqa: BLE001
        print(f"[notify-error] {exc}")
        return False


def get_me() -> dict | None:
    """Bot identity from getMe, or None if no token / unreachable."""
    url = _api("getMe")
    if not url:
        return None
    try:
        r = httpx.get(url, timeout=10)
        if r.status_code == 200 and r.json().get("ok"):
            return r.json()["result"]
    except Exception:  # noqa: BLE001
        pass
    return None


def get_updates() -> list[dict]:
    """Recent chats that messaged the bot — for discovering chat ids."""
    url = _api("getUpdates")
    if not url:
        return []
    try:
        r = httpx.get(url, timeout=10)
        if r.status_code != 200 or not r.json().get("ok"):
            return []
        seen: dict[str, dict] = {}
        for update in r.json()["result"]:
            msg = update.get("message") or update.get("edited_message") or {}
            chat = msg.get("chat") or {}
            cid = chat.get("id")
            if cid is None:
                continue
            name = (
                chat.get("username")
                or " ".join(filter(None, [chat.get("first_name"), chat.get("last_name")]))
                or str(cid)
            )
            seen[str(cid)] = {"chat_id": str(cid), "name": name, "text": msg.get("text", "")}
        return list(seen.values())
    except Exception:  # noqa: BLE001
        return []


def notify_subscribers(db: Session, target: Target) -> int:
    text = f"🐕 SpotHound\n'{target.name}' is AVAILABLE!\n{target.url}"
    subs = db.query(Subscription).filter(Subscription.target_id == target.id).all()
    sent = 0
    for sub in subs:
        user = db.get(User, sub.user_id)
        chat_id = user.telegram_chat_id if user else None
        if send_telegram(chat_id, text):
            sent += 1
    return sent
