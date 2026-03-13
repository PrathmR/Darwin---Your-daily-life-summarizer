# backend/app/schemas/team.py

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class TeamMemberCreate(BaseModel):
    name: str
    email: EmailStr
    role_in_team: Optional[str] = None


class TeamMemberResponse(BaseModel):
    id: int
    name: str
    email: str
    role_in_team: Optional[str] = None
    jira_account_id: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class MeetingRoleUpdate(BaseModel):
    meeting_role: str  # project_manager, software_pm, researcher, psychiatrist, standup_conductor, general
