from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


# Project root directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# SQLite database
DATABASE_PATH = BASE_DIR / "blog.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"


# Create database engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)


# Create session
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# Base model
Base = declarative_base()


# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()