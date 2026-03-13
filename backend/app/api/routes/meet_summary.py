from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import asyncio
import base64
import json
import re

from app.services.meet_summary import process_uploaded_file
from app.api import deps
from app.models.summary import Summary
from app.models.task import Task
from app.models.user import User
from app.models.team_member import TeamMember
from app.email import send_task_assignment_email
from app.services import jira_service

router = APIRouter(prefix="/meet-summary", tags=["Meet Summary"])

class TextSummaryRequest(BaseModel):
    text: str
    calendar_context: Optional[str] = None
    client_id: Optional[str] = None
    custom_api_key: Optional[str] = None
    model_preference: Optional[str] = None
    meeting_role: Optional[str] = None
    summary_format: str = "default"

@router.post("")
async def summarize(
    file: UploadFile = File(...),
    calendar_context: Optional[str] = Form(None),
    client_id: Optional[str] = Form(None),
    custom_api_key: Optional[str] = Form(None),
    model_preference: Optional[str] = Form(None),
    meeting_role: Optional[str] = Form(None),
    summary_format: Optional[str] = Form("default"),
    screenshot_0: Optional[UploadFile] = File(None),
    screenshot_1: Optional[UploadFile] = File(None),
    screenshot_times: Optional[str] = Form(None),
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")

    # Parse screenshot times
    times = []
    if screenshot_times:
        try:
            times = json.loads(screenshot_times)
        except Exception:
            pass

    # Process screenshots: convert to base64 data URIs and pair with timestamps
    screenshot_data = []
    for idx, screenshot in enumerate([screenshot_0, screenshot_1]):
        if screenshot and screenshot.filename:
            raw = await screenshot.read()
            b64 = base64.b64encode(raw).decode('utf-8')
            time_str = times[idx] if idx < len(times) else None
            screenshot_data.append({
                "data": f"data:image/jpeg;base64,{b64}",
                "timestamp": time_str
            })

    # Call the ML service
    result = await process_uploaded_file(file, calendar_context, client_id, custom_api_key, model_preference, meeting_role, summary_format or "default")

    meeting_topic = result.get("facts", {}).get("meeting_topic")
    filename_to_save = meeting_topic if meeting_topic else file.filename

    # Save to database
    db_summary = Summary(
        user_id=current_user.id,
        filename=filename_to_save,
        transcript=result["transcript"],
        summary_text=result["summary"],
        facts=result.get("facts", {}),
        speaker_summaries=result.get("speaker_summaries", []),
        screenshots=screenshot_data if screenshot_data else None
    )
    db.add(db_summary)
    db.commit()
    db.refresh(db_summary)

    # Process Tasks & Send Emails — with team member matching
    action_items = result.get("facts", {}).get("action_items", [])
    team_members = db.query(TeamMember).filter(TeamMember.user_id == current_user.id).all()
    
    if isinstance(action_items, list):
        for item in action_items:
            if not isinstance(item, dict):
                continue
            
            desc = item.get("task", "Unknown task")
            assignee = item.get("assignee", "")
            deadline = item.get("deadline", "")
            
            # 1. Check if email is directly in the text
            emails = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', str(assignee) + " " + str(desc))
            assignee_email = emails[0] if emails else None
            
            # 2. If no email found, try matching the name to a team member
            if not assignee_email and assignee and team_members:
                assignee_lower = assignee.lower().strip()
                for member in team_members:
                    if member.name.lower() in assignee_lower or assignee_lower in member.name.lower():
                        assignee_email = member.email
                        break
            
            status = "emailed" if assignee_email else "pending"
            
            db_task = Task(
                summary_id=db_summary.id,
                description=desc,
                assignee_name=assignee,
                assignee_email=assignee_email,
                deadline=deadline,
                status=status
            )
            db.add(db_task)
            
            if assignee_email:
                send_task_assignment_email(
                    to_email=assignee_email,
                    assignee_name=assignee,
                    task_desc=desc,
                    topic=filename_to_save
                )
                
                # Also create Jira issue if configured
                try:
                    if jira_service.is_jira_configured():
                        matched_member = next((m for m in team_members if m.email == assignee_email), None)
                        jira_account_id = matched_member.jira_account_id if matched_member else None
                        jira_service.create_issue(
                            summary=f"[Darwin] {desc}",
                            description=f"Auto-assigned from meeting: {filename_to_save}\nAssignee: {assignee}\nDeadline: {deadline or 'None'}",
                            assignee_account_id=jira_account_id
                        )
                except Exception as e:
                    print(f"⚠️ Jira issue creation failed: {e}")
                
        db.commit()

    return {"message": "Success ✅", "output": result, "summary_id": db_summary.id}

@router.get("")
def get_user_summaries(
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    summaries = db.query(Summary).filter(Summary.user_id == current_user.id).order_by(Summary.created_at.desc()).all()
    return [
        {
            "id": s.id,
            "filename": s.filename,
            "created_at": s.created_at,
            "summary_text": s.summary_text,
            "facts": s.facts,
            "speaker_summaries": s.speaker_summaries,
            "screenshots": s.screenshots,
        }
        for s in summaries
    ]

from app.services.summarizer_service import process_text
from app.api.ws_manager import manager

@router.post("/text")
async def summarize_text(
    request: TextSummaryRequest,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    if not request.text:
        raise HTTPException(status_code=400, detail="No transcript text provided")

    loop = asyncio.get_event_loop()
    def notify_progress(msg: str):
        if request.client_id:
            asyncio.run_coroutine_threadsafe(manager.send_personal_message(msg, request.client_id), loop)

    # Call the ML service via the threadpool since it does blocking LLM calls
    result = await loop.run_in_executor(
        None, process_text, request.text, request.calendar_context, notify_progress,
        request.custom_api_key, request.model_preference, request.meeting_role, request.summary_format
    )

    meeting_topic = result.get("facts", {}).get("meeting_topic")
    filename_to_save = meeting_topic if meeting_topic else "Live Meeting Recording"

    # Save to database
    db_summary = Summary(
        user_id=current_user.id,
        filename=filename_to_save,
        transcript=result["transcript"],
        summary_text=result["summary"],
        facts=result.get("facts", {}),
        speaker_summaries=result.get("speaker_summaries", [])
    )
    db.add(db_summary)
    db.commit()
    db.refresh(db_summary)

    # Process Tasks & Send Emails — with team member matching
    action_items = result.get("facts", {}).get("action_items", [])
    team_members = db.query(TeamMember).filter(TeamMember.user_id == current_user.id).all()
    
    if isinstance(action_items, list):
        for item in action_items:
            if not isinstance(item, dict):
                continue
            
            desc = item.get("task", "Unknown task")
            assignee = item.get("assignee", "")
            deadline = item.get("deadline", "")
            
            emails = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', str(assignee) + " " + str(desc))
            assignee_email = emails[0] if emails else None
            
            if not assignee_email and assignee and team_members:
                assignee_lower = assignee.lower().strip()
                for member in team_members:
                    if member.name.lower() in assignee_lower or assignee_lower in member.name.lower():
                        assignee_email = member.email
                        break
            
            status = "emailed" if assignee_email else "pending"
            
            db_task = Task(
                summary_id=db_summary.id,
                description=desc,
                assignee_name=assignee,
                assignee_email=assignee_email,
                deadline=deadline,
                status=status
            )
            db.add(db_task)
            
            if assignee_email:
                send_task_assignment_email(
                    to_email=assignee_email,
                    assignee_name=assignee,
                    task_desc=desc,
                    topic=filename_to_save
                )
                
                try:
                    if jira_service.is_jira_configured():
                        matched_member = next((m for m in team_members if m.email == assignee_email), None)
                        jira_account_id = matched_member.jira_account_id if matched_member else None
                        jira_service.create_issue(
                            summary=f"[Darwin] {desc}",
                            description=f"Auto-assigned from live meeting: {filename_to_save}\nAssignee: {assignee}\nDeadline: {deadline or 'None'}",
                            assignee_account_id=jira_account_id
                        )
                except Exception as e:
                    print(f"⚠️ Jira issue creation failed: {e}")
    
    db.commit()

    return {
        "message": "Live meeting summarized successfully",
        "summary_id": db_summary.id
    }

# -----------------------------------------------------------




# # backend/app/api/routes/meet_summary.py
# from fastapi import APIRouter, UploadFile, File, HTTPException
# from app.services.meet_summary import process_uploaded_file

# router = APIRouter(prefix="/meet-summary", tags=["Meet Summary"])

# @router.post("")
# async def summarize_meeting(file: UploadFile = File(...)):
#     if not file.filename:
#         raise HTTPException(status_code=400, detail="No file uploaded")

#     result = await process_uploaded_file(file)
#     return {
#         "message": "Success ✅",
#         "output": result
#     }





# backend/app/api/routes/meet_summary.py:
# from fastapi import APIRouter, Depends, HTTPException
# from pydantic import BaseModel, Field
# from typing import List, Optional

# from app.services.meet_summary import analyze_research


# router = APIRouter(prefix="/meet-summary", tags=["Meet Summary"])


# class ResearchRequest(BaseModel):
#     query: str = Field(..., min_length=3, description="Research query")


# class Paper(BaseModel):
#     title: str
#     authors: Optional[List[str]] = None
#     year: Optional[int] = None
#     venue: Optional[str] = None
#     citation_count: Optional[int] = 0
#     abstract: Optional[str] = None
#     url: Optional[str] = None
#     source: Optional[str] = None
#     bibtex: Optional[str] = None
#     citations: Optional[List[str]] = []


# class ResearchResponse(BaseModel):
#     summary: str
#     final_summary: str
#     papers: List[Paper]


# @router.post("/", response_model=ResearchResponse)
# def meet_summary(payload: ResearchRequest):
#     """
#     Main Meet Summary API
#     """
#     try:
#         return analyze_research(payload.query)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
