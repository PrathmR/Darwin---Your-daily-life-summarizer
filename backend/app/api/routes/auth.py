# 2
# app/api/routes/auth.py
from datetime import datetime, timedelta
import logging

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Response,
    Request,
)
from sqlalchemy.orm import Session
import requests
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from app.api import deps
from app.core.config import settings
from app.schemas.user import (
    UserCreate,
    UserLogin,
    UserPublic,
    GoogleLoginRequest,
)
from app.models.user import User
from app.core.security import (
    hash_password,
    verify_password,
    generate_email_verification_token,
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    decode_access_token,
)
from app.email import send_verification_email

router = APIRouter(prefix="/auth", tags=["auth"])

logger = logging.getLogger("auth")
logging.basicConfig(level=logging.INFO)


# ---------- helpers ----------

def set_auth_cookies(response: Response, access_token: str, refresh_token: str):
    """
    Set httpOnly auth cookies. For local dev we use secure=False and samesite='lax'.
    In production (HTTPS) set secure=True and samesite='none' to allow cross-site cookies.
    """
    access_max_age = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    refresh_max_age = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60

    is_production = settings.ENVIRONMENT == "prod"

    cookie_params = {
        "httponly": True,
        "secure": is_production,
        "samesite": "lax" if not is_production else "none",
    }

    response.set_cookie(
        key="access_token",
        value=access_token,
        max_age=access_max_age,
        **cookie_params,
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        max_age=refresh_max_age,
        **cookie_params,
    )


def clear_auth_cookies(response: Response):
    """
    Clear httpOnly auth cookies. Must use same path and samesite settings as when setting.
    """
    is_production = settings.ENVIRONMENT == "prod"
    
    cookie_params = {
        "httponly": True,
        "secure": is_production,
        "samesite": "lax" if not is_production else "none",
        "path": "/",  # Ensure path matches
    }
    
    response.delete_cookie("access_token", **cookie_params)
    response.delete_cookie("refresh_token", **cookie_params)


# ---------- register & verify email ----------

@router.post("/register", response_model=dict)
def register_user(
    payload: UserCreate,
    db: Session = Depends(deps.get_db),
):
    try:
        email = payload.email.lower().strip()
        password = payload.password

        if len(password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 8 characters long.",
            )

        existing = db.query(User).filter(User.email == email).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email is already registered.",
            )

        # Hash password (Argon2 recommended)
        try:
            hashed = hash_password(password)
        except Exception as e:
            logger.exception("Error hashing password")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error",
            )

        user = User(
            email=email,
            password_hash=hashed,
            provider="local",
            is_email_verified=False,
        )

        token = generate_email_verification_token()
        user.email_verification_token = token
        user.email_verification_token_expires_at = datetime.utcnow() + timedelta(hours=1)

        db.add(user)
        db.commit()
        db.refresh(user)

        # Send verification email (best-effort)
        try:
            send_verification_email(to_email=user.email, token=token)
        except Exception:
            logger.exception("Failed sending verification email")

        return {
            "message": "Registered successfully. Please check your email to verify your account."
        }
    except HTTPException:
        raise
    except Exception:
        logger.exception("Register user failed")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/verify-email", response_model=dict)
def verify_email(
    token: str,
    db: Session = Depends(deps.get_db),
):
    if not token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Token is required."
        )

    user = (
        db.query(User)
        .filter(
            User.email_verification_token == token,
            User.email_verification_token_expires_at > datetime.utcnow(),
        )
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token.",
        )

    user.is_email_verified = True
    user.email_verification_token = None
    user.email_verification_token_expires_at = None

    db.add(user)
    db.commit()
    db.refresh(user)

    return {"message": "Email verified successfully. You can now sign in."}


# ---------- login / refresh / logout ----------

@router.post("/login", response_model=UserPublic)
def login(
    payload: UserLogin,
    response: Response,
    db: Session = Depends(deps.get_db),
):
    email = payload.email.lower().strip()
    password = payload.password

    user = db.query(User).filter(User.email == email).first()
    if not user or not user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    if not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    if not user.is_email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email is not verified.",
        )

    access_token = create_access_token(user_id=user.id)
    refresh_token = create_refresh_token(
        user_id=user.id, version=user.refresh_token_version
    )

    set_auth_cookies(response, access_token, refresh_token)

    return UserPublic(
        id=user.id, email=user.email, is_email_verified=user.is_email_verified, provider=user.provider
    )


@router.post("/refresh-token", response_model=dict)
def refresh_token(
    request: Request,
    response: Response,
    db: Session = Depends(deps.get_db),
):
    refresh_token_cookie = request.cookies.get("refresh_token")
    if not refresh_token_cookie:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="No refresh token."
        )

    payload = decode_refresh_token(refresh_token_cookie)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token."
        )

    user_id = int(payload.get("sub"))
    version = payload.get("v")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found."
        )

    if user.refresh_token_version != version:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has been revoked.",
        )

    new_access_token = create_access_token(user_id=user.id)
    new_refresh_token = create_refresh_token(
        user_id=user.id, version=user.refresh_token_version
    )

    set_auth_cookies(response, new_access_token, new_refresh_token)

    return {"message": "Token refreshed."}


