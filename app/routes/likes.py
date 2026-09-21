from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Like, Post
from app.dependencies import get_current_user
from app.notification_service import send_like_notification


router = APIRouter(
    prefix="/likes",
    tags=["Likes"]
)


# ============================================================
# LIKE A POST
# ============================================================

@router.post("/{post_id}")
def like_post(
    post_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    # ========================================================
    # CHECK IF POST EXISTS
    # ========================================================

    post = db.query(Post).filter(
        Post.id == post_id
    ).first()

    if not post:
        raise HTTPException(
            status_code=404,
            detail="Post not found"
        )

    # ========================================================
    # CHECK ACTIVE SUBSCRIPTION
    # ========================================================

    plan = current_user.subscription_plan

    if not plan:
        raise HTTPException(
            status_code=403,
            detail="You do not have an active subscription plan."
        )

    # ========================================================
    # CHECK IF USER ALREADY LIKED THIS POST
    # ========================================================

    existing_like = db.query(Like).filter(
        Like.post_id == post_id,
        Like.user_id == current_user.id
    ).first()

    if existing_like:
        raise HTTPException(
            status_code=400,
            detail="Post already liked"
        )

    # ========================================================
    # CHECK LIKE LIMIT
    # ========================================================

    existing_likes_count = db.query(Like).filter(
        Like.user_id == current_user.id
    ).count()

    if (
        plan.max_likes is not None
        and existing_likes_count >= plan.max_likes
    ):
        raise HTTPException(
            status_code=403,
            detail="You've reached your plan limit. Kindly upgrade your plan to continue."
        )

    # ========================================================
    # CREATE LIKE
    # ========================================================

    like = Like(
        post_id=post_id,
        user_id=current_user.id
    )

    db.add(like)
    db.commit()
    db.refresh(like)

    # ========================================================
    # SEND LIKE NOTIFICATION IN BACKGROUND
    # ========================================================

    background_tasks.add_task(
        send_like_notification,
        post_title=post.title,
        liker_name=current_user.username,
        post_owner_email=post.author.email
    )

    return {
        "message": "Post liked successfully"
    }


# ============================================================
# UNLIKE A POST
# ============================================================

@router.delete("/{post_id}")
def unlike_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    # ========================================================
    # CHECK IF POST EXISTS
    # ========================================================

    post = db.query(Post).filter(
        Post.id == post_id
    ).first()

    if not post:
        raise HTTPException(
            status_code=404,
            detail="Post not found"
        )

    # ========================================================
    # FIND USER'S LIKE
    # ========================================================

    like = db.query(Like).filter(
        Like.post_id == post_id,
        Like.user_id == current_user.id
    ).first()

    if not like:
        raise HTTPException(
            status_code=400,
            detail="Post not liked yet"
        )

    # ========================================================
    # REMOVE LIKE
    # ========================================================

    db.delete(like)
    db.commit()

    return {
        "message": "Post unliked successfully"
    }