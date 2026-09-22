from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.database import Base, engine
from app import models
from app.routes import auth, posts, comments, likes, subscriptions, dashboard


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Blog Management API",
    description="Mini Blog Management System using FastAPI",
    version="1.0.0"
)


# Serve uploaded images
app.mount("/media", StaticFiles(directory="media"), name="media")


# Authentication routes
app.include_router(auth.router)

# Post routes
app.include_router(posts.router)

# Comment routes
app.include_router(comments.router)

# Like routes
app.include_router(likes.router)

# Subscription routes
app.include_router(subscriptions.router)

# User Dashboard API routes
app.include_router(dashboard.router)


# Dashboard frontend page
@app.get("/dashboard")
def dashboard_page():
    return FileResponse("app/templates/dashboard.html")


@app.get("/")
def root():
    return {
        "message": "Blog Management API is running"
    }