@router.post("/logout", response_model=dict)
def logout(
    response: Response,
    db: Session = Depends(deps.get_db),
):
    # optional: bump refresh_token_version to invalidate all old tokens
    clear_auth_cookies(response)
    return {"message": "Logged out."}


# ---------- Google login ----------

@router.post("/google", response_model=UserPublic)
def google_login(
    payload: GoogleLoginRequest,
    response: Response,
    db: Session = Depends(deps.get_db),
):
    if not settings.GOOGLE_CLIENT_ID:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google client ID not configured.",
        )

    try:
        idinfo = id_token.verify_oauth2_token(
            payload.credential,
            google_requests.Request(),
            settings.GOOGLE_CLIENT_ID,
            clock_skew_in_seconds=10,
        )
    except Exception:
        logger.exception("Invalid Google token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Google token."
        )

    google_id = idinfo.get("sub")
    email = idinfo.get("email")

    if not email or not google_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google token missing required fields.",
        )

    email = email.lower().strip()

    user = db.query(User).filter(User.google_id == google_id).first()
    if not user:
        # maybe existing local account with same email -> link?
        user = db.query(User).filter(User.email == email).first()
        if user:
            user.google_id = google_id
            user.provider = "google"
            user.is_email_verified = True
        else:
            user = User(
                email=email,
                google_id=google_id,
                provider="google",
                is_email_verified=True,
            )
        db.add(user)
        db.commit()
        db.refresh(user)

    access_token = create_access_token(user_id=user.id)
    refresh_token = create_refresh_token(
        user_id=user.id, version=user.refresh_token_version
    )

    set_auth_cookies(response, access_token, refresh_token)

    return UserPublic(
        id=user.id, email=user.email, is_email_verified=user.is_email_verified, provider=user.provider
    )


@router.get("/me", response_model=UserPublic)
def get_me(current_user: User = Depends(deps.get_current_user)):
    """
    Return current user based on access_token cookie.
    """
    return UserPublic(
        id=current_user.id,
        email=current_user.email,
        is_email_verified=current_user.is_email_verified,
        provider=current_user.provider,
    )







# 1
# Anna code below
# # app/api/routes/auth.py

# from datetime import datetime, timedelta

# from fastapi import (
#     APIRouter,
#     Depends,
#     HTTPException,
#     status,
#     Response,
#     Request,
# )
# from sqlalchemy.orm import Session
# import requests
# from google.oauth2 import id_token
# from google.auth.transport import requests as google_requests

# from app.api import deps
# from app.core.config import settings
# from app.schemas.user import (
#     UserCreate,
#     UserLogin,
#     UserPublic,
#     GoogleLoginRequest,
# )
# from app.models.user import User
# from app.core.security import (
#     hash_password,
#     verify_password,
#     generate_email_verification_token,
#     create_access_token,
#     create_refresh_token,
#     decode_refresh_token,
#     decode_access_token,   # 👈 add this
# )
# from app.email import send_verification_email

# router = APIRouter(prefix="/auth", tags=["auth"])


# # ---------- helpers ----------


# def set_auth_cookies(response: Response, access_token: str, refresh_token: str):
#     # seconds
#     access_max_age = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
#     refresh_max_age = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60

#     cookie_params = {
#         "httponly": True,
#         "secure": False,  # set to True in production with HTTPS
#         "samesite": "lax",
#     }

#     response.set_cookie(
#         key="access_token",
#         value=access_token,
#         max_age=access_max_age,
#         **cookie_params,
#     )
#     response.set_cookie(
#         key="refresh_token",
#         value=refresh_token,
#         max_age=refresh_max_age,
#         **cookie_params,
#     )


# def clear_auth_cookies(response: Response):
#     response.delete_cookie("access_token")
#     response.delete_cookie("refresh_token")


# # ---------- register & verify email ----------


# @router.post("/register", response_model=dict)
# def register_user(
#     payload: UserCreate,
#     db: Session = Depends(deps.get_db),
# ):
#     email = payload.email.lower().strip()
#     password = payload.password

#     if len(password) < 8:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Password must be at least 8 characters long.",
#         )

#     existing = db.query(User).filter(User.email == email).first()
#     if existing:
#         raise HTTPException(
#             status_code=status.HTTP_409_CONFLICT,
#             detail="Email is already registered.",
#         )

#     user = User(
#         email=email,
#         password_hash=hash_password(password),
#         provider="local",
#         is_email_verified=False,
#     )

#     token = generate_email_verification_token()
#     user.email_verification_token = token
#     user.email_verification_token_expires_at = datetime.utcnow() + timedelta(hours=1)

#     db.add(user)
#     db.commit()
#     db.refresh(user)

#     send_verification_email(to_email=user.email, token=token)

#     return {
#         "message": "Registered successfully. Please check your email to verify your account."
#     }


