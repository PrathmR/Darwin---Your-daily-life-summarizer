# app/schemas/user.py

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserLogin(UserBase):
    password: str


class UserPublic(UserBase):
    id: int
    is_email_verified: bool
    provider: str

    class Config:
        from_attributes = True  # pydantic v2 (replaces orm_mode = True)


class GoogleLoginRequest(BaseModel):
    credential: str  # Google ID token from frontend
