"""Create all database tables and seed initial data."""

from sqlalchemy import inspect, text
from app.database import Base, engine, SessionLocal
import app.models  # noqa: F401  # register all models
from app.models.user import User
from app.services.auth import hash_password
from app.seed.foods import main as seed_foods


def init_db():
    """Create all tables and seed initial food data."""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")

    # 1. Safety migration check for 'role' column in 'users' table
    try:
        inspector = inspect(engine)
        if "users" in inspector.get_table_names():
            columns = [col["name"] for col in inspector.get_columns("users")]
            if "role" not in columns:
                print("Adding 'role' column to 'users' table...")
                with engine.begin() as conn:
                    conn.execute(text("ALTER TABLE users ADD COLUMN role VARCHAR(20) NOT NULL DEFAULT 'user'"))
                print("'role' column added successfully.")
    except Exception as e:
        print(f"Error during schema update (users.role): {e}")

    # 1b. WeChat login migration: add openid column + relax NOT NULL on
    # username/email/password_hash so WeChat-only users can be created
    # with NULL values. MySQL allows multiple NULLs under UNIQUE, so this
    # does not conflict with existing accounts that carry real values.
    try:
        inspector = inspect(engine)
        if "users" in inspector.get_table_names():
            columns = [col["name"] for col in inspector.get_columns("users")]
            if "openid" not in columns:
                print("Adding 'openid' column to 'users' table...")
                with engine.begin() as conn:
                    conn.execute(text(
                        "ALTER TABLE users ADD COLUMN openid VARCHAR(64) NULL UNIQUE"
                    ))
                print("'openid' column added successfully.")
            # Relax NOT NULL on username/email/password_hash (idempotent)
            with engine.begin() as conn:
                conn.execute(text("ALTER TABLE users MODIFY username VARCHAR(50) NULL"))
                conn.execute(text("ALTER TABLE users MODIFY email VARCHAR(100) NULL"))
                conn.execute(text("ALTER TABLE users MODIFY password_hash VARCHAR(255) NULL"))
            print("Relaxed NOT NULL on username/email/password_hash for WeChat login.")
    except Exception as e:
        print(f"Error during WeChat schema migration: {e}")

    # 2. Seeding food data
    print("Seeding food data...")
    seed_foods()
    print("Food data seeded successfully.")

    # 3. Seed default admin 'yoyo' / 'yoyo'
    db = SessionLocal()
    try:
        yoyo = db.query(User).filter(User.username == "yoyo").first()
        if not yoyo:
            print("Creating default admin account 'yoyo'...")
            admin_user = User(
                username="yoyo",
                email="yoyo@yoyo.com",
                password_hash=hash_password("yoyo"),
                nickname="yoyo",
                role="admin",
                gender=1,
                height=175.0,
                age=25,
                target_weight=70.0,
                daily_calorie_goal=2000,
            )
            db.add(admin_user)
            db.commit()
            print("Default admin account 'yoyo' created.")
        else:
            # Ensure it is admin
            if yoyo.role != "admin":
                yoyo.role = "admin"
                db.commit()
                print("Updated existing user 'yoyo' role to 'admin'.")
    except Exception as e:
        db.rollback()
        print(f"Error seeding admin: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    init_db()

