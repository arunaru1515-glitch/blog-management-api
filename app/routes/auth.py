import os
import secrets

from dotenv import load_dotenv

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    status,
)

from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm

from authlib.integrations.starlette_client import OAuth

from sqlalchemy.orm import Session

from .. import models, schemas

from app.database.database import get_db

from app.core.auth import (
    hash_password,
    verify_password,
    create_access_token,
)

# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)


# ============================================================
# AUTH0 CONFIGURATION
# ============================================================

AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")

AUTH0_CLIENT_ID = os.getenv("AUTH0_CLIENT_ID")

AUTH0_CLIENT_SECRET = os.getenv("AUTH0_CLIENT_SECRET")

AUTH0_CALLBACK_URL = os.getenv(
    "AUTH0_CALLBACK_URL",
    "http://localhost:8000/auth/callback"
)


# ============================================================
# GOOGLE / FACEBOOK CONNECTIONS
# ============================================================

GOOGLE_CONNECTION = os.getenv(
    "AUTH0_GOOGLE_CONNECTION",
    "google-oauth2"
)

FACEBOOK_CONNECTION = os.getenv(
    "AUTH0_FACEBOOK_CONNECTION",
    "facebook"
)


# ============================================================
# AUTHLIB OAUTH
# ============================================================

oauth = OAuth()

if (
    AUTH0_DOMAIN
    and AUTH0_CLIENT_ID
    and AUTH0_CLIENT_SECRET
):
    oauth.register(
        name="auth0",
        client_id=AUTH0_CLIENT_ID,
        client_secret=AUTH0_CLIENT_SECRET,
        server_metadata_url=(
            f"https://{AUTH0_DOMAIN}/"
            ".well-known/openid-configuration"
        ),
        client_kwargs={
            "scope": "openid profile email"
        },
    )


# ============================================================
# AUTH0 CONFIG CHECK
# ============================================================

def check_auth0_config():

    if not AUTH0_DOMAIN:
        raise HTTPException(
            status_code=500,
            detail="AUTH0_DOMAIN is missing"
        )

    if not AUTH0_CLIENT_ID:
        raise HTTPException(
            status_code=500,
            detail="AUTH0_CLIENT_ID is missing"
        )

    if not AUTH0_CLIENT_SECRET:
        raise HTTPException(
            status_code=500,
            detail="AUTH0_CLIENT_SECRET is missing"
        )

    if not AUTH0_CALLBACK_URL:
        raise HTTPException(
            status_code=500,
            detail="AUTH0_CALLBACK_URL is missing"
        )


# ============================================================
# REGISTER
# ============================================================

@router.post(
    "/register",
    response_model=schemas.UserOut,
    status_code=status.HTTP_201_CREATED
)
def register(
    user_in: schemas.UserCreate,
    db: Session = Depends(get_db)
):

    # --------------------------------------------------------
    # CHECK USERNAME
    # --------------------------------------------------------

    existing_username = (
        db.query(models.User)
        .filter(
            models.User.username == user_in.username
        )
        .first()
    )

    if existing_username:
        raise HTTPException(
            status_code=400,
            detail="Username already registered"
        )


    # --------------------------------------------------------
    # CHECK EMAIL
    # --------------------------------------------------------

    existing_email = (
        db.query(models.User)
        .filter(
            models.User.email == user_in.email
        )
        .first()
    )

    if existing_email:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )


    # --------------------------------------------------------
    # GET BASIC PLAN
    # --------------------------------------------------------

    basic_plan = (
        db.query(models.SubscriptionPlan)
        .filter(
            models.SubscriptionPlan.name == "Basic"
        )
        .first()
    )


    # --------------------------------------------------------
    # CREATE USER
    # IMPORTANT: User model uses "password"
    # --------------------------------------------------------

    new_user = models.User(
        username=user_in.username,
        email=user_in.email,

        password=hash_password(
            user_in.password
        ),

        plan_id=(
            basic_plan.id
            if basic_plan
            else None
        )
    )


    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# ============================================================
# LOGIN
# ============================================================

@router.post(
    "/login",
    response_model=schemas.Token
)
def login(
    request: Request,

    form_data: OAuth2PasswordRequestForm = Depends(),

    db: Session = Depends(get_db)
):

    # --------------------------------------------------------
    # GET USERNAME / EMAIL
    # --------------------------------------------------------

    login_value = form_data.username.strip()


    # --------------------------------------------------------
    # FIND USER BY USERNAME OR EMAIL
    # --------------------------------------------------------

    user = (
        db.query(models.User)
        .filter(
            (models.User.username == login_value)
            |
            (models.User.email == login_value)
        )
        .first()
    )


    # --------------------------------------------------------
    # USER NOT FOUND
    # --------------------------------------------------------

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email/username or password",
            headers={
                "WWW-Authenticate": "Bearer"
            }
        )


    # --------------------------------------------------------
    # VERIFY PASSWORD
    # IMPORTANT: User model uses "password"
    # --------------------------------------------------------

    if not verify_password(
        form_data.password,
        user.password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email/username or password",
            headers={
                "WWW-Authenticate": "Bearer"
            }
        )


    # --------------------------------------------------------
    # CREATE JWT
    # --------------------------------------------------------

    access_token = create_access_token(
        data={
            "sub": str(user.id)
        }
    )


    # --------------------------------------------------------
    # SAVE SESSION
    # --------------------------------------------------------

    request.session["access_token"] = access_token
    request.session["user_id"] = user.id


    # --------------------------------------------------------
    # RETURN TOKEN
    # --------------------------------------------------------

    return schemas.Token(
        access_token=access_token,
        token_type="bearer"
    )


# ============================================================
# GOOGLE LOGIN
# ============================================================

