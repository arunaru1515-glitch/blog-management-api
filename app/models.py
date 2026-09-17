from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)

    # Existing relationships
    posts = relationship("Post", back_populates="author")
    comments = relationship("Comment", back_populates="user")
    likes = relationship("Like", back_populates="user")

    # Task 3: Active subscription plan
    subscription_plan_id = Column(
        Integer,
        ForeignKey("subscription_plans.id"),
        nullable=True
    )

    subscription_plan = relationship(
        "SubscriptionPlan",
        back_populates="users"
    )

    billing_history = relationship(
        "BillingHistory",
        back_populates="user"
    )


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    image = Column(String, nullable=True)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    author = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post")
    likes = relationship("Like", back_populates="post")


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    post = relationship("Post", back_populates="comments")
    user = relationship("User", back_populates="comments")


class Like(Base):
    __tablename__ = "likes"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    post = relationship("Post", back_populates="likes")
    user = relationship("User", back_populates="likes")


# ============================================================
# TASK 3 - SUBSCRIPTION PLAN
# ============================================================

class SubscriptionPlan(Base):
    __tablename__ = "subscription_plans"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False, unique=True)
    price = Column(Float, nullable=False, default=0.0)

    # Feature limits
    max_posts = Column(Integer, nullable=True)
    max_images_per_post = Column(Integer, nullable=True)
    max_likes = Column(Integer, nullable=True)
    max_comments = Column(Integer, nullable=True)

    users = relationship(
        "User",
        back_populates="subscription_plan"
    )

    billing_history = relationship(
        "BillingHistory",
        back_populates="plan"
    )


# ============================================================
# TASK 3 - BILLING HISTORY
# ============================================================

class BillingHistory(Base):
    __tablename__ = "billing_history"

    id = Column(Integer, primary_key=True, index=True)

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

    user = relationship(
        "User",
        back_populates="billing_history"
    )

    plan = relationship(
        "SubscriptionPlan",
        back_populates="billing_history"
    )