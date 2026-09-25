from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.core.dependencies import get_current_user

from app.models.user import User
from app.models.post import Post
from app.models.comment import Comment
from app.models.like import Like


# ============================================================
# DASHBOARD ROUTER
# ============================================================

router = APIRouter(
    prefix="/user",
    tags=["User Dashboard"]
)


# ============================================================
# USER DASHBOARD
# ============================================================

@router.get("/dashboard")
def get_user_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # ========================================================
    # TOTAL POSTS CREATED BY CURRENT USER
    # ========================================================

    total_posts = db.query(Post).filter(
        Post.author_id == current_user.id
    ).count()

    # ========================================================
    # TOTAL COMMENTS MADE BY CURRENT USER
    # ========================================================

    total_comments = db.query(Comment).filter(
        Comment.user_id == current_user.id
    ).count()

    # ========================================================
    # TOTAL LIKES MADE BY CURRENT USER
    # ========================================================

    total_likes_made = db.query(Like).filter(
        Like.user_id == current_user.id
    ).count()

    # ========================================================
    # TOTAL LIKES RECEIVED ON CURRENT USER'S POSTS
    # ========================================================

    total_likes_received = db.query(Like).join(
        Post,
        Like.post_id == Post.id
    ).filter(
        Post.author_id == current_user.id
    ).count()

    # ========================================================
    # GET CURRENT USER POSTS
    # ========================================================

    user_posts = db.query(Post).filter(
        Post.author_id == current_user.id
    ).all()

    # ========================================================
    # TOTAL VIEWS
    # ========================================================

    total_views = sum(
        post.views or 0
        for post in user_posts
    )

    # ========================================================
    # PER-POST STATISTICS
    # ========================================================

    post_statistics = []

    for post in user_posts:

        # ----------------------------------------------------
        # LIKES ON POST
        # ----------------------------------------------------

        likes_count = db.query(Like).filter(
            Like.post_id == post.id
        ).count()

        # ----------------------------------------------------
        # COMMENTS ON POST
        # ----------------------------------------------------

        comments_count = db.query(Comment).filter(
            Comment.post_id == post.id
        ).count()

        # ----------------------------------------------------
        # ADD POST STATISTICS
        # ----------------------------------------------------

        post_statistics.append({
            "post_id": post.id,
            "title": post.title,
            "likes": likes_count,
            "comments": comments_count,
            "views": post.views or 0
        })

    # ========================================================
    # RETURN DASHBOARD DATA
    # ========================================================

    return {
        "user_id": current_user.id,
        "username": current_user.username,

        "total_posts": total_posts,

        "total_comments": total_comments,

        "total_likes_made": total_likes_made,

        "total_likes_received": total_likes_received,

        "total_views": total_views,

        "posts": post_statistics
    }