# backend/app/models/team_member.py

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from datetime import datetime
from app.models.user import Base


class TeamMember(Base):
    __tablename__ = "team_members"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    role_in_team = Column(String, nullable=True)  # Developer, Designer, QA, etc.
    jira_account_id = Column(String, nullable=True)  # Cached from Jira user lookup
    created_at = Column(DateTime, default=datetime.utcnow)
