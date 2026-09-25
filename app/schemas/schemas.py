from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


# ============================================================
# USER / AUTH
# ============================================================

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    plan_id: int | None = None

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ============================================================
# SUBSCRIPTION
# ============================================================

class SubscriptionPlanOut(BaseModel):
    id: int
    name: str
    price: float
    post_limit: int
    image_limit: int
    like_limit: int
    comment_limit: int

    class Config:
        from_attributes = True


class SubscribeRequest(BaseModel):
    plan_name: str


class BillingHistoryOut(BaseModel):
    id: int
    plan_id: int
    price: float
    start_date: datetime
    end_date: datetime
    transaction_id: str
    invoice_pdf_path: str

    class Config:
        from_attributes = True


# ============================================================
# POST
# ============================================================

class PostCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)


class PostUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=200
    )

    content: str | None = Field(
        default=None,
        min_length=1
    )


class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    image: str | None = None
    author_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class PaginatedPostOut(BaseModel):
    posts: list[PostResponse]
    total_count: int
    total_pages: int
    current_page: int


# ============================================================
# COMMENT
# ============================================================

class CommentCreate(BaseModel):
    text: str = Field(..., min_length=1, max_length=1000)


class CommentResponse(BaseModel):
    id: int
    post_id: int
    user_id: int
    text: str
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================
# LIKE
# ============================================================

class LikeOut(BaseModel):
    liked: bool
    like_count: int
    message: str


# ============================================================
# DASHBOARD
# ============================================================

class DashboardPostStats(BaseModel):
    post_id: int
    post_title: str
    views: int
    likes_count: int
    comments_count: int


class DashboardDataOut(BaseModel):
    total_posts: int
    total_comments_made: int
    total_likes_received: int
    total_post_views: int
    post_stats: list[DashboardPostStats]


# ============================================================
# NOTIFICATIONS
# ============================================================

class NotificationOut(BaseModel):
    id: int
    user_id: int
    message: str
    notification_type: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================
# AI SUPPORT
# ============================================================

class AISupportRequest(BaseModel):
    message: str


class AISupportResponse(BaseModel):
    response: str