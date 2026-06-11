from database import Base, engine
import models  # noqa: F401 - imports SQLAlchemy models for metadata registration


def run_migrations() -> None:
    """Apply the current lightweight schema migration.

    The project does not use Alembic yet. This script is the explicit migration
    entrypoint used by Docker/Render and local development instead of creating
    tables inside the FastAPI import path.
    """
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    run_migrations()
    print("Database schema is up to date.")
