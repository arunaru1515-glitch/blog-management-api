from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.auth import decode_access_token
from app.database.database import get_db
from app.models.user import User


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/password-login",
    auto_error=False
)


def get_current_user(
    request: Request,
    token: str | None = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    # ============================================================
    # 1. TRY TO GET TOKEN FROM AUTHORIZATION HEADER
    # ============================================================

    access_token = token

    # ============================================================
    # 2. IF NO HEADER TOKEN, GET TOKEN FROM SESSION
    # ============================================================

    if not access_token:
        access_token = request.session.get(
            "access_token"
        )

    # ============================================================
    # 3. CHECK TOKEN
    # ============================================================

    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={
                "WWW-Authenticate": "Bearer"
            }
        )

    # ============================================================
    # 4. DECODE TOKEN
    # ============================================================

    payload = decode_access_token(
        access_token
    )

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={
                "WWW-Authenticate": "Bearer"
            }
        )

    # ============================================================
    # 5. GET USER ID FROM TOKEN
    # ============================================================

    user_id = payload.get("sub")

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={
                "WWW-Authenticate": "Bearer"
            }
        )

    # ============================================================
    # 6. CONVERT USER ID
    # ============================================================

    try:
        user_id = int(user_id)

    except (TypeError, ValueError):

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in token",
            headers={
                "WWW-Authenticate": "Bearer"
            }
        )

    # ============================================================
    # 7. FIND USER IN DATABASE
    # ============================================================

    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={
                "WWW-Authenticate": "Bearer"
            }
        )

    # ============================================================
    # 8. RETURN CURRENT USER
    # ============================================================

    return user