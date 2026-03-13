# backend/app/models/task.py

from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from datetime import datetime
from app.models.user import Base

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    summary_id = Column(Integer, ForeignKey("summaries.id"), nullable=False, index=True)
    description = Column(Text, nullable=False)
    assignee_name = Column(String, nullable=True)
    assignee_email = Column(String, nullable=True)
    deadline = Column(String, nullable=True)
    status = Column(String, default="pending")  # pending / emailed / completed
    created_at = Column(DateTime, default=datetime.utcnow)
