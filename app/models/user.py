from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.database.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    username = Column(
        String,
        nullable=False,
        unique=True
    )

    email = Column(
        String,
        nullable=False,
        unique=True
    )

    password = Column(
        String,
        nullable=False
    )

    # Posts created by the user
    posts = relationship(
        "Post",
        back_populates="author"
    )

    # Comments made by the user
    comments = relationship(
        "Comment",
        back_populates="user"
    )

    # Likes made by the user
    likes = relationship(
        "Like",
        back_populates="user"
    )

    # Active subscription
    subscription_plan_id = Column(
        Integer,
        ForeignKey("subscription_plans.id"),
        nullable=True
    )

    subscription_plan = relationship(
        "SubscriptionPlan",
        back_populates="users"
    )

    # Billing history
    billing_history = relationship(
        "BillingHistory",
        back_populates="user"
    )

    # Notifications received by the user
    notifications = relationship(
        "Notification",
        back_populates="user"
    )