# 2
# app/core/security.py
from datetime import datetime, timedelta
from typing import Optional
import secrets

from jose import jwt, JWTError
from passlib.context import CryptContext

from app.core.config import settings

# Use Argon2 for password hashing (stronger and avoids bcrypt 72-byte limit)
pwd_context = CryptContext(
    schemes=["argon2"],  # argon2 is recommended for new projects
    deprecated="auto",
)

ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    if password is None:
        password = ""
    return pwd_context.hash(str(password))


def verify_password(plain_password: str, password_hash: str) -> bool:
    return pwd_context.verify(str(plain_password), password_hash)


def create_access_token(user_id: int) -> str:
    expire = datetime.utcnow() + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode = {
        "sub": str(user_id),
        "type": "access",
        "exp": expire,
    }
    return jwt.encode(to_encode, settings.JWT_ACCESS_SECRET, algorithm=ALGORITHM)


def create_refresh_token(user_id: int, version: int) -> str:
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {
        "sub": str(user_id),
        "type": "refresh",
        "v": version,
        "exp": expire,
    }
    return jwt.encode(to_encode, settings.JWT_REFRESH_SECRET, algorithm=ALGORITHM)


def decode_access_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.JWT_ACCESS_SECRET, algorithms=[ALGORITHM])
        if payload.get("type") != "access":
            return None
        return payload
    except JWTError:
        return None


def decode_refresh_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(
            token, settings.JWT_REFRESH_SECRET, algorithms=[ALGORITHM]
        )
        if payload.get("type") != "refresh":
            return None
        return payload
    except JWTError:
        return None


def generate_email_verification_token() -> str:
    return secrets.token_urlsafe(32)




# 1
# # app/core/security.py

# from datetime import datetime, timedelta
# from typing import Optional
# import secrets

# from jose import jwt, JWTError
# from passlib.context import CryptContext

# from app.core.config import settings

# # Use bcrypt_sha256 to avoid bcrypt's 72-byte limit.
# # This pre-hashes the password with SHA-256 and then uses bcrypt,
# # preserving security while avoiding truncation/errors for long or unicode passwords.
# pwd_context = CryptContext(schemes=["bcrypt_sha256"], deprecated="auto")

# ALGORITHM = "HS256"


# def hash_password(password: str) -> str:
#     """
#     Hash the plain-text password and return the hash.
#     Uses bcrypt_sha256 internally so you can accept long/unicode passwords safely.
#     """
#     if password is None:
#         password = ""
#     # passlib handles encoding; ensure we pass str
#     return pwd_context.hash(str(password))


# def verify_password(plain_password: str, password_hash: str) -> bool:
#     return pwd_context.verify(str(plain_password), password_hash)


# def create_access_token(user_id: int) -> str:
#     expire = datetime.utcnow() + timedelta(
#         minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
#     )
#     to_encode = {
#         "sub": str(user_id),
#         "type": "access",
#         "exp": expire,
#     }
#     return jwt.encode(to_encode, settings.JWT_ACCESS_SECRET, algorithm=ALGORITHM)


# def create_refresh_token(user_id: int, version: int) -> str:
#     expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
#     to_encode = {
#         "sub": str(user_id),
#         "type": "refresh",
#         "v": version,
#         "exp": expire,
#     }
#     return jwt.encode(to_encode, settings.JWT_REFRESH_SECRET, algorithm=ALGORITHM)


# def decode_access_token(token: str) -> Optional[dict]:
#     try:
#         payload = jwt.decode(token, settings.JWT_ACCESS_SECRET, algorithms=[ALGORITHM])
#         if payload.get("type") != "access":
#             return None
#         return payload
#     except JWTError:
#         return None


# def decode_refresh_token(token: str) -> Optional[dict]:
#     try:
#         payload = jwt.decode(
#             token, settings.JWT_REFRESH_SECRET, algorithms=[ALGORITHM]
#         )
#         if payload.get("type") != "refresh":
#             return None
#         return payload
#     except JWTError:
#         return None


# def generate_email_verification_token() -> str:
#     return secrets.token_urlsafe(32)








# ===============================================================
# ---------- Anna code below ------------------------------------


# # app/core/security.py

# from datetime import datetime, timedelta
# from typing import Optional
# import secrets

# from jose import jwt, JWTError
# from passlib.context import CryptContext

# from app.core.config import settings

# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ALGORITHM = "HS256"


# def hash_password(password: str) -> str:
#     return pwd_context.hash(password)


# def verify_password(plain_password: str, password_hash: str) -> bool:
#     return pwd_context.verify(plain_password, password_hash)


# def create_access_token(user_id: int) -> str:
#     expire = datetime.utcnow() + timedelta(
#         minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
#     )
#     to_encode = {
#         "sub": str(user_id),
#         "type": "access",
#         "exp": expire,
#     }
#     return jwt.encode(to_encode, settings.JWT_ACCESS_SECRET, algorithm=ALGORITHM)


# def create_refresh_token(user_id: int, version: int) -> str:
#     expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
#     to_encode = {
#         "sub": str(user_id),
#         "type": "refresh",
#         "v": version,
#         "exp": expire,
#     }
#     return jwt.encode(to_encode, settings.JWT_REFRESH_SECRET, algorithm=ALGORITHM)


# def decode_access_token(token: str) -> Optional[dict]:
#     try:
#         payload = jwt.decode(token, settings.JWT_ACCESS_SECRET, algorithms=[ALGORITHM])
#         if payload.get("type") != "access":
#             return None
#         return payload
#     except JWTError:
#         return None


# def decode_refresh_token(token: str) -> Optional[dict]:
#     try:
#         payload = jwt.decode(
#             token, settings.JWT_REFRESH_SECRET, algorithms=[ALGORITHM]
#         )
#         if payload.get("type") != "refresh":
#             return None
#         return payload
#     except JWTError:
#         return None


# def generate_email_verification_token() -> str:
#     return secrets.token_urlsafe(32)
