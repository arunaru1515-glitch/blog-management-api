from fastapi import FastAPI

from app.database import Base, engine
from app import models
from app.routes import auth, posts, comments, likes


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Blog Management API",
    description="Mini Blog Management System using FastAPI",
    version="1.0.0"
)


# Authentication routes
app.include_router(auth.router)

# Post routes
app.include_router(posts.router)

# Comment routes
app.include_router(comments.router)

# Like routes
app.include_router(likes.router)


@app.get("/")
def root():
    return {
        "message": "Blog Management API is running"
    }