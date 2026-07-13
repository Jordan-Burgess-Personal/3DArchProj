from app.database.database import Base, engine

# Import models so SQLAlchemy registers their tables with Base.metadata.
from app.models import Component, Connection, Project  # noqa: F401


def create_database_tables() -> None:
    """Create database tables that do not already exist."""
    Base.metadata.create_all(bind=engine)