import os
import uuid

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

from app.database import get_db
from app.models import Post, User
from app.schemas import PostResponse
from app.dependencies import get_current_user


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
# ============================================================

@router.post("/", response_model=PostResponse)
def create_post(
    title: str = Form(..., min_length=1, max_length=200),
    content: str = Form(..., min_length=1),
    image: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

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
            detail="You've reached your plan limit. Kindly upgrade your plan to continue."
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
                detail="Image uploads are not available on your current plan. Kindly upgrade your plan to continue."
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
                detail="Only JPG, JPEG, PNG, GIF and WEBP images are allowed"
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
    # CREATE POST
    # ========================================================

    new_post = Post(
        title=title,
        content=content,
        image=image_path,
        author_id=current_user.id
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
# ============================================================

@router.put("/{post_id}", response_model=PostResponse)
def update_post(
    post_id: int,
    title: str = Form(..., min_length=1, max_length=200),
    content: str = Form(..., min_length=1),
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
                detail="Image uploads are not available on your current plan. Kindly upgrade your plan to continue."
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
                detail="Only JPG, JPEG, PNG, GIF and WEBP images are allowed"
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