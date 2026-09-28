import os
import uuid
from datetime import datetime

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    UploadFile,
    File,
    Form,
)
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.post import Post
from app.models.user import User
from app.schemas.schemas import PostResponse
from app.core.dependencies import get_current_user


router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)


# ============================================================
# IMAGE UPLOAD FOLDER
# ============================================================

UPLOAD_DIR = "media/posts"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ============================================================
# CREATE POST
# TASK 1/2 + TASK 3 SUBSCRIPTION ACCESS CONTROL
# + SCHEDULED BLOG PUBLISHING
# ============================================================

@router.post("/", response_model=PostResponse)
def create_post(
    title: str = Form(..., min_length=1, max_length=200),
    content: str = Form(..., min_length=1),

    # Publishing option:
    # publish = Publish Now
    # draft = Save as Draft
    # schedule = Schedule Post
    publish_option: str = Form("publish"),

    # Required when publish_option = schedule
    scheduled_at: str | None = Form(None),

    image: UploadFile | None = File(None),

    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # ========================================================
    # VALIDATE PUBLISH OPTION
    # ========================================================

    allowed_publish_options = {
        "publish",
        "draft",
        "schedule"
    }

    if publish_option not in allowed_publish_options:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Invalid publish option. "
                "Use 'publish', 'draft' or 'schedule'."
            )
        )

    # ========================================================
    # PARSE SCHEDULED DATE
    # ========================================================

    scheduled_datetime = None

    if scheduled_at:

        try:
            scheduled_datetime = datetime.fromisoformat(
                scheduled_at
            )
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Invalid scheduled_at format. "
                    "Use YYYY-MM-DDTHH:MM:SS."
                )
            )

    # ========================================================
    # PUBLISHING VALIDATION
    # ========================================================

    # --------------------------------------------------------
    # DRAFT
    # --------------------------------------------------------

    if publish_option == "draft":

        if scheduled_datetime is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Draft posts cannot have a scheduled date."
                )
            )

    # --------------------------------------------------------
    # SCHEDULE
    # --------------------------------------------------------

    if publish_option == "schedule":

        if scheduled_datetime is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "scheduled_at is required when scheduling a post."
                )
            )

        if scheduled_datetime <= datetime.now():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Scheduled time must be in the future."
                )
            )

    # --------------------------------------------------------
    # PUBLISH NOW
    # --------------------------------------------------------

    if publish_option == "publish":

        if scheduled_datetime is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Publish Now cannot have a scheduled date."
                )
            )

    # ========================================================
    # TASK 3 - CHECK ACTIVE SUBSCRIPTION
    # ========================================================

    plan = current_user.subscription_plan

    if not plan:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have an active subscription plan."
        )

    # ========================================================
    # TASK 3 - CHECK MAXIMUM POSTS LIMIT
    # ========================================================

    existing_posts_count = db.query(Post).filter(
        Post.author_id == current_user.id
    ).count()

    if (
        plan.max_posts is not None
        and existing_posts_count >= plan.max_posts
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You've reached your plan limit. "
                "Kindly upgrade your plan to continue."
            )
        )

    # ========================================================
    # TASK 3 - CHECK IMAGE LIMIT
    # ========================================================

    image_path = None

    if image:

        if (
            plan.max_images_per_post is not None
            and plan.max_images_per_post < 1
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "Image uploads are not available on your "
                    "current plan. Kindly upgrade your plan "
                    "to continue."
                )
            )

        # Allowed image formats
        allowed_extensions = {
            ".jpg",
            ".jpeg",
            ".png",
            ".gif",
            ".webp"
        }

        file_extension = os.path.splitext(
            image.filename
        )[1].lower()

        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Only JPG, JPEG, PNG, GIF and WEBP "
                    "images are allowed"
                )
            )

        # Generate unique filename
        filename = f"{uuid.uuid4()}{file_extension}"

        file_path = os.path.join(
            UPLOAD_DIR,
            filename
        )

        # Save image
        with open(file_path, "wb") as buffer:
            buffer.write(image.file.read())

        image_path = f"/media/posts/{filename}"

    # ========================================================
    # DETERMINE POST STATUS
    # ========================================================

    if publish_option == "draft":

        post_status = "Draft"
        published_datetime = None
        scheduled_datetime = None

    elif publish_option == "schedule":

        post_status = "Scheduled"
        published_datetime = None

    else:

        post_status = "Published"
        published_datetime = datetime.now()
        scheduled_datetime = None

    # ========================================================
    # CREATE POST
    # ========================================================

    new_post = Post(
        title=title,
        content=content,
        image=image_path,
        author_id=current_user.id,
        status=post_status,
        scheduled_at=scheduled_datetime,
        published_at=published_datetime
    )

    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post


# ============================================================
# GET POSTS
# SEARCH + PAGINATION
# ============================================================

