from celery import Celery

from app.services.scheduler import publish_scheduled_posts


celery_app = Celery(
    "blog_management",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)


@celery_app.task(name="publish_scheduled_posts")
def scheduled_post_publisher():
    publish_scheduled_posts()


celery_app.conf.beat_schedule = {
    "publish-scheduled-posts-every-30-seconds": {
        "task": "publish_scheduled_posts",
        "schedule": 30.0,
    },
}