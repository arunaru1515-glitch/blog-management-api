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


# Image upload folder
UPLOAD_DIR = "media/posts"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# Create a post with optional image
@router.post("/", response_model=PostResponse)
def create_post(
    title: str = Form(..., min_length=1, max_length=200),
    content: str = Form(..., min_length=1),
    image: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    image_path = None

    if image:
        allowed_extensions = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
        file_extension = os.path.splitext(image.filename)[1].lower()

        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only JPG, JPEG, PNG, GIF and WEBP images are allowed"
            )

        filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, filename)

        with open(file_path, "wb") as buffer:
            buffer.write(image.file.read())

        image_path = f"/media/posts/{filename}"

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


# View posts with pagination and search
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

    # Search by title or content
    if search:
        query = query.filter(
            (Post.title.ilike(f"%{search}%")) |
            (Post.content.ilike(f"%{search}%"))
        )

    # Get total matching posts
    total_count = query.count()

    # Calculate total pages
    total_pages = (total_count + limit - 1) // limit

    # Apply pagination
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


# View a single post
@router.get("/{post_id}", response_model=PostResponse)
def get_post(
    post_id: int,
    db: Session = Depends(get_db)
):
    post = db.query(Post).filter(Post.id == post_id).first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    return post


# Update own post with optional image
@router.put("/{post_id}", response_model=PostResponse)
def update_post(
    post_id: int,
    title: str = Form(..., min_length=1, max_length=200),
    content: str = Form(..., min_length=1),
    image: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    post = db.query(Post).filter(Post.id == post_id).first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    if post.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own posts"
        )

    post.title = title
    post.content = content

    if image:
        allowed_extensions = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
        file_extension = os.path.splitext(image.filename)[1].lower()

        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only JPG, JPEG, PNG, GIF and WEBP images are allowed"
            )

        filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, filename)

        with open(file_path, "wb") as buffer:
            buffer.write(image.file.read())

        post.image = f"/media/posts/{filename}"

    db.commit()
    db.refresh(post)

    return post


# Delete own post
@router.delete("/{post_id}")
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    post = db.query(Post).filter(Post.id == post_id).first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    if post.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own posts"
        )

    db.delete(post)
    db.commit()

    return {
        "message": "Post deleted successfully"
    }