import datetime as dt
from typing import Any

from pydantic import BaseModel, ConfigDict


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "user"
    telegram_chat_id: str | None = None


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    role: str
    telegram_chat_id: str | None = None


class TargetBase(BaseModel):
    name: str
    url: str
    steps: list[dict[str, Any]] = []
    condition: dict[str, Any] = {}
    interval_seconds: int = 300
    active_days: list[int] | None = None
    active_start: str | None = None
    active_end: str | None = None
    headless: bool = True
    enabled: bool = True


class TargetUpdate(BaseModel):
    """User-editable fields only. The check logic (url/steps/condition/headless)
    is defined in code (app/spots/) and is never editable through the API."""

    interval_seconds: int | None = None
    active_days: list[int] | None = None
    active_start: str | None = None
    active_end: str | None = None
    enabled: bool | None = None


class TargetOut(TargetBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    spot_key: str | None = None
    last_checked_at: dt.datetime | None = None
    last_status: str | None = None
    last_observed: str | None = None


class SubscriberOut(BaseModel):
    user_id: int
    username: str


class CheckResult(BaseModel):
    met: bool
    observed: str | None = None
    error: str | None = None
