# backend/app/models/summary.py

from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, JSON
from datetime import datetime
from app.models.user import Base

class Summary(Base):
    __tablename__ = "summaries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    filename = Column(String, nullable=False)
    transcript = Column(Text, nullable=False)
    summary_text = Column(Text, nullable=False)
    facts = Column(JSON, nullable=True)
    speaker_summaries = Column(JSON, nullable=True)
    screenshots = Column(JSON, nullable=True)  # list of base64-encoded JPEG strings
    created_at = Column(DateTime, default=datetime.utcnow)
