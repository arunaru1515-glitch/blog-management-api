from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse
from starlette.middleware.sessions import SessionMiddleware

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
    Notification,
    AISupportActivity
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
    notifications,
    ai_support
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
# SESSION MIDDLEWARE
# ============================================================

app.add_middleware(
    SessionMiddleware,
    secret_key="your-secret-key-change-this"
)


# ============================================================
# SERVE MEDIA FILES
# ============================================================

app.mount(
    "/media",
    StaticFiles(directory="media"),
    name="media"
)


# ============================================================
# SERVE STATIC FRONTEND FILES
# ============================================================

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)


# ============================================================
# AUTH ROUTES
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
# DASHBOARD API ROUTES
# ============================================================

app.include_router(dashboard.router)


# ============================================================
# NOTIFICATION ROUTES
# ============================================================

app.include_router(notifications.router)


# ============================================================
# AI SUPPORT ROUTES
# ============================================================

app.include_router(ai_support.router)


# ============================================================
# LOGIN FRONTEND PAGE
# ============================================================

@app.get("/login")
def login_page():

    return FileResponse(
        "static/login.html"
    )


# ============================================================
# DASHBOARD FRONTEND PAGE
# ============================================================

@app.get("/dashboard")
def dashboard_page():

    return FileResponse(
        "static/dashboard.html"
    )


# ============================================================
# AI SUPPORT FRONTEND PAGE
# ============================================================

@app.get("/ai-support")
def ai_support_page():

    return FileResponse(
        "static/ai_support/ai_support.html"
    )


# ============================================================
# ROOT ENDPOINT
# ============================================================

@app.get("/")
def root():

    return RedirectResponse(
        url="/login",
        status_code=302
    )