from datetime import datetime

from app.database.database import SessionLocal
from app.models.post import Post


def publish_scheduled_posts():
    db = SessionLocal()

    try:
        # Find scheduled posts whose scheduled time has arrived
        posts = db.query(Post).filter(
            Post.status == "Scheduled",
            Post.scheduled_at <= datetime.now()
        ).all()

        for post in posts:
            post.status = "Published"
            post.published_at = datetime.now()
            post.scheduled_at = None

        if posts:
            db.commit()

            print(
                f"Published {len(posts)} scheduled post(s) successfully."
            )

        else:
            print("No scheduled posts are ready to publish.")

    except Exception as e:
        db.rollback()
        print(f"Scheduled publishing error: {e}")

    finally:
        db.close()