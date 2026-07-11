from sqlalchemy.orm import Session

from app.database.database import SessionLocal


def get_db():
    """
    FastAPI dependency that provides a database session.

    Example:
        db: Session = Depends(get_db)
    """

    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()