# app/models/user.py

from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=True)  # null for Google-only users

    provider = Column(String, nullable=False, default="local")  # local / google
    google_id = Column(String, nullable=True)

    is_email_verified = Column(Boolean, default=False)

    email_verification_token = Column(String, nullable=True)
    email_verification_token_expires_at = Column(DateTime, nullable=True)

    refresh_token_version = Column(Integer, default=0, nullable=False)
    meeting_role = Column(String, default="general", nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
