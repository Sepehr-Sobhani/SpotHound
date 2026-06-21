import datetime as dt

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(64), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(16), nullable=False, default="user")  # admin | user
    telegram_chat_id = Column(String(64), nullable=True)
    created_at = Column(DateTime, default=dt.datetime.utcnow)


class Target(Base):
    __tablename__ = "targets"

    id = Column(Integer, primary_key=True)

    # Links this row to its code-defined spot module (app/spots/<key>.py).
    spot_key = Column(String(64), unique=True, index=True, nullable=True)

    # --- definition-owned: synced from the spot module, read-only in the UI ---
    name = Column(String(200), nullable=False)
    url = Column(Text, nullable=False)
    steps = Column(JSON, nullable=False, default=list)
    condition = Column(JSON, nullable=False, default=dict)
    headless = Column(Boolean, nullable=False, default=True)

    # --- user-owned: editable in the UI, never overwritten by a spot sync ---
    interval_seconds = Column(Integer, nullable=False, default=300)

    # optional active window; null active_days = every day
    active_days = Column(JSON, nullable=True)        # list[int], 0=Mon .. 6=Sun
    active_start = Column(String(5), nullable=True)  # "07:00"
    active_end = Column(String(5), nullable=True)    # "21:00"

    enabled = Column(Boolean, nullable=False, default=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    last_checked_at = Column(DateTime, nullable=True)
    last_status = Column(String(16), nullable=True)  # met | not_met | error
    last_observed = Column(Text, nullable=True)
    created_at = Column(DateTime, default=dt.datetime.utcnow)

    subscriptions = relationship(
        "Subscription", back_populates="target", cascade="all, delete-orphan"
    )


class Subscription(Base):
    """Which users get notified for which target."""

    __tablename__ = "subscriptions"
    __table_args__ = (UniqueConstraint("target_id", "user_id", name="uq_target_user"),)

    id = Column(Integer, primary_key=True)
    target_id = Column(Integer, ForeignKey("targets.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    target = relationship("Target", back_populates="subscriptions")
    user = relationship("User")


class Event(Base):
    """History of checks — useful for debugging and an activity feed."""

    __tablename__ = "events"

    id = Column(Integer, primary_key=True)
    target_id = Column(Integer, ForeignKey("targets.id"), nullable=False)
    timestamp = Column(DateTime, default=dt.datetime.utcnow)
    status = Column(String(16), nullable=False)  # met | not_met | error
    observed = Column(Text, nullable=True)
    notified = Column(Boolean, default=False)