# @router.get("/verify-email", response_model=dict)
# def verify_email(
#     token: str,
#     db: Session = Depends(deps.get_db),
# ):
#     if not token:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST, detail="Token is required."
#         )

#     user = (
#         db.query(User)
#         .filter(
#             User.email_verification_token == token,
#             User.email_verification_token_expires_at > datetime.utcnow(),
#         )
#         .first()
#     )

#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Invalid or expired verification token.",
#         )

#     user.is_email_verified = True
#     user.email_verification_token = None
#     user.email_verification_token_expires_at = None

#     db.add(user)
#     db.commit()
#     db.refresh(user)

#     return {"message": "Email verified successfully. You can now sign in."}


# # ---------- login / refresh / logout ----------


# @router.post("/login", response_model=UserPublic)
# def login(
#     payload: UserLogin,
#     response: Response,
#     db: Session = Depends(deps.get_db),
# ):
#     email = payload.email.lower().strip()
#     password = payload.password

#     user = db.query(User).filter(User.email == email).first()
#     if not user or not user.password_hash:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid email or password.",
#         )

#     if not verify_password(password, user.password_hash):
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid email or password.",
#         )

#     if not user.is_email_verified:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Email is not verified.",
#         )

#     access_token = create_access_token(user_id=user.id)
#     refresh_token = create_refresh_token(
#         user_id=user.id, version=user.refresh_token_version
#     )

#     set_auth_cookies(response, access_token, refresh_token)

#     return UserPublic(
#         id=user.id, email=user.email, is_email_verified=user.is_email_verified, provider=user.provider
#     )


# @router.post("/refresh-token", response_model=dict)
# def refresh_token(
#     request: Request,
#     response: Response,
#     db: Session = Depends(deps.get_db),
# ):
#     refresh_token_cookie = request.cookies.get("refresh_token")
#     if not refresh_token_cookie:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED, detail="No refresh token."
#         )

#     payload = decode_refresh_token(refresh_token_cookie)
#     if not payload:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token."
#         )

#     user_id = int(payload.get("sub"))
#     version = payload.get("v")

#     user = db.query(User).filter(User.id == user_id).first()
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found."
#         )

#     if user.refresh_token_version != version:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Refresh token has been revoked.",
#         )

#     new_access_token = create_access_token(user_id=user.id)
#     new_refresh_token = create_refresh_token(
#         user_id=user.id, version=user.refresh_token_version
#     )

#     set_auth_cookies(response, new_access_token, new_refresh_token)

#     return {"message": "Token refreshed."}


# @router.post("/logout", response_model=dict)
# def logout(
#     response: Response,
#     db: Session = Depends(deps.get_db),
# ):
#     # optional: bump refresh_token_version to invalidate all old tokens
#     clear_auth_cookies(response)
#     return {"message": "Logged out."}


# # ---------- Google login ----------


# @router.post("/google", response_model=UserPublic)
# def google_login(
#     payload: GoogleLoginRequest,
#     response: Response,
#     db: Session = Depends(deps.get_db),
# ):
#     if not settings.GOOGLE_CLIENT_ID:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Google client ID not configured.",
#         )

#     try:
#         idinfo = id_token.verify_oauth2_token(
#             payload.credential,
#             google_requests.Request(),
#             settings.GOOGLE_CLIENT_ID,
#         )
#     except Exception:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Google token."
#         )

#     google_id = idinfo.get("sub")
#     email = idinfo.get("email")

#     if not email or not google_id:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Google token missing required fields.",
#         )

#     email = email.lower().strip()

#     user = db.query(User).filter(User.google_id == google_id).first()
#     if not user:
#         # maybe existing local account with same email -> link?
#         user = db.query(User).filter(User.email == email).first()
#         if user:
#             user.google_id = google_id
#             user.provider = "google"
#             user.is_email_verified = True
#         else:
#             user = User(
#                 email=email,
#                 google_id=google_id,
#                 provider="google",
#                 is_email_verified=True,
#             )
#         db.add(user)
#         db.commit()
#         db.refresh(user)

#     access_token = create_access_token(user_id=user.id)
#     refresh_token = create_refresh_token(
#         user_id=user.id, version=user.refresh_token_version
#     )

#     set_auth_cookies(response, access_token, refresh_token)

#     return UserPublic(
#         id=user.id, email=user.email, is_email_verified=user.is_email_verified, provider=user.provider
#     )

# @router.get("/me", response_model=UserPublic)
# def get_me(
#     request: Request,
#     db: Session = Depends(deps.get_db),
# ):
#     """
#     Return current user based on access_token cookie.
#     """
#     token = request.cookies.get("access_token")
#     if not token:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Not authenticated.",
#         )

#     payload = decode_access_token(token)
#     if not payload:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid or expired access token.",
#         )

#     user_id = int(payload.get("sub", 0) or 0)

#     user = db.query(User).filter(User.id == user_id).first()
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="User not found.",
#         )

#     return UserPublic(
#         id=user.id,
#         email=user.email,
#         is_email_verified=user.is_email_verified,
#         provider=user.provider,
#     )

