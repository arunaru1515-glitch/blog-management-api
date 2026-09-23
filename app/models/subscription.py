from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship

from app.database.database import Base


class SubscriptionPlan(Base):
    __tablename__ = "subscription_plans"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String,
        nullable=False,
        unique=True
    )

    price = Column(
        Float,
        nullable=False,
        default=0.0
    )

    # Feature limits
    max_posts = Column(
        Integer,
        nullable=True
    )

    max_images_per_post = Column(
        Integer,
        nullable=True
    )

    max_likes = Column(
        Integer,
        nullable=True
    )

    max_comments = Column(
        Integer,
        nullable=True
    )

    # Users subscribed to this plan
    users = relationship(
        "User",
        back_populates="subscription_plan"
    )

    # Billing records for this plan
    billing_history = relationship(
        "BillingHistory",
        back_populates="plan"
    )