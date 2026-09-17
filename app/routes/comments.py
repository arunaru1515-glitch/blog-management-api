from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Comment, Post
from app.schemas import CommentCreate, CommentResponse
from app.dependencies import get_current_user
from app.email_service import send_email


router = APIRouter(
    prefix="/comments",
    tags=["Comments"]
)


# ============================================================
# ADD A COMMENT TO A POST
# TASK 3 - SUBSCRIPTION COMMENT LIMIT
# ============================================================

@router.post("/{post_id}", response_model=CommentResponse)
def add_comment(
    post_id: int,
    comment_data: CommentCreate,
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
    # TASK 3 - CHECK ACTIVE SUBSCRIPTION
    # ========================================================

    plan = current_user.subscription_plan

    if not plan:
        raise HTTPException(
            status_code=403,
            detail="You do not have an active subscription plan."
        )

    # ========================================================
    # TASK 3 - CHECK COMMENT LIMIT
    # ========================================================

    existing_comments_count = db.query(Comment).filter(
        Comment.user_id == current_user.id
    ).count()

    if (
        plan.max_comments is not None
        and existing_comments_count >= plan.max_comments
    ):
        raise HTTPException(
            status_code=403,
            detail="You've reached your plan limit. Kindly upgrade your plan to continue."
        )

    # ========================================================
    # CREATE COMMENT
    # ========================================================

    comment = Comment(
        post_id=post_id,
        user_id=current_user.id,
        text=comment_data.text
    )

    db.add(comment)
    db.commit()
    db.refresh(comment)

    # ========================================================
    # SEND EMAIL NOTIFICATION IN BACKGROUND
    # ========================================================

    background_tasks.add_task(
        send_email,
        to_email=post.author.email,
        subject="New Comment on Your Post",
        body=(
            f"Hello {post.author.username},\n\n"
            f"User {current_user.username} commented on your post "
            f"'{post.title}'.\n\n"
            f"Comment: {comment_data.text}\n\n"
            f"Blog Management API"
        )
    )

    return comment


# ============================================================
# VIEW COMMENTS OF A POST
# ============================================================

@router.get(
    "/{post_id}",
    response_model=list[CommentResponse]
)
def get_comments(
    post_id: int,
    db: Session = Depends(get_db)
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
    # GET COMMENTS
    # ========================================================

    comments = db.query(Comment).filter(
        Comment.post_id == post_id
    ).all()

    return comments


# ============================================================
# DELETE OWN COMMENT
# ============================================================

@router.delete("/{comment_id}")
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    # ========================================================
    # FIND COMMENT
    # ========================================================

    comment = db.query(Comment).filter(
        Comment.id == comment_id
    ).first()

    if not comment:
        raise HTTPException(
            status_code=404,
            detail="Comment not found"
        )

    # ========================================================
    # CHECK COMMENT OWNERSHIP
    # ========================================================

    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only delete your own comments"
        )

    # ========================================================
    # DELETE COMMENT
    # ========================================================

    db.delete(comment)
    db.commit()

    return {
        "message": "Comment deleted successfully"
    }