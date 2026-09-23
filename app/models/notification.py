from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database.database import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # User who receives the notification
    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    # Notification message
    message = Column(
        String,
        nullable=False
    )

    # Type: like / comment / subscription
    notification_type = Column(
        String,
        nullable=False
    )

    # False = unread, True = read
    is_read = Column(
        Boolean,
        default=False,
        nullable=False
    )

    # Notification creation time
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # Relationship with User
    user = relationship(
        "User",
        back_populates="notifications"
    )