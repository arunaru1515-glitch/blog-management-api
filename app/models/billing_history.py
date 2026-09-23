from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database.database import Base


class BillingHistory(Base):
    __tablename__ = "billing_history"

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

    plan_id = Column(
        Integer,
        ForeignKey("subscription_plans.id"),
        nullable=False
    )

    start_date = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    end_date = Column(
        DateTime,
        nullable=True
    )

    transaction_id = Column(
        String,
        nullable=False,
        unique=True
    )

    invoice_path = Column(
        String,
        nullable=True
    )

    # Relationship with User
    user = relationship(
        "User",
        back_populates="billing_history"
    )

    # Relationship with SubscriptionPlan
    plan = relationship(
        "SubscriptionPlan",
        back_populates="billing_history"
    )