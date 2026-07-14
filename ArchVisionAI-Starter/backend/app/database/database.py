from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.database.config import DATABASE_URL

#SQLAlchemy Engine
engine = create_engine(
    DATABASE_URL,
    echo=True,
    future=True
    )

#Session Factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
    )

#Base class for models
class Base(DeclarativeBase):
    pass