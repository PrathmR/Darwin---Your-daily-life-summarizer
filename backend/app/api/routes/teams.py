# backend/app/api/routes/teams.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.api import deps
from app.models.user import User
from app.models.team_member import TeamMember
from app.schemas.team import TeamMemberCreate, TeamMemberResponse, MeetingRoleUpdate
from app.services.jira_service import search_user_by_email, is_jira_configured

router = APIRouter(prefix="/teams", tags=["Teams"])

VALID_ROLES = [
    "project_manager",
    "software_pm",
    "researcher",
    "psychiatrist",
    "standup_conductor",
    "general",
]

PM_ROLES = ["project_manager", "software_pm"]


@router.put("/role")
def update_meeting_role(
    payload: MeetingRoleUpdate,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    if payload.meeting_role not in VALID_ROLES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Must be one of: {', '.join(VALID_ROLES)}",
        )

    current_user.meeting_role = payload.meeting_role
    db.add(current_user)
    db.commit()
    db.refresh(current_user)

    return {"message": "Role updated", "meeting_role": current_user.meeting_role}


@router.get("/members", response_model=List[TeamMemberResponse])
def get_team_members(
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    members = (
        db.query(TeamMember)
        .filter(TeamMember.user_id == current_user.id)
        .order_by(TeamMember.created_at.desc())
        .all()
    )
    return members


@router.post("/members", response_model=TeamMemberResponse, status_code=status.HTTP_201_CREATED)
def add_team_member(
    payload: TeamMemberCreate,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    # Check for duplicate email within this user's team
    existing = (
        db.query(TeamMember)
        .filter(
            TeamMember.user_id == current_user.id,
            TeamMember.email == payload.email.lower(),
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A team member with this email already exists.",
        )

    # Lookup Jira account ID (non-blocking — returns None if Jira not configured)
    jira_account_id = search_user_by_email(payload.email)

    member = TeamMember(
        user_id=current_user.id,
        name=payload.name.strip(),
        email=payload.email.lower().strip(),
        role_in_team=payload.role_in_team,
        jira_account_id=jira_account_id,
    )
    db.add(member)
    db.commit()
    db.refresh(member)

    return member


@router.delete("/members/{member_id}")
def delete_team_member(
    member_id: int,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    member = (
        db.query(TeamMember)
        .filter(TeamMember.id == member_id, TeamMember.user_id == current_user.id)
        .first()
    )
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team member not found.",
        )

    db.delete(member)
    db.commit()
    return {"message": "Team member removed."}


@router.get("/jira-status")
def jira_status():
    """Check if Jira integration is configured."""
    return {"configured": is_jira_configured()}
