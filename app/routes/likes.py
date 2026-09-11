from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Like, Post
from app.dependencies import get_current_user
from app.email_service import send_email


router = APIRouter(
    prefix="/likes",
    tags=["Likes"]
)


# Like a post
@router.post("/{post_id}")
def like_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    # Check if post exists
    post = db.query(Post).filter(Post.id == post_id).first()

    if not post:
        raise HTTPException(
            status_code=404,
            detail="Post not found"
        )

    # Check if user already liked the post
    existing_like = db.query(Like).filter(
        Like.post_id == post_id,
        Like.user_id == current_user.id
    ).first()

    if existing_like:
        raise HTTPException(
            status_code=400,
            detail="Post already liked"
        )

    # Create like
    like = Like(
        post_id=post_id,
        user_id=current_user.id
    )

    db.add(like)
    db.commit()
    db.refresh(like)

    # Send email notification to post owner
    send_email(
        to_email=post.author.email,
        subject="New Like on Your Post",
        body=(
            f"Hello {post.author.username},\n\n"
            f"User {current_user.username} liked your post "
            f"'{post.title}'.\n\n"
            f"Blog Management API"
        )
    )

    return {
        "message": "Post liked successfully"
    }


# Unlike a post
@router.delete("/{post_id}")
def unlike_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    # Check if post exists
    post = db.query(Post).filter(Post.id == post_id).first()

    if not post:
        raise HTTPException(
            status_code=404,
            detail="Post not found"
        )

    # Find user's like
    like = db.query(Like).filter(
        Like.post_id == post_id,
        Like.user_id == current_user.id
    ).first()

    if not like:
        raise HTTPException(
            status_code=400,
            detail="Post not liked yet"
        )

    # Remove like
    db.delete(like)
    db.commit()

    return {
        "message": "Post unliked successfully"
    }