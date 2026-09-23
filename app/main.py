from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.database.database import Base, engine

# ============================================================
# IMPORT ALL MODELS
# ============================================================

from app.models import (
    User,
    Post,
    Comment,
    Like,
    SubscriptionPlan,
    BillingHistory,
    Notification
)

# ============================================================
# IMPORT ALL ROUTES
# ============================================================

from app.routes import (
    auth,
    posts,
    comments,
    likes,
    subscriptions,
    dashboard,
    notifications
)


# ============================================================
# CREATE DATABASE TABLES
# ============================================================

Base.metadata.create_all(bind=engine)


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="Blog Management API",
    description="Mini Blog Management System using FastAPI",
    version="1.0.0"
)


# ============================================================
# SERVE UPLOADED MEDIA FILES
# ============================================================

app.mount(
    "/media",
    StaticFiles(directory="media"),
    name="media"
)


# ============================================================
# AUTHENTICATION ROUTES
# ============================================================

app.include_router(auth.router)


# ============================================================
# POST ROUTES
# ============================================================

app.include_router(posts.router)


# ============================================================
# COMMENT ROUTES
# ============================================================

app.include_router(comments.router)


# ============================================================
# LIKE ROUTES
# ============================================================

app.include_router(likes.router)


# ============================================================
# SUBSCRIPTION ROUTES
# ============================================================

app.include_router(subscriptions.router)


# ============================================================
# USER DASHBOARD API ROUTES
# ============================================================

app.include_router(dashboard.router)


# ============================================================
# NOTIFICATION ROUTES
# ============================================================

app.include_router(notifications.router)


# ============================================================
# DASHBOARD FRONTEND PAGE
# ============================================================

@app.get("/dashboard")
def dashboard_page():
    return FileResponse(
        "app/templates/dashboard.html"
    )


# ============================================================
# ROOT ENDPOINT
# ============================================================

@app.get("/")
def root():
    return {
        "message": "Blog Management API is running"
    }