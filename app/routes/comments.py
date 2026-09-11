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


# Add a comment to a post
@router.post("/{post_id}", response_model=CommentResponse)
def add_comment(
    post_id: int,
    comment_data: CommentCreate,
    background_tasks: BackgroundTasks,
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

    # Create comment
    comment = Comment(
        post_id=post_id,
        user_id=current_user.id,
        text=comment_data.text
    )

    db.add(comment)
    db.commit()
    db.refresh(comment)

    # Send email notification in background
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


# View comments of a post
@router.get("/{post_id}", response_model=list[CommentResponse])
def get_comments(
    post_id: int,
    db: Session = Depends(get_db)
):
    # Check if post exists
    post = db.query(Post).filter(Post.id == post_id).first()

    if not post:
        raise HTTPException(
            status_code=404,
            detail="Post not found"
        )

    comments = db.query(Comment).filter(
        Comment.post_id == post_id
    ).all()

    return comments


# Delete own comment
@router.delete("/{comment_id}")
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    # Find comment
    comment = db.query(Comment).filter(
        Comment.id == comment_id
    ).first()

    if not comment:
        raise HTTPException(
            status_code=404,
            detail="Comment not found"
        )

    # Check comment ownership
    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only delete your own comments"
        )

    # Delete comment
    db.delete(comment)
    db.commit()

    return {
        "message": "Comment deleted successfully"
    }