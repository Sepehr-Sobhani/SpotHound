"""Create the admin user and the two reference targets.

    uv run python -m app.seed
"""
from .config import settings
from .database import Base, SessionLocal, engine
from .models import Subscription, Target, User
from .security import hash_password
from .targets_data import REFERENCE_TARGETS


def main() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.username == settings.admin_username).first()
        if not admin:
            admin = User(
                username=settings.admin_username,
                password_hash=hash_password(settings.admin_password),
                role="admin",
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)
            print(f"Created admin user '{settings.admin_username}'")
        else:
            print(f"Admin '{settings.admin_username}' already exists")

        for t in REFERENCE_TARGETS:
            if db.query(Target).filter(Target.name == t["name"]).first():
                print(f"Target exists: {t['name']}")
                continue
            target = Target(
                name=t["name"],
                url=t["url"],
                steps=t["steps"],
                condition=t["condition"],
                interval_seconds=t["interval_seconds"],
                headless=t.get("headless", True),
                created_by=admin.id,
            )
            db.add(target)
            db.commit()
            db.refresh(target)
            db.add(Subscription(target_id=target.id, user_id=admin.id))
            db.commit()
            print(f"Created target: {t['name']}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
