# backend/app/api/routes/meet_summary.py
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List

from app.services.meet_summary import process_uploaded_file
from app.api import deps
from app.models.summary import Summary
from app.models.user import User

router = APIRouter(prefix="/meet-summary", tags=["Meet Summary"])

@router.post("")
async def summarize(
    file: UploadFile = File(...),
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")

    # Call the ML service
    result = await process_uploaded_file(file)

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
