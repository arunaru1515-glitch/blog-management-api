from datetime import datetime

from sqlalchemy.orm import Session

from app.models.notification import Notification
from app.services.email_service import send_email


# ============================================================
# CREATE IN-APP NOTIFICATION
# ============================================================

def create_notification(
    db: Session,
    user_id: int,
    message: str,
    notification_type: str
):
    notification = Notification(
        user_id=user_id,
        message=message,
        notification_type=notification_type,
        is_read=False,
        created_at=datetime.utcnow()
    )

    db.add(notification)
    db.commit()
    db.refresh(notification)

    return notification


# ============================================================
# COMMENT NOTIFICATION
# ============================================================

def send_comment_notification(
    post_title: str,
    commenter_name: str,
    comment_text: str,
    post_owner_email: str
):
    timestamp = datetime.now().strftime("%Y-%m-%d %I:%M %p")

    subject = "New Comment on Your Post"

    body = f"""
Hello,

You have received a new activity on your blog post.

Post Title: {post_title}
User: {commenter_name}
Activity: Comment
Timestamp: {timestamp}

Comment:
{comment_text}

Blog Management API
"""

    send_email(
        to_email=post_owner_email,
        subject=subject,
        body=body
    )


# ============================================================
# LIKE NOTIFICATION
# ============================================================

def send_like_notification(
    post_title: str,
    liker_name: str,
    post_owner_email: str
):
    timestamp = datetime.now().strftime("%Y-%m-%d %I:%M %p")

    subject = "New Like on Your Post"

    body = f"""
Hello,

You have received a new activity on your blog post.

Post Title: {post_title}
User: {liker_name}
Activity: Like
Timestamp: {timestamp}

Blog Management API
"""

    send_email(
        to_email=post_owner_email,
        subject=subject,
        body=body
    )