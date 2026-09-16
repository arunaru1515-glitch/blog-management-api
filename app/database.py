from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


# SQLite database
DATABASE_URL = r"sqlite:///C:\Users\HP\Desktop\Backend Accessment\Blog Management API using FastAPI\blog_management_api\blog.db"


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