"""Bootstrap: create the admin user, sync spots into targets, subscribe admin.

    uv run python -m app.seed
"""
from .config import settings
from .database import Base, SessionLocal, engine
from .models import Subscription, Target, User
from .security import hash_password
from .sync import sync_spots


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

        result = sync_spots(db)
        print(f"Synced spots: {result['created']} created, {result['updated']} updated")

        # subscribe admin to every target so notifications have a recipient
        for target in db.query(Target).all():
            exists = (
                db.query(Subscription)
                .filter(Subscription.target_id == target.id, Subscription.user_id == admin.id)
                .first()
            )
            if not exists:
                db.add(Subscription(target_id=target.id, user_id=admin.id))
        db.commit()
        print("Admin subscribed to all targets.")
        print("\nTargets are created DISABLED — turn them on via the UI/API when ready.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
