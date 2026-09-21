from datetime import datetime
from app.email_service import send_email


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