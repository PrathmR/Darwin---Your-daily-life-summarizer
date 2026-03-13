from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import asyncio

from app.services.meet_summary import process_uploaded_file
from app.api import deps
from app.models.summary import Summary
from app.models.task import Task
from app.models.user import User
from app.email import send_task_assignment_email

router = APIRouter(prefix="/meet-summary", tags=["Meet Summary"])

class TextSummaryRequest(BaseModel):
    text: str
    calendar_context: Optional[str] = None
    client_id: Optional[str] = None

@router.post("")
async def summarize(
    file: UploadFile = File(...),
    calendar_context: Optional[str] = Form(None),
    client_id: Optional[str] = Form(None),
    custom_api_key: Optional[str] = Form(None),
    model_preference: Optional[str] = Form(None),
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")

    # Call the ML service
    result = await process_uploaded_file(file, calendar_context, client_id, custom_api_key, model_preference)

    meeting_topic = result.get("facts", {}).get("meeting_topic")
    filename_to_save = meeting_topic if meeting_topic else file.filename

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

    # Process Tasks & Send Emails
    action_items = result.get("facts", {}).get("action_items", [])
    if isinstance(action_items, list):
        for item in action_items:
            if not isinstance(item, dict):
                continue
            
            desc = item.get("task", "Unknown task")
            assignee = item.get("assignee", "")
            deadline = item.get("deadline", "")
            
            # Simple heuristic to extract email from the prompt if present
            # Prompt output often has format: assignee Name (email@domain)
            import re
            emails = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', str(assignee) + " " + str(desc))
            assignee_email = emails[0] if emails else None
            
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
        None, process_text, request.text, request.calendar_context, notify_progress
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

    # Process Tasks & Send Emails
    action_items = result.get("facts", {}).get("action_items", [])
    if isinstance(action_items, list):
        for item in action_items:
            if not isinstance(item, dict):
                continue
            
            desc = item.get("task", "Unknown task")
            assignee = item.get("assignee", "")
            deadline = item.get("deadline", "")
            
            import re
            emails = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', str(assignee) + " " + str(desc))
            assignee_email = emails[0] if emails else None
            
            db_task = Task(
                summary_id=db_summary.id,
                description=desc,
                assignee_name=assignee,
                assignee_email=assignee_email,
                deadline=deadline,
                status="pending"
            )
            db.add(db_task)
            
            if assignee_email:
                send_task_assignment_email(
                    to_email=assignee_email,
                    task_description=desc,
                    meeting_topic=meeting_topic or "Live Meeting",
                    meeting_link="http://localhost:5173/game-workspace"
                )
    
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