@router.get("/")
def get_posts(
    page: int = 1,
    limit: int = 10,
    search: str | None = None,
    db: Session = Depends(get_db)
):

    # Validate page
    if page < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Page must be greater than or equal to 1"
        )

    # Validate limit
    if limit < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Limit must be greater than or equal to 1"
        )

    # Base query
    query = db.query(Post)

    # ========================================================
    # SEARCH BY TITLE OR CONTENT
    # ========================================================

    if search:
        query = query.filter(
            (Post.title.ilike(f"%{search}%")) |
            (Post.content.ilike(f"%{search}%"))
        )

    # ========================================================
    # TOTAL MATCHING POSTS
    # ========================================================

    total_count = query.count()

    # ========================================================
    # TOTAL PAGES
    # ========================================================

    total_pages = (
        (total_count + limit - 1) // limit
    )

    # ========================================================
    # PAGINATION
    # ========================================================

    posts = query.offset(
        (page - 1) * limit
    ).limit(limit).all()

    return {
        "posts": posts,
        "total_count": total_count,
        "total_pages": total_pages,
        "page": page,
        "limit": limit
    }


# ============================================================
# GET SINGLE POST
# OPTIONAL FEATURE - POST VIEW TRACKING
# ============================================================

@router.get("/{post_id}", response_model=PostResponse)
def get_post(
    post_id: int,
    db: Session = Depends(get_db)
):

    post = db.query(Post).filter(
        Post.id == post_id
    ).first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    # ========================================================
    # OPTIONAL - INCREMENT POST VIEW COUNT
    # ========================================================

    post.views += 1

    db.commit()
    db.refresh(post)

    return post


# ============================================================
# UPDATE OWN POST
# + SCHEDULED BLOG PUBLISHING
# ============================================================

@router.put("/{post_id}", response_model=PostResponse)
def update_post(
    post_id: int,

    title: str = Form(..., min_length=1, max_length=200),
    content: str = Form(..., min_length=1),

    # Publishing option during update
    publish_option: str | None = Form(None),

    # Schedule date/time during update
    scheduled_at: str | None = Form(None),

    image: UploadFile | None = File(None),

    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # ========================================================
    # FIND POST
    # ========================================================

    post = db.query(Post).filter(
        Post.id == post_id
    ).first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    # ========================================================
    # CHECK POST OWNER
    # ========================================================

    if post.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own posts"
        )

    # ========================================================
    # UPDATE TEXT
    # ========================================================

    post.title = title
    post.content = content

    # ========================================================
    # HANDLE PUBLISHING OPTION
    # ========================================================

    if publish_option is not None:

        allowed_publish_options = {
            "publish",
            "draft",
            "schedule"
        }

        if publish_option not in allowed_publish_options:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Invalid publish option. "
                    "Use 'publish', 'draft' or 'schedule'."
                )
            )

        # ----------------------------------------------------
        # PARSE SCHEDULED DATE
        # ----------------------------------------------------

        scheduled_datetime = None

        if scheduled_at:

            try:
                scheduled_datetime = datetime.fromisoformat(
                    scheduled_at
                )
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        "Invalid scheduled_at format. "
                        "Use YYYY-MM-DDTHH:MM:SS."
                    )
                )

        # ----------------------------------------------------
        # DRAFT
        # ----------------------------------------------------

        if publish_option == "draft":

            if scheduled_datetime is not None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        "Draft posts cannot have a scheduled date."
                    )
                )

            post.status = "Draft"
            post.scheduled_at = None
            post.published_at = None

        # ----------------------------------------------------
        # SCHEDULE
        # ----------------------------------------------------

        elif publish_option == "schedule":

            if scheduled_datetime is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        "scheduled_at is required when "
                        "scheduling a post."
                    )
                )

            if scheduled_datetime <= datetime.now():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        "Scheduled time must be in the future."
                    )
                )

            post.status = "Scheduled"
            post.scheduled_at = scheduled_datetime
            post.published_at = None

        # ----------------------------------------------------
        # PUBLISH NOW
        # ----------------------------------------------------

        elif publish_option == "publish":

            if scheduled_datetime is not None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        "Publish Now cannot have a scheduled date."
                    )
                )

            post.status = "Published"
            post.scheduled_at = None
            post.published_at = datetime.now()

    # ========================================================
    # UPDATE IMAGE
    # ========================================================

    if image:

        plan = current_user.subscription_plan

        if not plan:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have an active subscription plan."
            )

        if (
            plan.max_images_per_post is not None
            and plan.max_images_per_post < 1
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "Image uploads are not available on your "
                    "current plan. Kindly upgrade your plan "
                    "to continue."
                )
            )

        # Allowed image formats
        allowed_extensions = {
            ".jpg",
            ".jpeg",
            ".png",
            ".gif",
            ".webp"
        }

        file_extension = os.path.splitext(
            image.filename
        )[1].lower()

        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Only JPG, JPEG, PNG, GIF and WEBP "
                    "images are allowed"
                )
            )

        # Generate unique filename
        filename = f"{uuid.uuid4()}{file_extension}"

        file_path = os.path.join(
            UPLOAD_DIR,
            filename
        )

        # Save image
        with open(file_path, "wb") as buffer:
            buffer.write(image.file.read())

        post.image = f"/media/posts/{filename}"

    # ========================================================
    # SAVE CHANGES
    # ========================================================

    db.commit()
    db.refresh(post)

    return post


# ============================================================
# DELETE OWN POST
# ============================================================

@router.delete("/{post_id}")
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # ========================================================
    # FIND POST
    # ========================================================

    post = db.query(Post).filter(
        Post.id == post_id
    ).first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    # ========================================================
    # CHECK POST OWNER
    # ========================================================

    if post.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own posts"
        )

    # ========================================================
    # DELETE POST
    # ========================================================

    db.delete(post)
    db.commit()

    return {
        "message": "Post deleted successfully"
    }