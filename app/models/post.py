from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database.database import Base


class Post(Base):
    __tablename__ = "posts"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    title = Column(
        String,
        nullable=False
    )

    content = Column(
        Text,
        nullable=False
    )

    image = Column(
        String,
        nullable=True
    )

    # User Dashboard - Post Views
    views = Column(
        Integer,
        default=0,
        nullable=False
    )

    author_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    # Relationship with User
    author = relationship(
        "User",
        back_populates="posts"
    )

    # Relationship with Comments
    comments = relationship(
        "Comment",
        back_populates="post"
    )

    # Relationship with Likes
    likes = relationship(
        "Like",
        back_populates="post"
    )