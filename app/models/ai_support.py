from datetime import datetime

from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database.database import Base


class AISupportActivity(Base):
    __tablename__ = "ai_support_activities"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    question = Column(
        Text,
        nullable=False
    )

    ai_response = Column(
        Text,
        nullable=False
    )

    timestamp = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    user = relationship(
        "User",
        back_populates="ai_support_activities"
    )