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

    # Password is optional for Auth0 social-login users
    password = Column(
        String,
        nullable=True
    )

    # Authentication provider:
    # local / google / facebook
    provider = Column(
        String,
        nullable=False,
        default="local"
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

    # AI Support activity history
    ai_support_activities = relationship(
        "AISupportActivity",
        back_populates="user",
        cascade="all, delete-orphan"
    )