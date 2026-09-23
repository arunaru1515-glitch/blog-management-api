from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.notification import Notification


router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"]
)


# ============================================================
# GET USER NOTIFICATIONS
# ============================================================

@router.get("/")
def get_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    notifications = db.query(Notification).filter(
        Notification.user_id == current_user.id
    ).order_by(
        Notification.created_at.desc()
    ).all()

    return [
        {
            "id": notification.id,
            "message": notification.message,
            "notification_type": notification.notification_type,
            "is_read": notification.is_read,
            "created_at": notification.created_at
        }
        for notification in notifications
    ]


# ============================================================
# MARK ONE NOTIFICATION AS READ
# ============================================================

@router.put("/{notification_id}/read")
def mark_notification_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()

    if not notification:
        return {
            "message": "Notification not found"
        }

    notification.is_read = True

    db.commit()
    db.refresh(notification)

    return {
        "message": "Notification marked as read",
        "notification_id": notification.id,
        "is_read": notification.is_read
    }


# ============================================================
# MARK ALL NOTIFICATIONS AS READ
# ============================================================

@router.put("/read-all")
def mark_all_notifications_as_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    notifications = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).all()

    for notification in notifications:
        notification.is_read = True

    db.commit()

    return {
        "message": "All notifications marked as read",
        "updated_count": len(notifications)
    }