@router.get("/google")
async def google_login(
    request: Request
):

    check_auth0_config()

    return await oauth.auth0.authorize_redirect(
        request,
        AUTH0_CALLBACK_URL,
        connection=GOOGLE_CONNECTION
    )


# ============================================================
# FACEBOOK LOGIN
# ============================================================

@router.get("/facebook")
async def facebook_login(
    request: Request
):

    check_auth0_config()

    return await oauth.auth0.authorize_redirect(
        request,
        AUTH0_CALLBACK_URL,
        connection=FACEBOOK_CONNECTION
    )


# ============================================================
# AUTH0 CALLBACK
# ============================================================

@router.get("/callback")
async def auth0_callback(
    request: Request,
    db: Session = Depends(get_db)
):

    check_auth0_config()

    # --------------------------------------------------------
    # GET AUTH0 TOKEN
    # --------------------------------------------------------

    try:

        token = await oauth.auth0.authorize_access_token(
            request
        )

    except Exception as exc:

        print(
            "AUTH0 CALLBACK ERROR:",
            repr(exc)
        )

        raise HTTPException(
            status_code=400,
            detail=f"Auth0 login failed: {str(exc)}"
        )


    # --------------------------------------------------------
    # GET USER INFORMATION
    # --------------------------------------------------------

    userinfo = token.get("userinfo")


    # --------------------------------------------------------
    # IF USERINFO IS NOT IN TOKEN
    # --------------------------------------------------------

    if not userinfo:

        try:

            response = await oauth.auth0.get(
                "userinfo",
                token=token
            )

            userinfo = response.json()

        except Exception as exc:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Unable to retrieve Auth0 "
                    f"user information: {str(exc)}"
                )
            )


    # --------------------------------------------------------
    # GET AUTH0 USER DETAILS
    # --------------------------------------------------------

    auth0_id = userinfo.get("sub")
    email = userinfo.get("email")


    # --------------------------------------------------------
    # CHECK AUTH0 ID
    # --------------------------------------------------------

    if not auth0_id:

        raise HTTPException(
            status_code=400,
            detail="Auth0 user ID was not provided"
        )


    # --------------------------------------------------------
    # CHECK EMAIL
    # --------------------------------------------------------

    if not email:

        raise HTTPException(
            status_code=400,
            detail=(
                "Email was not provided by "
                "Google/Facebook"
            )
        )


    # --------------------------------------------------------
    # FIND USER USING AUTH0 ID
    # --------------------------------------------------------

    user = (
        db.query(models.User)
        .filter(
            models.User.auth0_id == auth0_id
        )
        .first()
    )


    # --------------------------------------------------------
    # IF NOT FOUND, FIND USING EMAIL
    # --------------------------------------------------------

    if not user:

        user = (
            db.query(models.User)
            .filter(
                models.User.email == email
            )
            .first()
        )


    # ========================================================
    # CREATE NEW AUTH0 USER
    # ========================================================

    if not user:

        username = (
            userinfo.get("nickname")
            or userinfo.get("name")
            or email.split("@")[0]
        )


        # Replace spaces
        username = username.replace(
            " ",
            "_"
        )


        base_username = username
        counter = 1


        # ----------------------------------------------------
        # MAKE USERNAME UNIQUE
        # ----------------------------------------------------

        while (
            db.query(models.User)
            .filter(
                models.User.username == username
            )
            .first()
        ):

            username = (
                f"{base_username}_{counter}"
            )

            counter += 1


        # ----------------------------------------------------
        # GET BASIC PLAN
        # ----------------------------------------------------

        basic_plan = (
            db.query(models.SubscriptionPlan)
            .filter(
                models.SubscriptionPlan.name == "Basic"
            )
            .first()
        )


        # ----------------------------------------------------
        # CREATE AUTH0 USER
        # IMPORTANT: User model uses "password"
        # ----------------------------------------------------

        user = models.User(
            username=username,
            email=email,

            password=hash_password(
                secrets.token_urlsafe(32)
            ),

            auth0_id=auth0_id,
            auth_provider="auth0",

            plan_id=(
                basic_plan.id
                if basic_plan
                else None
            )
        )

        db.add(user)


    # ========================================================
    # EXISTING USER
    # ========================================================

    else:

        user.auth0_id = auth0_id
        user.auth_provider = "auth0"


    # --------------------------------------------------------
    # SAVE USER
    # --------------------------------------------------------

    db.commit()
    db.refresh(user)


    # --------------------------------------------------------
    # CREATE APPLICATION JWT
    # --------------------------------------------------------

    access_token = create_access_token(
        data={
            "sub": str(user.id)
        }
    )


    # --------------------------------------------------------
    # SAVE SESSION
    # --------------------------------------------------------

    request.session["access_token"] = access_token
    request.session["user_id"] = user.id


    # --------------------------------------------------------
    # REDIRECT TO DASHBOARD
    # --------------------------------------------------------

    return RedirectResponse(
        url="/dashboard",
        status_code=302
    )


# ============================================================
# GET CURRENT SESSION
# ============================================================

@router.get("/session")
async def get_session(
    request: Request
):

    access_token = request.session.get(
        "access_token"
    )

    user_id = request.session.get(
        "user_id"
    )


    # --------------------------------------------------------
    # CHECK SESSION
    # --------------------------------------------------------

    if not access_token:

        raise HTTPException(
            status_code=401,
            detail="No active login session"
        )


    return {
        "authenticated": True,
        "access_token": access_token,
        "user_id": user_id
    }


# ============================================================
# LOGOUT
# ============================================================

@router.get("/logout")
async def logout(
    request: Request
):

    request.session.clear()

    return {
        "message": "Logged out successfully"
    }