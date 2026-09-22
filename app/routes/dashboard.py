from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User, Post, Comment, Like


router = APIRouter(
    prefix="/user",
    tags=["User Dashboard"]
)


@router.get("/dashboard")
def get_user_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # ============================================================
    # TOTAL POSTS CREATED BY CURRENT USER
    # ============================================================

    total_posts = db.query(Post).filter(
        Post.author_id == current_user.id
    ).count()


    # ============================================================
    # TOTAL COMMENTS MADE BY CURRENT USER
    # ============================================================

    total_comments = db.query(Comment).filter(
        Comment.user_id == current_user.id
    ).count()


    # ============================================================
    # TOTAL LIKES MADE BY CURRENT USER
    # ============================================================

    total_likes_made = db.query(Like).filter(
        Like.user_id == current_user.id
    ).count()


    # ============================================================
    # TOTAL LIKES RECEIVED ON CURRENT USER'S POSTS
    # ============================================================

    total_likes_received = db.query(Like).join(
        Post,
        Like.post_id == Post.id
    ).filter(
        Post.author_id == current_user.id
    ).count()


    # ============================================================
    # TOTAL VIEWS ON CURRENT USER'S POSTS
    # ============================================================

    user_posts = db.query(Post).filter(
        Post.author_id == current_user.id
    ).all()

    total_views = sum(
        post.views or 0
        for post in user_posts
    )


    # ============================================================
    # PER-POST STATISTICS
    # ============================================================

    post_statistics = []

    for post in user_posts:

        # Likes received on this post
        likes_count = db.query(Like).filter(
            Like.post_id == post.id
        ).count()


        # Comments received on this post
        comments_count = db.query(Comment).filter(
            Comment.post_id == post.id
        ).count()


        post_statistics.append({
            "post_id": post.id,
            "title": post.title,
            "likes": likes_count,
            "comments": comments_count,
            "views": post.views or 0
        })


    # ============================================================
    # DASHBOARD RESPONSE
    # ============================================================

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