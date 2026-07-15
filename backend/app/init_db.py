"""Create all database tables and seed initial data."""

from app.database import Base, engine
import app.models  # noqa: F401  # register all models
from app.seed.foods import main as seed_foods


def init_db():
    """Create all tables and seed initial food data."""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")

    print("Seeding food data...")
    seed_foods()
    print("Food data seeded successfully.")


if __name__ == "__main__":
    init_db()
